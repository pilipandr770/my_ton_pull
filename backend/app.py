# backend/app.py
# Path: backend/app.py
"""
Простий Flask бекенд:
- Admin login (local)
- Stripe webhook (підписка 5 €/міс)
- / (інфо), /login (адмін), /dashboard (захищено)
- Mock: on-chain дані (пізніше підключимо TON indexer)
"""
import os
import json
from flask import Flask, request, jsonify, session, redirect, url_for, render_template_string
from flask_cors import CORS
import stripe
from dotenv import load_dotenv

load_dotenv()
STRIPE_SECRET = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "change-me")

stripe.api_key = STRIPE_SECRET

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "super-secret-key")

# Enable CORS для frontend (localhost:3000)
CORS(app, origins=["http://localhost:3000"], supports_credentials=True)

STORAGE_FILE = os.path.join(os.path.dirname(__file__), "subscriptions.json")

def load_store():
    if not os.path.exists(STORAGE_FILE):
        return {"customers": {}}
    with open(STORAGE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_store(data):
    with open(STORAGE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

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
    store = load_store()
    active = sum(1 for c in store["customers"].values() if c.get("status") == "active")
    return render_template_string(DASH_HTML, active=active, store=json.dumps(store, indent=2, ensure_ascii=False))

@app.route("/stripe/webhook", methods=["POST"])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature", None)
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

    store = load_store()

    if event["type"] == "invoice.payment_succeeded":
        invoice = event["data"]["object"]
        customer_id = invoice.get("customer")
        subscription_id = invoice.get("subscription")
        if customer_id:
            store["customers"].setdefault(customer_id, {})
            store["customers"][customer_id].update({
                "subscription_id": subscription_id,
                "status": "active",
                "last_invoice": invoice.get("id"),
            })
            save_store(store)

    elif event["type"] == "customer.subscription.deleted":
        sub = event["data"]["object"]
        customer_id = sub.get("customer")
        if customer_id and customer_id in store["customers"]:
            store["customers"][customer_id]["status"] = "canceled"
            save_store(store)

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
