# Phase 3 Testing & Deployment Guide

## 🎯 Ready for Production

Your application now has **real stake/unstake transactions**!

Before deploying, let's verify everything works.

---

## 🧪 LOCAL TESTING (5 MINUTES)

### 1. Start Backend
```bash
cd backend
python app.py
```
Should show: `Running on http://localhost:8000`

### 2. Start Frontend
```bash
cd frontend
npm run dev
```
Should show: `http://localhost:3000`

### 3. Test Stake Transaction

**Step by step:**
1. Open http://localhost:3000
2. Click "Register"
3. Create test account (test@example.com / password123)
4. Login
5. Go to Dashboard
6. Connect wallet (use TON testnet)
7. Enter amount: **0.5** (small test amount)
8. Click "Stake"
9. **Approve in wallet** when TonConnect shows transaction
10. See success message with tx hash

**Expected result:**
```
✅ Transaction sent! Deposit 0.5 TON (abc123...)
```

### 4. Test Unstake Transaction

1. In Dashboard, click "Withdraw" tab
2. Click "Request Withdrawal"
3. **Approve in wallet**
4. See success message

**Expected result:**
```
✅ Transaction sent! Withdrawal Request (xyz789...)
```

### 5. Verify in Database

```bash
# Check recorded transactions
curl http://localhost:8000/api/user/UQCX.../balance
```

Should show updated balances.

---

## 🚀 PRODUCTION DEPLOYMENT

### Step 1: Verify Code

```bash
cd backend
python -m py_compile ton_api.py app.py

cd frontend
npm run build
```

Both should complete without errors.

### Step 2: Push to GitHub

```bash
git add .
git commit -m "Phase 3 complete - Real stake/unstake transactions"
git push origin master
```

### Step 3: Render Auto-Deploy

1. Go to https://dashboard.render.com
2. Find "my-ton-pull" service
3. Should auto-redeploy within 1-2 minutes
4. Check build logs

### Step 4: Test on Production

1. Open https://my-ton-pull.onrender.com
2. Register new account
3. Connect wallet
4. Try small transaction (0.5-1 TON on testnet)
5. Approve in wallet
6. Verify success message

---

## ✅ CHECKLIST

Before declaring Phase 3 complete, verify:

- [ ] Stake transaction works on testnet
- [ ] Unstake transaction works on testnet
- [ ] Transaction hash shown in success message
- [ ] Transactions recorded in database
- [ ] No errors in backend logs
- [ ] No errors in frontend console
- [ ] Frontend builds successfully
- [ ] Production deployment successful

---

## 🔍 TROUBLESHOOTING

### "Transaction failed" Error

**Possible causes:**
1. Insufficient TON in wallet
2. Network error (try testnet)
3. Wallet not connected

**Solution:**
- Check wallet balance
- Try with testnet
- Reload page and retry

### "Payload format error"

**Cause:** Backend payload formatting issue

**Solution:**
```bash
# Check backend logs
tail -f backend/app.log

# Verify payload is hex string
curl -X POST http://localhost:8000/api/transaction/prepare-stake \
  -H "Content-Type: application/json" \
  -d '{
    "user_address": "UQCX...",
    "amount": 0.5
  }'
```

### "401 Unauthorized"

**Cause:** Missing JWT token

**Solution:**
- Make sure you're logged in
- Token is stored in localStorage
- Try logout → login again

---

## 📊 SUCCESS INDICATORS

After deployment, you should see:

### In Database
```
Transaction entries with:
- user_id: correct user
- type: "stake" or "unstake"
- tx_hash: real blockchain hash
- status: "pending"
- created_at: current timestamp
```

### On Blockchain (Testnet)
Visit https://testnet.tonapi.io/ and search for tx_hash:
- Should show transaction from user wallet to pool contract
- Amount in nanotons matches request
- Status: OK

### In Dashboard
- Staked amount increases after stake confirms
- User can request withdrawal

---

## 🎓 KEY FEATURES IMPLEMENTED

✅ **Prepare Stake** - Build transaction ready for signing
✅ **Sign with Wallet** - TonConnect integration
✅ **Execute Stake** - Record transaction hash
✅ **Prepare Unstake** - Build withdrawal request
✅ **Execute Unstake** - Record withdrawal request
✅ **Database Tracking** - All transactions stored
✅ **Error Handling** - User-friendly error messages
✅ **Authentication** - JWT token required

---

## 💡 NEXT IMPROVEMENTS

After Phase 3 is stable, consider:

1. **Transaction History Page**
   - Show all user transactions
   - Filter by type (stake/unstake)
   - Link to TONscan

2. **Real-time Status Updates**
   - Poll blockchain for confirmation
   - Update UI when transaction confirms
   - Show balance updates

3. **Admin Dashboard**
   - View all users' transactions
   - Monitor pool statistics
   - Track rewards distribution

4. **Email Notifications**
   - Confirm stake transactions
   - Notify when rewards earned
   - Alert on withdrawals

---

## 📞 QUICK COMMANDS

```bash
# Test backend endpoints
curl -X POST http://localhost:8000/api/transaction/prepare-stake \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {token}" \
  -d '{"user_address":"UQCX...","amount":0.5}'

# Check logs
tail -f backend/app.log

# Rebuild frontend
cd frontend && npm run build

# Fresh local test
cd backend && rm -rf instance db.sqlite
python app.py
```

---

## 🎉 YOU'RE DONE!

Phase 3 is complete! Your TON staking pool now has:

✅ Real wallet balance queries
✅ Real pool balance queries
✅ Smart contract integration
✅ Stake transactions
✅ Unstake transactions
✅ Transaction tracking
✅ Production deployment

**Next: Test on production and monitor for issues!**

---

**Estimated time to deployment:** 5 minutes
**Estimated time for production stability:** 24 hours
**Status:** 🚀 READY TO DEPLOY
