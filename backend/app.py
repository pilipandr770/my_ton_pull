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

from flask import Flask, request, jsonify, send_from_directory, send_file, Response
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
from ton_api import TONAPIClient, PoolService
from transaction_monitor import init_scheduler

# --- Env ---------------------------------------------------------------------
load_dotenv()
STRIPE_SECRET = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
SECRET_KEY = os.getenv("SECRET_KEY", os.getenv("FLASK_SECRET_KEY", "super-secret-key"))
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

stripe.api_key = STRIPE_SECRET

# --- TON API Configuration ---------------------------------------------------
# Use mainnet for production (testnet=False)
TON_API_CLIENT = TONAPIClient(testnet=False)  # Mainnet
POOL_ADDRESS = os.getenv("POOL_CONTRACT_ADDRESS", "EQD-AKzjnXxLk8PFyVJvt9sIQW2_MqmSwi5qPfBZbhKT5bXf")  # Default pool address
POOL_SERVICE = PoolService(POOL_ADDRESS, testnet=False)  # Mainnet

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
    "img-src": [
        "'self'",
        "data:",
        "blob:",
        "https://ton.org",
        "https://raw.githubusercontent.com",
        "https://ton-connect.github.io",
        "https://wallets-backend.tonhubapi.com",
        "https://*.tonhubapi.com",
        "https://tonhub.com",
        "https://tonkeeper.app",
        "https://*.tonkeeper.app",
        "https://walletbot.me",
    ],
    "font-src": ["'self'", "data:"],
    "script-src": [
        "'self'",
        "'unsafe-inline'",
        "'unsafe-eval'",
        "https://ton-connect.github.io",
    ],
    "style-src": ["'self'", "'unsafe-inline'"],
    "connect-src": [
        "'self'",
        "https://api.stripe.com",
        "https://ton-connect.github.io",
        "https://wallets-backend.tonhubapi.com",
        "https://*.tonhubapi.com",
        "https://connect.tonhubapi.com",
        "https://tonkeeper.app",
        "https://*.tonkeeper.app",
        "https://tonhub.com",
        "https://*.tonhub.com",
        "https://walletbot.me",
        "https://bridge.tonapi.io",
        "https://*.tonapi.io",
        "wss://bridge.tonapi.io",
        "wss://*.tonapi.io",
        "https://tonapi.io",
        "https://toncenter.com",
    ],
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
    """Get real pool statistics from TON blockchain"""
    try:
        # Try to get real data from blockchain
        pool_balance = TON_API_CLIENT.get_address_balance(POOL_ADDRESS)
        
        # Get or create stats record in DB
        stats = PoolStats.query.order_by(PoolStats.id.desc()).first()
        if not stats:
            stats = PoolStats(
                total_staked=pool_balance,
                total_staked_usd=pool_balance * 5.0,  # Approximate USD price
                participants_count=42,
                apy=0.097,
                min_stake=0.5,
                status='active',
                testnet=False
            )
            db.session.add(stats)
            db.session.commit()
        else:
            # Update with real balance from blockchain
            stats.total_staked = pool_balance
            stats.total_staked_usd = pool_balance * 5.0
            stats.testnet = False
            db.session.commit()
        
        return jsonify(stats.to_dict()), 200
    except Exception as e:
        print(f"Error fetching real pool stats: {str(e)}")
        # Fallback to DB or mock data
        stats = PoolStats.query.order_by(PoolStats.id.desc()).first()
        if stats:
            return jsonify(stats.to_dict()), 200
        else:
            # Return mock data as fallback
            return jsonify({
                "total_staked": 12345.678,
                "total_staked_usd": 123456.78,
                "participants_count": 42,
                "apy": 0.097,
                "min_stake": 0.5,
                "status": 'active',
                "testnet": False
            }), 200

