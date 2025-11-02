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
from flask_login import LoginManager, login_user, logout_user, current_user
from flask_jwt_extended import (
    JWTManager, create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, get_jwt
)
import stripe
from dotenv import load_dotenv
from datetime import datetime, timedelta
from models import db, User, Transaction, PoolStats, Subscription
from auth import login_required, admin_required, subscription_required

load_dotenv()
STRIPE_SECRET = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "change-me")

stripe.api_key = STRIPE_SECRET

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", os.getenv("FLASK_SECRET_KEY", "super-secret-key"))

# JWT Configuration
app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY", app.secret_key)
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)

# Initialize JWT
jwt = JWTManager(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

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

# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@app.route("/api/auth/register", methods=["POST"])
def register():
    """Register new user"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400
        
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already registered'}), 400
        
        # Create new user
        user = User(email=email, role='user')
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # Create JWT tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        return jsonify({
            'message': 'Registration successful',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict(include_email=True)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route("/api/auth/login", methods=["POST"])
def login():
    """Login user"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400
        
        # Find user
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Create JWT tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict(include_email=True)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route("/api/auth/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    user_id = get_jwt_identity()
    access_token = create_access_token(identity=user_id)
    return jsonify({'access_token': access_token}), 200


@app.route("/api/auth/me", methods=["GET"])
@jwt_required()
def get_current_user_info():
    """Get current user info"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({'user': user.to_dict(include_email=True)}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route("/api/auth/logout", methods=["POST"])
@jwt_required()
def logout():
    """Logout user (client should delete tokens)"""
    return jsonify({'message': 'Logout successful'}), 200


# ============================================================================
# ADMIN ENDPOINTS
# ============================================================================

@app.route("/api/admin/stats")
@admin_required
def api_admin_stats():
    """Admin statistics endpoint"""
    total_users = User.query.count()
    active_subs = Subscription.query.filter_by(status='active').count()
    total_staked = db.session.query(db.func.sum(Transaction.amount)).filter(
        Transaction.tx_type == 'deposit',
        Transaction.status == 'confirmed'
    ).scalar() or 0
    
    recent_txs = Transaction.query.order_by(Transaction.created_at.desc()).limit(10).all()
    
    return jsonify({
        "total_users": total_users,
        "active_subscriptions": active_subs,
        "total_staked": float(total_staked),
        "recent_transactions": [tx.to_dict() for tx in recent_txs]
    })


@app.route("/api/admin/users")
@admin_required
def api_admin_users():
    """Get all users (admin only)"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        users_query = User.query.order_by(User.created_at.desc())
        pagination = users_query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'users': [user.to_dict(include_email=True) for user in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route("/api/admin/users/<int:user_id>", methods=["GET", "PATCH", "DELETE"])
@admin_required
def api_admin_user_detail(user_id):
    """Get, update or delete user (admin only)"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if request.method == "GET":
            return jsonify({'user': user.to_dict(include_email=True)}), 200
        
        elif request.method == "PATCH":
            data = request.get_json()
            
            if 'role' in data and data['role'] in ['user', 'admin']:
                user.role = data['role']
            
            if 'subscription_status' in data:
                user.subscription_status = data['subscription_status']
            
            if 'subscription_expires_at' in data:
                from dateutil import parser
                user.subscription_expires_at = parser.parse(data['subscription_expires_at'])
            
            user.updated_at = datetime.utcnow()
            db.session.commit()
            
            return jsonify({
                'message': 'User updated',
                'user': user.to_dict(include_email=True)
            }), 200
        
        elif request.method == "DELETE":
            db.session.delete(user)
            db.session.commit()
            return jsonify({'message': 'User deleted'}), 200
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route("/api/admin/transactions")
@admin_required
def api_admin_transactions():
    """Get all transactions (admin only)"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        
        txs_query = Transaction.query.order_by(Transaction.created_at.desc())
        pagination = txs_query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'transactions': [tx.to_dict() for tx in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# SUBSCRIPTION ENDPOINTS
# ============================================================================

@app.route("/api/subscription/create-checkout", methods=["POST"])
@jwt_required()
def create_subscription_checkout():
    """Create Stripe checkout session for subscription"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Check if user already has active subscription
        if user.has_active_subscription():
            return jsonify({'error': 'You already have an active subscription'}), 400
        
        # Price ID from Stripe (5€/month)
        price_id = os.getenv('STRIPE_PRICE_ID', 'price_1234567890')
        
        # Create or get Stripe customer
        existing_sub = Subscription.query.filter_by(user_id=user.id).first()
        if existing_sub and existing_sub.stripe_customer_id:
            customer_id = existing_sub.stripe_customer_id
        else:
            customer = stripe.Customer.create(
                email=user.email,
                metadata={'user_id': user.id}
            )
            customer_id = customer.id
        
        # Create checkout session
        success_url = os.getenv('FRONTEND_URL', 'http://localhost:3000') + '/subscription/success?session_id={CHECKOUT_SESSION_ID}'
        cancel_url = os.getenv('FRONTEND_URL', 'http://localhost:3000') + '/pricing'
        
        checkout_session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=['card'],
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            mode='subscription',
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={'user_id': user.id}
        )
        
        return jsonify({
            'checkout_url': checkout_session.url,
            'session_id': checkout_session.id
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route("/api/subscription/portal", methods=["POST"])
@jwt_required()
def create_customer_portal():
    """Create Stripe customer portal session"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get customer ID from subscription
        sub = Subscription.query.filter_by(user_id=user.id).first()
        if not sub or not sub.stripe_customer_id:
            return jsonify({'error': 'No subscription found'}), 404
        
        # Create portal session
        return_url = os.getenv('FRONTEND_URL', 'http://localhost:3000') + '/dashboard'
        
        portal_session = stripe.billing_portal.Session.create(
            customer=sub.stripe_customer_id,
            return_url=return_url
        )
        
        return jsonify({
            'portal_url': portal_session.url
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route("/api/subscription/status", methods=["GET"])
@jwt_required()
def get_subscription_status():
    """Get user's subscription status"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        sub = Subscription.query.filter_by(user_id=user.id).order_by(Subscription.created_at.desc()).first()
        
        return jsonify({
            'has_subscription': sub is not None,
            'subscription': sub.to_dict() if sub else None,
            'user_status': {
                'subscription_status': user.subscription_status,
                'subscription_expires_at': user.subscription_expires_at.isoformat() if user.subscription_expires_at else None,
                'has_active_subscription': user.has_active_subscription()
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route("/stripe/webhook", methods=["POST"])
def stripe_webhook():
    """Handle Stripe webhook events"""
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature", None)
    
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

    try:
        # Handle subscription creation/update
        if event["type"] in ["customer.subscription.created", "customer.subscription.updated"]:
            sub_data = event["data"]["object"]
            subscription_id = sub_data.get("id")
            customer_id = sub_data.get("customer")
            price_id = sub_data["items"]["data"][0]["price"]["id"] if sub_data.get("items") else None
            status = sub_data.get("status")
            current_period_start = datetime.fromtimestamp(sub_data.get("current_period_start", 0))
            current_period_end = datetime.fromtimestamp(sub_data.get("current_period_end", 0))
            cancel_at_period_end = sub_data.get("cancel_at_period_end", False)
            
            if not subscription_id or not customer_id:
                return jsonify({"status": "error", "message": "Missing subscription or customer ID"}), 400
            
            # Find subscription record
            sub = Subscription.query.filter_by(stripe_subscription_id=subscription_id).first()
            
            if not sub:
                # Create new subscription (find user by customer_id)
                customer = stripe.Customer.retrieve(customer_id)
                user_id = customer.get("metadata", {}).get("user_id")
                
                if not user_id:
                    return jsonify({"status": "error", "message": "User ID not found in customer metadata"}), 400
                
                user = User.query.get(int(user_id))
                if not user:
                    return jsonify({"status": "error", "message": "User not found"}), 404
                
                sub = Subscription(
                    user_id=user.id,
                    stripe_subscription_id=subscription_id,
                    stripe_customer_id=customer_id,
                    stripe_price_id=price_id or ''
                )
                db.session.add(sub)
            
            # Update subscription
            sub.status = status
            sub.current_period_start = current_period_start
            sub.current_period_end = current_period_end
            sub.cancel_at_period_end = cancel_at_period_end
            sub.updated_at = datetime.utcnow()
            
            # Update user subscription status
            user = sub.user
            if status == 'active':
                user.subscription_status = 'active'
                user.subscription_expires_at = current_period_end
            elif status in ['past_due', 'unpaid']:
                user.subscription_status = 'past_due'
            elif status in ['canceled', 'incomplete_expired']:
                user.subscription_status = 'inactive'
                user.subscription_expires_at = current_period_end
            
            user.updated_at = datetime.utcnow()
            db.session.commit()

        # Handle successful payment
        elif event["type"] == "invoice.payment_succeeded":
            invoice = event["data"]["object"]
            subscription_id = invoice.get("subscription")
            
            if subscription_id:
                sub = Subscription.query.filter_by(stripe_subscription_id=subscription_id).first()
                if sub:
                    sub.status = 'active'
                    sub.user.subscription_status = 'active'
                    if sub.current_period_end:
                        sub.user.subscription_expires_at = sub.current_period_end
                    db.session.commit()

        # Handle subscription deletion
        elif event["type"] == "customer.subscription.deleted":
            sub_data = event["data"]["object"]
            subscription_id = sub_data.get("id")
            
            if subscription_id:
                sub = Subscription.query.filter_by(stripe_subscription_id=subscription_id).first()
                if sub:
                    sub.status = 'canceled'
                    sub.user.subscription_status = 'inactive'
                    sub.updated_at = datetime.utcnow()
                    db.session.commit()

        return jsonify({"status": "success"}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Webhook error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

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

# ============================================================================
# SERVE FRONTEND STATIC FILES (Next.js)
# ============================================================================

from flask import send_from_directory, send_file

# Path to frontend build - support both local and Render deployment
if os.path.exists("/opt/render/project/src/frontend/out"):
    # Render deployment path
    FRONTEND_BUILD_DIR = "/opt/render/project/src/frontend/out"
else:
    # Local development path
    FRONTEND_BUILD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "out")

print(f"🎨 Frontend build directory: {FRONTEND_BUILD_DIR}")
print(f"📂 Directory exists: {os.path.exists(FRONTEND_BUILD_DIR)}")

# Catch-all route for serving frontend (MUST BE LAST!)
# Flask processes more specific routes first, so /api/* routes above won't be affected
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    """Serve Next.js static files for all non-API routes"""
    
    # Double-check: API and Stripe routes should be handled above
    if path.startswith('api') or path.startswith('stripe'):
        return jsonify({"error": "API endpoint not found"}), 404
    
    # For root path, serve index.html
    if not path or path == '':
        index_path = os.path.join(FRONTEND_BUILD_DIR, "index.html")
        if os.path.exists(index_path):
            return send_file(index_path)
    
    # Try exact path first (for static assets like JS, CSS, images)
    exact_path = os.path.join(FRONTEND_BUILD_DIR, path)
    if os.path.exists(exact_path) and os.path.isfile(exact_path):
        return send_from_directory(FRONTEND_BUILD_DIR, path)
    
    # Try with .html extension (Next.js static export)
    html_path = os.path.join(FRONTEND_BUILD_DIR, f"{path}.html")
    if os.path.exists(html_path):
        return send_file(html_path)
    
    # Try directory index (path/index.html)
    dir_index = os.path.join(FRONTEND_BUILD_DIR, path, "index.html")
    if os.path.exists(dir_index):
        return send_file(dir_index)
    
    # Fallback to root index.html for client-side routing
    index_path = os.path.join(FRONTEND_BUILD_DIR, "index.html")
    if os.path.exists(index_path):
        return send_file(index_path)
    
    # Frontend not built yet
    return f"""
    <!DOCTYPE html>
    <html>
    <head><title>TON Pool - Build Required</title></head>
    <body style="font-family: Arial; padding: 40px; max-width: 800px; margin: 0 auto;">
        <h1>🏗️ Frontend Not Built</h1>
        <p>The Next.js frontend hasn't been compiled yet.</p>
        <h3>To build locally:</h3>
        <pre style="background: #f5f5f5; padding: 15px; border-radius: 5px;">
cd frontend
npm install
npm run build</pre>
        <p><strong>Looking for:</strong> <code>{FRONTEND_BUILD_DIR}</code></p>
        <hr>
        <p>✅ Backend API is running: <a href="/api/pool/stats">Check API</a></p>
    </body>
    </html>
    """, 200

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("FLASK_ENV") != "production"
    app.run(host="0.0.0.0", port=port, debug=debug)
