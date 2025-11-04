# Phase 3 Complete: Stake & Unstake Transactions Implementation

## ✅ WHAT WE ACCOMPLISHED

### 1. Smart Contract Integration ✅
- Studied official TON Pool contract (pool.fc)
- Identified correct opcodes:
  - **op=1**: Simple deposit for nominators
  - **op=2**: Withdrawal request processing
  - **op=3**: Emergency withdrawal
- Implemented proper payload formatting

### 2. Backend Implementation ✅
- **Updated prepare_deposit_transaction()**
  - Builds proper message with op=1 opcode
  - Returns transaction ready for TonConnect signing
  - Handles amount conversion (TON → nanotons)

- **Updated prepare_withdraw_transaction()**
  - Builds message with op=2 and limit parameter
  - Sets appropriate gas fee (0.05 TON)
  - Returns transaction structure for TonConnect

- **New API Endpoints:**
  ```
  POST /api/transaction/prepare-stake
  POST /api/transaction/stake
  POST /api/transaction/prepare-unstake
  POST /api/transaction/unstake
  ```

### 3. Frontend Integration ✅
- Updated StakeForm component to:
  - Call new prepare endpoints
  - Use TonConnect wallet for signing
  - Record transaction after signing
  - Display tx hash to user
  - Handle errors gracefully

### 4. Authentication & Security ✅
- All transaction endpoints require JWT token (@login_required)
- User verification before recording transactions
- Proper error handling
- Transaction logging

---

## 🎯 TRANSACTION FLOW

### Stake Transaction Flow

```
User
  ↓ Enter amount + click "Stake"
Frontend
  ↓ POST /api/transaction/prepare-stake
Backend (PoolService)
  ↓ prepare_deposit_transaction(address, amount)
  ↓ Returns: {to: pool_address, amount: nanotons, payload: op=1}
Frontend
  ↓ Build transaction for TonConnect
TonConnect Wallet
  ↓ Show transaction details
  ↓ User signs with private key (local)
Signed Transaction
  ↓ Send to frontend
Frontend
  ↓ POST /api/transaction/stake with tx_hash
Backend
  ↓ Record transaction in database
  ↓ status = "pending"
Database
  ↓ transaction_id, tx_hash, status, timestamp
Frontend
  ↓ Show success "Transaction sent: abc123..."
Blockchain (next ~5s)
  ↓ Confirms transaction
Smart Contract
  ↓ Processes deposit
  ↓ Updates user staked_amount
User
  ↓ New balance visible in dashboard
```

### Unstake Transaction Flow

```
User
  ↓ Click "Request Withdrawal"
Frontend
  ↓ POST /api/transaction/prepare-unstake
Backend
  ↓ prepare_withdraw_transaction(address)
  ↓ Returns: {to: pool_address, amount: 0.05TON, payload: op=2}
TonConnect
  ↓ Sign withdrawal request
Backend
  ↓ Record in database
  ↓ status = "pending"
Frontend
  ↓ Show "Withdrawal request sent"
Blockchain
  ↓ Processes withdraw request
Smart Contract
  ↓ Marks user for withdrawal
  ↓ Processes after next epoch (~36 hours)
  ↓ Sends TON back to user wallet
User
  ↓ Receives TON in wallet
```

---

## 📡 API ENDPOINTS

### Stake Endpoints

#### 1. Prepare Stake Transaction
```http
POST /api/transaction/prepare-stake
Authorization: Bearer {jwt_token}
Content-Type: application/json

{
  "user_address": "UQCX...",
  "amount": 100.5
}

Response (200 OK):
{
  "transaction": {
    "to": "EQD-AKzj...",
    "amount": "100500000000",
    "payload": "00000001",
    "from": "UQCX...",
    "type": "deposit",
    "description": "Stake 100.5 TON in pool"
  },
  "status": "ready_for_signing"
}
```

#### 2. Execute Stake Transaction
```http
POST /api/transaction/stake
Authorization: Bearer {jwt_token}
Content-Type: application/json

{
  "tx_hash": "abc123def456...",
  "amount": 100.5,
  "user_address": "UQCX..."
}

Response (200 OK):
{
  "status": "recorded",
  "tx_hash": "abc123def456...",
  "amount": 100.5,
  "message": "Transaction recorded, waiting for blockchain confirmation"
}
```

### Unstake Endpoints

#### 1. Prepare Unstake Transaction
```http
POST /api/transaction/prepare-unstake
Authorization: Bearer {jwt_token}
Content-Type: application/json

{
  "user_address": "UQCX..."
}

Response (200 OK):
{
  "transaction": {
    "to": "EQD-AKzj...",
    "amount": "50000000",
    "payload": "000000 02ff",
    "from": "UQCX...",
    "type": "withdraw",
    "description": "Request withdrawal from pool"
  },
  "status": "ready_for_signing"
}
```

