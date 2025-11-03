# backend/app.py
"""
TON Staking Pool Backend + Static Frontend server
- Віддає статичний Next.js export з ../frontend/out
- Поправлений CSP для Next (script/style eval/inline дозволені)
- API з JWT/Stripe (як було)
"""
import os
import json
from datetime import datetime, timedelta
from pathlib import Path

from flask import Flask, request, jsonify, send_from_directory, send_file
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

# Абсолютний шлях до зібраного фронтенду (Next export)
# На локальній машині: /path/to/backend/../frontend/out
# На Render: /opt/render/project/src/backend/../frontend/out = /opt/render/project/src/frontend/out
BACKEND_DIR = Path(__file__).resolve().parent
FRONTEND_OUT = (BACKEND_DIR / "../frontend/out").resolve()

# Fallback якщо FRONTEND_OUT не існує
if not FRONTEND_OUT.exists():
    print(f"⚠️  FRONTEND_OUT не знайдено: {FRONTEND_OUT}")
    print(f"📁 BACKEND_DIR: {BACKEND_DIR}")
    print(f"📁 Досліджуємо батьківськукаталог...")
    # Спробуємо знайти frontend/out в інших місцях
    alternatives = [
        BACKEND_DIR.parent / "frontend" / "out",
        Path("/opt/render/project/src/frontend/out"),
        Path("/opt/render/project/src") / "frontend" / "out",
    ]
    for alt in alternatives:
        if alt.exists():
            print(f"✅ Знайдено альтернативний шлях: {alt}")
            FRONTEND_OUT = alt
            break
else:
    print(f"✅ FRONTEND_OUT знайдено: {FRONTEND_OUT}")

# --- App ---------------------------------------------------------------------
app = Flask(__name__, static_folder=str(FRONTEND_OUT), static_url_path="")
app.config['SECRET_KEY'] = SECRET_KEY

# DB config
if DATABASE_URL:
    db_uri = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    if "postgresql://" in db_uri and "sslmode" not in db_uri:
        separator = "&" if "?" in db_uri else "?"
        db_uri += f"{separator}sslmode=require"
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///ton_pool.db"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# CORS
CORS(app, supports_credentials=True)