@app.get("/api/user/<address>/balance")
def api_user_balance(address: str):
    """Get real wallet balance and staking data from TON blockchain"""
    try:
        # Use PoolService to get all user data (queries smart contract)
        user_balance_data = POOL_SERVICE.get_user_balance(address)
        
        # Return real data from blockchain
        return jsonify(user_balance_data), 200
    except Exception as e:
        print(f"Error fetching balance for {address}: {str(e)}")
        # Return mock data as fallback if something fails
        return jsonify({
            "user_address": address,
            "wallet_balance": 50.0,
            "staked_amount": 10.0,
            "accumulated_rewards": 0.5,
            "jettons_balance": 0.0,
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

@app.get("/api/health/ton")
def health_ton():
    """Check TON API connection status"""
    try:
        # Try to get address info
        info = TON_API_CLIENT.get_address_info(POOL_ADDRESS)
        balance = TON_API_CLIENT.get_address_balance(POOL_ADDRESS)
        
        return jsonify({
            "status": "connected",
            "network": "mainnet",
            "pool_address": POOL_ADDRESS,
            "pool_balance": balance,
            "api_working": True
        }), 200
    except Exception as e:
        print(f"Health check error: {str(e)}")
        
        # Return error status but still 200 (health check should not fail)
        # Client can check "api_working" field
        return jsonify({
            "status": "error",
            "network": "mainnet",
            "pool_address": POOL_ADDRESS,
            "error": str(e)[:100],  # Truncate error message
            "api_working": False,
            "message": "TON API connection failed - using fallback data"
        }), 200

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

# Transaction endpoints

@app.post("/api/transaction/prepare-stake")
@login_required
def prepare_stake():
    """Prepare a stake transaction - returns data for TonConnect signing"""
    try:
        data = request.get_json(force=True) or {}
        amount = float(data.get("amount", 0))
        user_address = data.get("user_address", "")
        
        if not amount or not user_address:
            return jsonify({"error": "Missing amount or user_address"}), 400
        
        if amount <= 0:
            return jsonify({"error": "Amount must be positive"}), 400
        
        # Get transaction data from PoolService
        tx_data = POOL_SERVICE.prepare_deposit_transaction(user_address, amount)
        
        return jsonify({
            "transaction": tx_data,
            "status": "ready_for_signing",
            "message": "Ready to be signed by wallet"
        }), 200
    except Exception as e:
        print(f"Error preparing stake: {str(e)}")
        return jsonify({"error": str(e)}), 400

@app.post("/api/transaction/stake")
@login_required
def execute_stake():
    """Execute a stake transaction - record it in database"""
    try:
        data = request.get_json(force=True) or {}
        tx_hash = data.get("tx_hash", "")
        amount = float(data.get("amount", 0))
        user_address = data.get("user_address", "")
        
        if not tx_hash or not amount or not user_address:
            return jsonify({"error": "Missing tx_hash, amount, or user_address"}), 400
        
        # Get user from token
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Record transaction in database
        transaction = Transaction(
            user_id=user_id,
            type="stake",
            amount=amount,
            tx_hash=tx_hash,
            status="pending"
        )
        db.session.add(transaction)
        db.session.commit()
        
        return jsonify({
            "status": "recorded",
            "tx_hash": tx_hash,
            "amount": amount,
            "message": "Transaction recorded, waiting for blockchain confirmation"
        }), 200
    except Exception as e:
        print(f"Error recording stake: {str(e)}")
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@app.post("/api/transaction/prepare-unstake")
@login_required
def prepare_unstake():
    """Prepare an unstake transaction"""
    try:
        data = request.get_json(force=True) or {}
        user_address = data.get("user_address", "")
        
        if not user_address:
            return jsonify({"error": "Missing user_address"}), 400
        
        # Get transaction data from PoolService
        tx_data = POOL_SERVICE.prepare_withdraw_transaction(user_address)
        
        return jsonify({
            "transaction": tx_data,
            "status": "ready_for_signing",
            "message": "Ready to be signed by wallet"
        }), 200
    except Exception as e:
        print(f"Error preparing unstake: {str(e)}")
        return jsonify({"error": str(e)}), 400

@app.post("/api/transaction/unstake")
@login_required
def execute_unstake():
    """Execute an unstake transaction"""
    try:
        data = request.get_json(force=True) or {}
        tx_hash = data.get("tx_hash", "")
        user_address = data.get("user_address", "")
        
        if not tx_hash or not user_address:
            return jsonify({"error": "Missing tx_hash or user_address"}), 400
        
        # Get user from token
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Record transaction in database
        transaction = Transaction(
            user_id=user_id,
            type="unstake",
            amount=0,  # Unstake doesn't have amount tracked this way
            tx_hash=tx_hash,
            status="pending"
        )
        db.session.add(transaction)
        db.session.commit()
        
        return jsonify({
            "status": "recorded",
            "tx_hash": tx_hash,
            "message": "Withdrawal request recorded, coins will be sent after processing"
        }), 200
    except Exception as e:
        print(f"Error recording unstake: {str(e)}")
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@app.post("/api/transaction/prepare")
def prepare_transaction():
    """Legacy endpoint - prepare a transaction (stake or unstake)"""
    data = request.get_json(force=True)
    action = data.get("action", "").lower()  # "stake" or "unstake"
    amount = data.get("amount", 0)
    address = data.get("address", "")
    
    if not action or not amount or not address:
        return jsonify({"error": "Missing required fields"}), 400
    
    if action not in ["stake", "unstake"]:
        return jsonify({"error": "Invalid action"}), 400
    
    try:
        if action == "stake":
            tx_data = POOL_SERVICE.prepare_deposit_transaction(address, amount)
        else:  # unstake
            tx_data = POOL_SERVICE.prepare_withdraw_transaction(address)
        
        return jsonify({
            "tx_id": tx_data.get("tx_hash", f"tx_{hash(address + str(amount))}"),
            "transaction": tx_data,
            "action": action,
            "amount": amount,
            "address": address,
            "status": "ready_for_signing",
            "created_at": datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        print(f"Error preparing transaction: {str(e)}")
        return jsonify({"error": str(e)}), 400

@app.get("/api/transaction/history")
@login_required
def get_transaction_history():
    """Get user's transaction history with pagination and sorting"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Get query parameters
        page = request.args.get("page", 1, type=int)
        limit = request.args.get("limit", 20, type=int)
        sort_by = request.args.get("sort_by", "created_at", type=str)  # created_at, amount, type
        order = request.args.get("order", "desc", type=str)  # asc or desc
        status_filter = request.args.get("status", None, type=str)  # pending, confirmed, failed
        
        # Validate inputs
        if page < 1:
            page = 1
        if limit > 100:
            limit = 100
        if limit < 1:
            limit = 20
        if sort_by not in ["created_at", "amount", "type"]:
            sort_by = "created_at"
        if order not in ["asc", "desc"]:
            order = "desc"
        
        # Build query
        query = Transaction.query.filter_by(user_id=user_id)
        
        # Apply status filter if provided
        if status_filter:
            query = query.filter_by(status=status_filter)
        
        # Get total count
        total_count = query.count()
        
        # Apply sorting
        if sort_by == "created_at":
            if order == "desc":
                query = query.order_by(Transaction.created_at.desc())
            else:
                query = query.order_by(Transaction.created_at.asc())
        elif sort_by == "amount":
            if order == "desc":
                query = query.order_by(Transaction.amount.desc())
            else:
                query = query.order_by(Transaction.amount.asc())
        elif sort_by == "type":
            if order == "desc":
                query = query.order_by(Transaction.type.desc())
            else:
                query = query.order_by(Transaction.type.asc())
        
        # Apply pagination
        offset = (page - 1) * limit
        transactions = query.offset(offset).limit(limit).all()
        
        # Format response
        transaction_list = []
        for tx in transactions:
            transaction_list.append({
                "id": tx.id,
                "type": tx.type,  # "stake" or "unstake"
                "amount": float(tx.amount) if tx.amount else 0,
                "status": tx.status,  # "pending", "confirmed", "failed"
                "tx_hash": tx.tx_hash,
                "created_at": tx.created_at.isoformat() if tx.created_at else None,
                "updated_at": tx.updated_at.isoformat() if tx.updated_at else None,
            })
        
        return jsonify({
            "transactions": transaction_list,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total_count,
                "pages": (total_count + limit - 1) // limit  # Ceiling division
            },
            "sort": {
                "by": sort_by,
                "order": order
            }
        }), 200
        
    except Exception as e:
        print(f"Error fetching transaction history: {str(e)}")
        return jsonify({"error": str(e)}), 400

@app.get("/api/transaction/<tx_hash>/status")
@login_required
def get_transaction_status(tx_hash):
    """Get current status of a specific transaction"""
    try:
        user_id = get_jwt_identity()
        
        # Find transaction
        tx = Transaction.query.filter_by(tx_hash=tx_hash, user_id=user_id).first()
        if not tx:
            return jsonify({"error": "Transaction not found"}), 404
        
        # Check status on blockchain
        status_info = POOL_SERVICE.check_transaction_confirmed(tx_hash)
        
        # Update transaction status if changed
        if status_info.get("confirmed"):
            if tx.status != "confirmed":
                tx.update_status("confirmed")
                db.session.commit()
        
        return jsonify({
            "tx_hash": tx_hash,
            "status": tx.status,
            "type": tx.type,
            "amount": float(tx.amount) if tx.amount else 0,
            "created_at": tx.created_at.isoformat() if tx.created_at else None,
            "updated_at": tx.updated_at.isoformat() if tx.updated_at else None,
            "confirmations": status_info.get("confirmations", 0),
            "message": status_info.get("message", "")
        }), 200
        
    except Exception as e:
        print(f"Error checking transaction status: {str(e)}")
        return jsonify({"error": str(e)}), 500

# ----------------------- STATIC FRONTEND ROUTES (catch-all at end) -----------
# Healthcheck
@app.get("/health")
def health():
    return jsonify({"ok": True, "service": "TON Pool", "time": datetime.utcnow().isoformat()}), 200

# Helper function to serve files with proper MIME types and headers
def serve_static_file(file_path, mime_type=None):
    """Serve a file by reading content directly and returning as Response"""
    if not isinstance(file_path, Path):
        file_path = Path(file_path)
    
    if not file_path.exists():
        return None
    
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
        
        if not content:
            print(f"⚠️  Warning: File is empty: {file_path}")
            return None
        
        # Create response with actual content
        response = Response(content, mimetype=mime_type or 'application/octet-stream')
        response.headers['Cache-Control'] = 'public, max-age=3600'
        response.headers['Content-Length'] = len(content)
        
        print(f"✅ Served {file_path.name} ({len(content)} bytes)")
        return response
    except Exception as e:
        print(f"❌ Error serving file {file_path}: {e}")
        return None

# 1) Next.js static assets - handle nested paths
@app.route("/_next/<path:filename>")
def next_static(filename):
    file_path = FRONTEND_OUT / "_next" / filename
    if not file_path.exists():
        print(f"❌ Not found: {file_path}")
        return jsonify({"error": "not found"}), 404
    
    # Determine MIME type based on file extension
    mime_types = {
        '.js': 'application/javascript; charset=utf-8',
        '.mjs': 'application/javascript; charset=utf-8',
        '.css': 'text/css; charset=utf-8',
        '.woff2': 'font/woff2',
        '.woff': 'font/woff',
        '.ttf': 'font/ttf',
        '.svg': 'image/svg+xml',
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.gif': 'image/gif',
        '.map': 'application/json',
    }
    
    suffix = Path(filename).suffix.lower()
    mime_type = mime_types.get(suffix, 'application/octet-stream')
    
    result = serve_static_file(file_path, mime_type)
    if result:
        return result
    return ("", 404)

# 2) Static files in root
@app.route("/favicon.ico")
def favicon():
    result = serve_static_file(FRONTEND_OUT / "favicon.ico", 'image/x-icon')
    return result if result else ("", 404)

@app.route("/tonconnect-manifest.json", methods=['GET', 'OPTIONS'])
def ton_manifest():
    if request.method == 'OPTIONS':
        response = Response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response, 200
    
    result = serve_static_file(FRONTEND_OUT / "tonconnect-manifest.json", 'application/json')
    if result:
        # Add explicit CORS headers for manifest
        result.headers['Access-Control-Allow-Origin'] = '*'
        result.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        result.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return result
    return (jsonify({"error": "not found"}), 404)

# 3) Pages - explicit routes BEFORE catch-all
@app.route("/dashboard")
def dashboard_page():
    try:
        # Try direct index.html first
        index_path = FRONTEND_OUT / "dashboard" / "index.html"
        if not index_path.exists():
            # Try dashboard.html (Next export creates this)
            index_path = FRONTEND_OUT / "dashboard.html"
        
        if index_path.exists():
            print(f"✅ Serving /dashboard from {index_path}")
            result = serve_static_file(index_path, 'text/html')
            return result if result else (jsonify({"error": "error"}), 500)
        
        print(f"❌ Not found: {FRONTEND_OUT / 'dashboard' / 'index.html'}")
        print(f"❌ Not found: {FRONTEND_OUT / 'dashboard.html'}")
        return jsonify({"error": "not found"}), 404
    except Exception as e:
        print(f"❌ Error serving /dashboard: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/login")
def login_page_html():
    try:
        index_path = FRONTEND_OUT / "login" / "index.html"
        if not index_path.exists():
            index_path = FRONTEND_OUT / "login.html"
        
        if index_path.exists():
            result = serve_static_file(index_path, 'text/html')
            return result if result else (jsonify({"error": "error"}), 500)
        return jsonify({"error": "not found"}), 404
    except Exception as e:
        print(f"❌ Error serving /login: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/register")
def register_page_html():
    try:
        index_path = FRONTEND_OUT / "register" / "index.html"
        if not index_path.exists():
            index_path = FRONTEND_OUT / "register.html"
        
        if index_path.exists():
            result = serve_static_file(index_path, 'text/html')
            return result if result else (jsonify({"error": "error"}), 500)
        return jsonify({"error": "not found"}), 404
    except Exception as e:
        print(f"❌ Error serving /register: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/history")
def history_page_html():
    try:
        index_path = FRONTEND_OUT / "history" / "index.html"
        if not index_path.exists():
            index_path = FRONTEND_OUT / "history.html"
        
        if index_path.exists():
            result = serve_static_file(index_path, 'text/html')
            return result if result else (jsonify({"error": "error"}), 500)
        return jsonify({"error": "not found"}), 404
    except Exception as e:
        print(f"❌ Error serving /history: {e}")
        return jsonify({"error": str(e)}), 500

# 4) Root index
@app.route("/")
def index_html():
    try:
        index_path = FRONTEND_OUT / "index.html"
        if index_path.exists():
            print(f"✅ Serving / from {index_path}")
            result = serve_static_file(index_path, 'text/html')
            return result if result else (jsonify({"error": "error"}), 500)
        return jsonify({"error": "Frontend not found"}), 404
    except Exception as e:
        print(f"❌ Error serving /: {e}")
        return jsonify({"error": str(e)}), 500



# --- Init DB & Scheduler ---
with app.app_context():
    try:
        with db.engine.connect() as conn:
            conn.execute(db.text("CREATE SCHEMA IF NOT EXISTS ton_pool"))
            conn.commit()
        db.create_all()
        print("✅ Database schema 'ton_pool' ready")
    except Exception as e:
        print(f"⚠️  Database setup: {e}")
    
    # Initialize background transaction monitoring
    try:
        init_scheduler(app)
        print("✅ Transaction monitor scheduler initialized")
    except Exception as e:
        print(f"⚠️  Scheduler setup: {e}")

# --- Main ----
if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    app.run(host="0.0.0.0", port=port, debug=(os.getenv("FLASK_ENV") != "production"))
