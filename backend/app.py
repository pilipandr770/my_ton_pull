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
import stripe
from dotenv import load_dotenv

load_dotenv()
STRIPE_SECRET = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "change-me")

stripe.api_key = STRIPE_SECRET

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "super-secret-key")

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

# TODO: /api/pool та /api/position/:address — підключити TON indexer, поки віддаємо mock
@app.route("/api/pool")
def api_pool():
    return jsonify({
        "total_pool_ton": 12345.678,
        "total_jettons": 98765.432,
        "apy": 0.097
    })

@app.route("/api/position/<address>")
def api_position(address):
    return jsonify({
        "address": address,
        "ton": 10.0,
        "jettons": 100.0
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