# CSP, скориговане для Next export (дозволяємо inline/eval для стабільності)
csp = {
    "default-src": ["'self'"],
    "base-uri": ["'self'"],
    "object-src": ["'none'"],
    "img-src": ["'self'", "data:", "blob:"],
    "font-src": ["'self'", "data:"],
    "script-src": ["'self'", "'unsafe-inline'", "'unsafe-eval'"],
    "style-src": ["'self'", "'unsafe-inline'"],
    "connect-src": ["'self'", "https://api.stripe.com"],
    "frame-ancestors": ["'none'"],
}
Talisman(
    app,
    content_security_policy=csp,
    strict_transport_security=True,
    force_https=True,
    frame_options='DENY',
    referrer_policy='no-referrer',
    session_cookie_secure=True
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

# ----------------------------- API ROUTES -----------------------------------
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

@app.post("/api/auth/logout")
@jwt_required()
def logout():
    return jsonify({'message': 'logged out'}), 200

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

# Платний доступ
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

    if event["type"] == "invoice.payment_succeeded":
        invoice = event["data"]["object"]
        customer_id = invoice.get("customer")
        subscription_id = invoice.get("subscription")
        sub = Subscription.query.filter_by(stripe_customer_id=customer_id).first()
        if sub:
            sub.status = "active"
            sub.stripe_subscription_id = subscription_id or sub.stripe_subscription_id
            try:
                period = invoice["lines"]["data"][0]["period"]
                sub.current_period_start = datetime.utcfromtimestamp(period["start"])
                sub.current_period_end = datetime.utcfromtimestamp(period["end"])
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

# --- API routes (pool, stats, etc) -------------------------------------------
@app.get("/api/pool/stats")
def api_pool_stats():
    stats = PoolStats.query.order_by(PoolStats.id.desc()).first()
    if not stats:
        stats = PoolStats(
            total_staked=12345.678,
            total_staked_usd=123456.78,
            participants_count=42,
            apy=0.097,
            min_stake=0.5,
            status='active',
            testnet=False
        )
        db.session.add(stats)
        db.session.commit()
    return jsonify(stats.to_dict()), 200

@app.get("/api/user/<address>/balance")
def api_user_balance(address: str):
    return jsonify({
        "user_address": address,
        "wallet_balance": 50.0,
        "staked_amount": 10.0,
        "accumulated_rewards": 0.5,
        "jettons_balance": 100.0,
        "share_percentage": 0.1
    }), 200

@app.get("/api/admin/stats")
@admin_required
def admin_stats():
    return jsonify({
        "total_users": User.query.count(),
        "total_transactions": Transaction.query.count(),
        "total_staked": 123456.78,
        "active_subscriptions": Subscription.query.filter_by(status='active').count()
    }), 200

@app.get("/api/admin/users")
@admin_required
def admin_users():
    users = User.query.all()
    return jsonify([u.to_dict(include_email=True) for u in users]), 200

# Compatibility
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


# ----------------------- STATIC FRONTEND ROUTES (catch-all at end) -----------
# Healthcheck
@app.get("/health")
def health():
    return jsonify({"ok": True, "service": "TON Pool", "time": datetime.utcnow().isoformat()}), 200

# 1) Next.js static assets
@app.route("/_next/<path:filename>")
def next_static(filename):
    folder = FRONTEND_OUT / "_next"
    try:
        return send_from_directory(str(folder), filename, conditional=True)
    except Exception as e:
        print(f"❌ Error serving /_next/{filename}: {e}")
        return jsonify({"error": "not found"}), 404

# 2) Static files in root
@app.route("/favicon.ico")
def favicon():
    try:
        return send_from_directory(str(FRONTEND_OUT), "favicon.ico", conditional=True)
    except:
        return "", 404

@app.route("/tonconnect-manifest.json")
def ton_manifest():
    try:
        return send_from_directory(str(FRONTEND_OUT), "tonconnect-manifest.json", conditional=True)
    except:
        return jsonify({"error": "not found"}), 404

# 3) Pages - explicit routes BEFORE catch-all
@app.route("/dashboard")
def dashboard_page():
    try:
        index_path = FRONTEND_OUT / "dashboard" / "index.html"
        if index_path.exists():
            print(f"✅ Serving /dashboard from {index_path}")
            return send_from_directory(str(index_path.parent), "index.html")
        print(f"❌ Not found: {index_path}")
        return jsonify({"error": "not found"}), 404
    except Exception as e:
        print(f"❌ Error serving /dashboard: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/login")
def login_page_html():
    try:
        index_path = FRONTEND_OUT / "login" / "index.html"
        if index_path.exists():
            return send_from_directory(str(index_path.parent), "index.html")
        return jsonify({"error": "not found"}), 404
    except Exception as e:
        print(f"❌ Error serving /login: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/register")
def register_page_html():
    try:
        index_path = FRONTEND_OUT / "register" / "index.html"
        if index_path.exists():
            return send_from_directory(str(index_path.parent), "index.html")
        return jsonify({"error": "not found"}), 404
    except Exception as e:
        print(f"❌ Error serving /register: {e}")
        return jsonify({"error": str(e)}), 500

# 4) Root index
@app.route("/")
def index_html():
    try:
        index_path = FRONTEND_OUT / "index.html"
        if index_path.exists():
            return send_from_directory(str(index_path.parent), "index.html")
        return jsonify({"error": "Frontend not found"}), 404
    except Exception as e:
        print(f"❌ Error serving /: {e}")
        return jsonify({"error": str(e)}), 500



# --- Init DB ---
with app.app_context():
    try:
        with db.engine.connect() as conn:
            conn.execute(db.text("CREATE SCHEMA IF NOT EXISTS ton_pool"))
            conn.commit()
        db.create_all()
        print("✅ Database schema 'ton_pool' ready")
    except Exception as e:
        print(f"⚠️  Database setup: {e}")

# --- Main ----
if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    app.run(host="0.0.0.0", port=port, debug=(os.getenv("FLASK_ENV") != "production"))
