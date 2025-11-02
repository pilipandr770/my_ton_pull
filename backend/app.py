# backend/app.py
# Path: backend/app.py
"""
TON Staking Pool Backend
- PostgreSQL database with separate schema 'ton_pool'
- Stripe webhook (підписка 5 €/міс)
- TON blockchain integration
- Automatic migrations on deployment
"""
import os
import json
from flask import Flask, request, jsonify, session, redirect, url_for, render_template_string
from flask_cors import CORS
from flask_migrate import Migrate
import stripe
from dotenv import load_dotenv
from models import db, User, Transaction, PoolStats, Subscription

load_dotenv()
STRIPE_SECRET = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "change-me")

stripe.api_key = STRIPE_SECRET

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", os.getenv("FLASK_SECRET_KEY", "super-secret-key"))

# Database configuration
database_url = os.getenv("DATABASE_URL")
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///local.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
}

# Initialize database and migrations
db.init_app(app)
migrate = Migrate(app, db)

# Enable CORS
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
CORS(app, origins=[frontend_url, "http://localhost:3000"], supports_credentials=True)

# Create database schema on startup
with app.app_context():
    try:
        with db.engine.connect() as conn:
            conn.execute(db.text("CREATE SCHEMA IF NOT EXISTS ton_pool"))
            conn.commit()
        db.create_all()
        print("✅ Database schema 'ton_pool' ready")
    except Exception as e:
        print(f"⚠️  Database setup: {e}")

INDEX_HTML = """
<h2>TON Pool — Демо</h2>
<p>Поточний APY (mock): 9.7%</p>
<a href="/login">Admin login</a>
"""

LOGIN_HTML = """
<h2>Admin login</h2>
<form method="post">
  <input type="password" name="password" placeholder="Password"/>
  <button type="submit">Login</button>
</form>
"""

DASH_HTML = """
<h2>Admin dashboard</h2>
<p>Активні підписки: {{active}}</p>
<pre>{{store}}</pre>
<a href="/">Back</a>
"""

@app.route("/")
def index():
    return render_template_string(INDEX_HTML)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        pwd = request.form.get("password", "")
        if pwd == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect(url_for("dashboard"))
        return "Невірний пароль", 403
    return render_template_string(LOGIN_HTML)

@app.route("/dashboard")
def dashboard():
    if not session.get("admin"):
        return redirect(url_for("login"))
    
    # Get stats from database
    total_users = User.query.count()
    active_subs = Subscription.query.filter_by(status='active').count()
    recent_txs = Transaction.query.order_by(Transaction.created_at.desc()).limit(10).all()
    
    stats = {
        "total_users": total_users,
        "active_subscriptions": active_subs,
        "recent_transactions": len(recent_txs)
    }
    
    return render_template_string(DASH_HTML, active=active_subs, store=json.dumps(stats, indent=2, ensure_ascii=False))

@app.route("/stripe/webhook", methods=["POST"])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature", None)
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

    if event["type"] == "invoice.payment_succeeded":
        invoice = event["data"]["object"]
        customer_id = invoice.get("customer")
        subscription_id = invoice.get("subscription")
        
        if customer_id and subscription_id:
            # Find or create user (for now using stripe customer_id as identifier)
            user = User.query.filter_by(wallet_address=f"stripe_{customer_id}").first()
            if not user:
                user = User(wallet_address=f"stripe_{customer_id}")
                db.session.add(user)
                db.session.flush()
            
            # Create or update subscription
            sub = Subscription.query.filter_by(stripe_subscription_id=subscription_id).first()
            if not sub:
                sub = Subscription(
                    user_id=user.id,
                    stripe_subscription_id=subscription_id,
                    stripe_customer_id=customer_id,
                    status='active'
                )
                db.session.add(sub)
            else:
                sub.status = 'active'
            
            db.session.commit()

    elif event["type"] == "customer.subscription.deleted":
        sub_data = event["data"]["object"]
        subscription_id = sub_data.get("id")
        
        if subscription_id:
            sub = Subscription.query.filter_by(stripe_subscription_id=subscription_id).first()
            if sub:
                sub.status = 'canceled'
                db.session.commit()

    return jsonify({"status": "success"}), 200

# ============================================================================
# TON POOL API ENDPOINTS
# ============================================================================

from ton_api import get_pool_service

@app.route("/api/pool/stats")
def api_pool_stats():
    """Статистика пулу (total staked, APY, учасники)"""
    try:
        pool_service = get_pool_service()
        stats = pool_service.get_pool_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/user/<address>/balance")
def api_user_balance(address):
    """Баланс користувача (wallet + staked + rewards)"""
    try:
        pool_service = get_pool_service()
        balance = pool_service.get_user_balance(address)
        return jsonify(balance)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/user/<address>/transactions")
def api_user_transactions(address):
    """Історія транзакцій користувача"""
    try:
        limit = int(request.args.get("limit", 10))
        pool_service = get_pool_service()
        transactions = pool_service.get_user_transactions(address, limit)
        return jsonify({"transactions": transactions})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/transaction/prepare", methods=["POST"])
def api_prepare_transaction():
    """Підготовка транзакції для підпису в гаманці"""
    try:
        data = request.get_json()
        tx_type = data.get("type")  # "deposit" або "withdraw"
        user_address = data.get("address")
        amount = float(data.get("amount", 0))
        
        if not user_address or amount <= 0:
            return jsonify({"error": "Invalid parameters"}), 400
        
        pool_service = get_pool_service()
        
        if tx_type == "deposit":
            tx_data = pool_service.prepare_deposit_transaction(user_address, amount)
        elif tx_type == "withdraw":
            tx_data = pool_service.prepare_withdraw_transaction(user_address, amount)
        else:
            return jsonify({"error": "Invalid transaction type"}), 400
        
        return jsonify(tx_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Legacy endpoints (backward compatibility)
@app.route("/api/pool")
def api_pool():
    """Legacy endpoint - redirect to /api/pool/stats"""
    return api_pool_stats()

@app.route("/api/position/<address>")
def api_position(address):
    """Legacy endpoint - redirect to /api/user/:address/balance"""
    return api_user_balance(address)

@app.cli.command()
def init_db():
    """Initialize database with schema"""
    with db.engine.connect() as conn:
        conn.execute(db.text("CREATE SCHEMA IF NOT EXISTS ton_pool"))
        conn.commit()
    db.create_all()
    print("Database initialized!")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("FLASK_ENV") != "production"
    app.run(host="0.0.0.0", port=port, debug=debug)
