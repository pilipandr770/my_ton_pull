# backend/app.py
"""
TON Staking Pool Backend
- PostgreSQL/SQLite via SQLAlchemy
- Stripe webhook
- JWT + simple session auth
- Security headers (CSP, HSTS, X-Frame-Options, X-Content-Type-Options)
- Mock TON API
"""
import os
import json
from datetime import datetime, timedelta

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from flask_jwt_extended import (
    JWTManager, create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, get_jwt
)
from flask_talisman import Talisman
from dotenv import load_dotenv
import stripe

from models import db, User, Transaction, PoolStats, Subscription
from auth import login_required, admin_required, subscription_required

# --- Env ---------------------------------------------------------------------
load_dotenv()
STRIPE_SECRET = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
SECRET_KEY = os.getenv("SECRET_KEY", os.getenv("FLASK_SECRET_KEY", "super-secret-key"))
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

stripe.api_key = STRIPE_SECRET

# --- App ---------------------------------------------------------------------
app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY

# DB config: Render Postgres or local SQLite
if DATABASE_URL:
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL.replace("postgres://", "postgresql://", 1)
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///ton_pool.db"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Enable CORS
CORS(app, supports_credentials=True)

# Security headers
csp = {
    'default-src': ["'self'"],
    'script-src': ["'self'"],
    'connect-src': ["'self'", "https://api.stripe.com"],
    'img-src': ["'self'", "data:"],
    'style-src': ["'self'", "'unsafe-inline'"],
    'frame-ancestors': ["'none'"],
}
Talisman(
    app,
    content_security_policy=csp,
    strict_transport_security=True,
    force_https=(os.getenv("FLASK_ENV") == "production"),
    frame_options='DENY',
    referrer_policy='no-referrer',
    session_cookie_secure=(os.getenv("FLASK_ENV") == "production")
)

# --- Init DB & JWT -----------------------------------------------------------
db.init_app(app)
migrate = Migrate(app, db)

app.config['JWT_SECRET_KEY'] = SECRET_KEY
jwt = JWTManager(app)

@jwt.additional_claims_loader
def add_claims(identity):
    user = User.query.get(identity)
    return {
        'role': user.role if user else 'user',
        'subscription_status': user.subscription_status if user else 'inactive'
    }

# --- Health & root -----------------------------------------------------------
@app.get("/")
def root():
    return jsonify({"ok": True, "service": "TON Pool Backend", "time": datetime.utcnow().isoformat()}), 200

# --- Auth endpoints -----------------------------------------------------------
@app.post("/api/auth/register")
def register():
    data = request.get_json(force=True)
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    if not email or not password:
        return jsonify({'error': 'email/password required'}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'email exists'}), 409

    user = User(email=email, role='user', subscription_status='inactive')
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    access_token = create_access_token(identity=user.id, expires_delta=timedelta(hours=2))
    refresh_token = create_refresh_token(identity=user.id)
    return jsonify({
        'message': 'ok',
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': user.to_dict(include_email=True)
    }), 201

@app.post("/api/auth/login")
def login():
    data = request.get_json(force=True)
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({'error': 'invalid credentials'}), 401

    access_token = create_access_token(identity=user.id, expires_delta=timedelta(hours=2))
    refresh_token = create_refresh_token(identity=user.id)
    return jsonify({
        'message': 'ok',
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': user.to_dict(include_email=True)
    }), 200

@app.post("/api/auth/refresh")
@jwt_required(refresh=True)
def refresh():
    uid = get_jwt_identity()
    token = create_access_token(identity=uid, expires_delta=timedelta(hours=2))
    return jsonify({'access_token': token}), 200

@app.get("/api/auth/me")
@jwt_required()
def get_me():
    uid = get_jwt_identity()
    user = User.query.get(uid)
    if not user:
        return jsonify({'error': 'user not found'}), 404
    return jsonify({'user': user.to_dict(include_email=True)}), 200

# --- Protected demo ----------------------------------------------------------
@app.get("/api/secure/demo")
@subscription_required
def secure_demo():
    return jsonify({'ok': True, 'msg': 'You have active subscription'}), 200

# --- Stripe webhook -----------------------------------------------------------
@app.post("/stripe/webhook")
def stripe_webhook():
    payload = request.data
    sig = request.headers.get("Stripe-Signature", None)
    try:
        event = stripe.Webhook.construct_event(payload, sig, STRIPE_WEBHOOK_SECRET)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

    # Handle key events
    if event["type"] == "invoice.payment_succeeded":
        invoice = event["data"]["object"]
        customer_id = invoice.get("customer")
        subscription_id = invoice.get("subscription")
        sub = Subscription.query.filter_by(stripe_customer_id=customer_id).first()
        if sub:
            sub.status = "active"
            sub.stripe_subscription_id = subscription_id or sub.stripe_subscription_id
            try:
                sub.current_period_start = datetime.utcfromtimestamp(invoice["lines"]["data"][0]["period"]["start"])
                sub.current_period_end = datetime.utcfromtimestamp(invoice["lines"]["data"][0]["period"]["end"])
            except:
                pass
            db.session.commit()
            user = User.query.get(sub.user_id)
            if user:
                user.subscription_status = 'active'
                user.subscription_expires_at = sub.current_period_end
                db.session.commit()

    elif event["type"] == "customer.subscription.deleted":
        sub_obj = event["data"]["object"]
        customer_id = sub_obj.get("customer")
        sub = Subscription.query.filter_by(stripe_customer_id=customer_id).first()
        if sub:
            sub.status = "canceled"
            db.session.commit()
            user = User.query.get(sub.user_id)
            if user:
                user.subscription_status = 'inactive'
                user.subscription_expires_at = None
                db.session.commit()

    return jsonify({"status": "success"}), 200

# --- Mock TON API -------------------------------------------------------------
@app.get("/api/pool")
def api_pool():
    stats = PoolStats.query.order_by(PoolStats.id.desc()).first()
    if not stats:
        stats = PoolStats(total_pool_ton=12345.678, total_jettons=98765.432, apy=0.097)
        db.session.add(stats)
        db.session.commit()
    return jsonify(stats.to_dict()), 200

@app.get("/api/position/<address>")
def api_position(address: str):
    return jsonify({
        "address": address,
        "ton": 10.0,
        "jettons": 100.0
    }), 200

# --- CLI helper: create admin -------------------------------------------------
@app.post("/api/admin/bootstrap")
def bootstrap_admin():
    token = request.headers.get("X-Setup-Token")
    if token != os.getenv("SETUP_TOKEN", "setup-once"):
        return jsonify({"error": "forbidden"}), 403
    email = request.json.get("email")
    pwd = request.json.get("password")
    if not email or not pwd:
        return jsonify({"error": "email/password required"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "exists"}), 409
    u = User(email=email, role='admin', subscription_status='active', subscription_expires_at=datetime.utcnow()+timedelta(days=30))
    u.set_password(pwd)
    db.session.add(u)
    db.session.commit()
    return jsonify({"ok": True}), 200

# --- Main --------------------------------------------------------------------
with app.app_context():
    try:
        # Create schema if needed
        with db.engine.connect() as conn:
            conn.execute(db.text("CREATE SCHEMA IF NOT EXISTS ton_pool"))
            conn.commit()
        db.create_all()
        print("✅ Database schema 'ton_pool' ready")
    except Exception as e:
        print(f"⚠️  Database setup: {e}")

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    app.run(host="0.0.0.0", port=port, debug=(os.getenv("FLASK_ENV") != "production"))