#### 2. Execute Unstake Transaction
```http
POST /api/transaction/unstake
Authorization: Bearer {jwt_token}
Content-Type: application/json

{
  "tx_hash": "xyz789...",
  "user_address": "UQCX..."
}

Response (200 OK):
{
  "status": "recorded",
  "tx_hash": "xyz789...",
  "message": "Withdrawal request recorded, coins will be sent after processing"
}
```

---

## 💾 Database Schema

### Transaction Model

```python
class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    type = db.Column(db.String(20))           # 'stake', 'unstake', 'claim'
    amount = db.Column(db.Float)               # Amount in TON
    tx_hash = db.Column(db.String(255))        # Blockchain transaction hash
    status = db.Column(db.String(20))          # 'pending', 'confirmed', 'failed'
    created_at = db.Column(db.DateTime)        # Creation time
    updated_at = db.Column(db.DateTime)        # Last update time
```

### Sample Records

```
Stake Transaction:
  user_id: 42
  type: "stake"
  amount: 100.5
  tx_hash: "2af0...bc0f5"
  status: "pending"
  created_at: 2025-11-04T15:30:00Z

Unstake Transaction:
  user_id: 42
  type: "unstake"
  amount: 0.0
  tx_hash: "1234...5678"
  status: "pending"
  created_at: 2025-11-04T15:35:00Z
```

---

## 🔐 Contract Details

### Nominator Operations

**Deposit (op=1):**
```
Message: {
  to: pool_address,
  amount: stake_amount (nanotons),
  body: op=1 (just the opcode)
}
```

**Process Withdrawal (op=2):**
```
Message: {
  to: pool_address,
  amount: 0.05 TON (gas fee),
  body: op=2 + limit(255)
}
```

### Contract Data Structures

**Nominator Storage:**
```
{
  staked_amount: uint,
  pending_deposit_amount: uint
}
```

**Withdrawal Requests:**
Dictionary mapping nominator address → withdrawal pending flag

---

## 🧪 TESTING

### Local Testing

1. **Start backend:**
   ```bash
   cd backend
   python app.py
   ```

2. **Start frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Test flow:**
   - Go to http://localhost:3000/dashboard
   - Connect wallet with TonConnect
   - Fill in amount (1-100 TON)
   - Click "Stake"
   - Approve in wallet
   - Check dashboard for transaction

### Production Testing

1. Go to https://my-ton-pull.onrender.com
2. Register and login
3. Connect wallet
4. Test small amount (0.5 TON)
5. Monitor transaction on TONscan

### Monitoring Transactions

```bash
# Check transaction status
curl https://my-ton-pull.onrender.com/api/user/UQCX.../balance

# Should show updated staked_amount after confirmation
```

---

## 📊 PAYLOAD FORMATTING

### Hex Payload Examples

**Deposit (op=1):**
```
00000001 = op code for "accept coins"
```

**Withdraw (op=2 + limit=255):**
```
00000002 = op code for "process withdraw"
ff       = limit=255 (process all requests)
```

### Conversion in Code

```python
# Build payload bytes
payload_bytes = bytes([0x00, 0x00, 0x00, 0x01])  # op=1

# Convert to hex string for API
hex_string = payload_bytes.hex()  # "00000001"

# TonConnect expects hex string
transaction = {
    "to": address,
    "amount": amount_nanotons,
    "payload": hex_string
}
```

---

## ✅ PHASE 3 CHECKLIST

- [x] Find contract opcodes
- [x] Implement prepare_deposit_transaction()
- [x] Implement prepare_withdraw_transaction()
- [x] Create /api/transaction/prepare-stake endpoint
- [x] Create /api/transaction/stake endpoint
- [x] Create /api/transaction/prepare-unstake endpoint
- [x] Create /api/transaction/unstake endpoint
- [x] Update frontend StakeForm component
- [x] Integrate TonConnect wallet signing
- [x] Add error handling
- [x] Add authentication
- [x] Record transactions in database

---

## 🎯 NEXT STEPS (Phase 4)

1. **Monitor Transactions**
   - Poll blockchain for confirmation
   - Update database status
   - Show real-time updates in UI

2. **Admin Panel**
   - View all user transactions
   - Monitor pool statistics
   - Track rewards

3. **Email Notifications**
   - Stake confirmation email
   - Withdrawal processed email
   - Reward received email

4. **Enhanced Features**
   - Claim rewards separately
   - View transaction history
   - Export transaction CSV
   - Analytics dashboard

---

## 📝 Files Changed

- `backend/ton_api.py` - Smart contract transaction builders
- `backend/app.py` - New API endpoints
- `frontend/src/components/StakeForm.tsx` - TonConnect integration

---

## 🚀 DEPLOYMENT

Latest commit: 5c5a086
Status: Ready for production deployment
Tests: Pass locally ✅

```bash
# Push to production
git push origin master

# Render will auto-deploy within 1-2 minutes
# Check: https://my-ton-pull.onrender.com
```

---

**Phase 3 Status:** ✅ COMPLETE
**Date:** Nov 4, 2025
**Time Spent:** ~30 minutes
**Lines Added:** ~213

Your TON Staking Pool now has **REAL STAKE/UNSTAKE TRANSACTIONS**! 🎉
