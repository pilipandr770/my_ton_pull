# What's Next: Phase 3 Planning

## 🎯 Phase 3: Stake & Unstake Transactions

После успешной реализации smart contract queries, следующий шаг - **реальные транзакции на блокчейне**.

## 📋 Implementation Plan

### 1. Stake Transaction Flow

**Frontend:**
```
User Dashboard
    ↓ Enters amount to stake
Stake Form
    ↓ Clicks "Stake" button
TonConnect Wallet
    ↓ Shows transaction details
    ↓ User signs with private key (local)
Signed Transaction
    ↓ Sent to backend
Backend API /api/transaction/stake
    ↓ Verifies signature
    ↓ Records in database
    ↓ Returns transaction hash
Frontend
    ↓ Shows "Pending..." with hash
Blockchain
    ↓ ~5 seconds
    ↓ Transaction confirmed
Frontend
    ↓ Shows success + new balance
```

### 2. Unstake Transaction Flow

Similar to stake, but:
- Pool marks tokens for withdrawal
- After withdrawal period (usually next round)
- Coins returned to user wallet

### 3. API Endpoints to Implement

#### A. Prepare Stake Transaction
```
POST /api/transaction/prepare-stake

Request:
{
  "amount": 100.0,        // TON
  "user_address": "UQCX..."
}

Response:
{
  "to": "EQD-AKzj...",    // Pool address
  "amount": "100000000000", // In nanotons
  "init_code": "...",     // Contract init if needed
  "data": "...",          // Payload with deposit message
  "valid_until": 1730000000
}
```

#### B. Execute Stake (Called by TonConnect)
```
POST /api/transaction/stake

Request:
{
  "tx_hash": "abc123...",
  "user_address": "UQCX...",
  "amount": 100.0
}

Response:
{
  "status": "pending",
  "tx_hash": "abc123...",
  "recorded_at": "2025-11-04T12:00:00Z"
}
```

#### C. Similar for Unstake
```
POST /api/transaction/prepare-unstake
POST /api/transaction/unstake
```

## 🛠️ Technical Implementation

### 1. Update PoolService (ton_api.py)

```python
def prepare_deposit_transaction(self, user_address: str, amount_ton: float) -> Dict:
    """
    Prepare deposit transaction structure
    """
    # Build proper payload with deposit opcode
    # Return wallet -> pool contract call
    
def prepare_withdraw_transaction(self, user_address: str, amount_ton: float) -> Dict:
    """
    Prepare withdraw transaction structure
    """
    # Build payload with withdraw opcode
```

### 2. Update Backend Routes (app.py)

```python
@app.post("/api/transaction/prepare-stake")
@login_required
def prepare_stake():
    amount = request.json.get("amount")
    user_address = get_jwt_identity()
    
    tx_data = POOL_SERVICE.prepare_deposit_transaction(user_address, amount)
    return jsonify(tx_data), 200

@app.post("/api/transaction/stake")
@login_required
def execute_stake():
    tx_hash = request.json.get("tx_hash")
    amount = request.json.get("amount")
    user_address = get_jwt_identity()
    
    # Record in database
    transaction = Transaction(
        user_id=...,
        type="stake",
        amount=amount,
        tx_hash=tx_hash,
        status="pending"
    )
    db.session.add(transaction)
    db.session.commit()
    
    return jsonify({
        "status": "pending",
        "tx_hash": tx_hash
    }), 200
```

### 3. Update Frontend (React)

```typescript
// components/StakeForm.tsx

async function handleStake(amount: number) {
  // 1. Prepare transaction
  const prepareRes = await fetch('/api/transaction/prepare-stake', {
    method: 'POST',
    body: JSON.stringify({ amount })
  });
  
  const txData = await prepareRes.json();
  
  // 2. Send via TonConnect
  const result = await sendTransaction(txData);
  
  // 3. Confirm on backend
  const confirmRes = await fetch('/api/transaction/stake', {
    method: 'POST',
    body: JSON.stringify({
      tx_hash: result.hash,
      amount
    })
  });
  
  // 4. Show success
}
```

## 📚 Understanding TON Transactions

### Message Format

TON uses Cell-based data structure:
```
Cell = Binary data + references to other cells
```

For contract interaction:
```
Message {
  to: Address,
  value: Amount in nanotons,
  init: Optional init code for new contracts,
  body: Message body (op_code + data)
}
```

### Opcodes for Pool Contract

Common opcodes (need to verify in actual contract):
- `0x4e73744b` (4981640523) - Deposit/Stake
- `0x47657424` (1196248292) - Withdraw/Unstake
- etc.

## 🧪 Testing Strategy

### 1. Local Testing
```python
# Test message building
def test_stake_message():
    message = pool.prepare_deposit_transaction(
        "UQCX...",
        100.0
    )
    assert message["to"] == POOL_ADDRESS
    assert message["amount"] == "100000000000"  # 100 TON in nanotons
```

### 2. Testnet Testing
- Deploy contracts to TON testnet
- Test stake/unstake with test TON
- Verify balances update

### 3. Production Testing
- Live mainnet with real TON
- Monitor transaction success rate
- Check gas fees

## 📊 Database Schema Update

```python
# models.py

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    type = db.Column(db.String(20))  # 'stake', 'unstake', 'claim'
    amount = db.Column(db.Float)
    tx_hash = db.Column(db.String(255))
    status = db.Column(db.String(20))  # 'pending', 'confirmed', 'failed'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
```

## 🎨 Frontend Updates

### Stake Form Component
- Input field for amount
- Max button
- Fee estimation
- Wallet balance display
- Loading state during transaction
- Success/Error messages

### Transaction History
- List of all user transactions
- Status badges (pending, confirmed, failed)
- Links to TONscan
- Filtering and sorting

## ✅ Phase 3 Checklist

- [ ] Find actual pool contract opcodes
- [ ] Implement prepare_deposit_transaction()
- [ ] Implement prepare_withdraw_transaction()
- [ ] Add prepare-stake API endpoint
- [ ] Add stake API endpoint
- [ ] Add prepare-unstake API endpoint
- [ ] Add unstake API endpoint
- [ ] Update StakeForm component
- [ ] Add transaction history page
- [ ] Add error handling for failed transactions
- [ ] Test on testnet
- [ ] Deploy to production
- [ ] Monitor success rates

## 🔍 Resources

1. **TON Contract Documentation:** https://ton.org/docs/#/func
2. **Message Format:** https://ton.org/docs/#/func/stdlib?id=send_raw_message
3. **Opcodes:** https://ton.org/docs/#/func/stdlib?id=opcodes
4. **TonWeb Library:** https://github.com/tonwhales/TonWeb (reference)

## 📞 Questions to Answer

1. What are the exact opcodes for deposit/withdraw in our pool?
2. What parameters do they require?
3. What's the withdrawal period? (e.g., next round?)
4. Are there any fees or commissions?
5. Can users claim rewards separately?

---

**Next Phase:** Start with Phase 3 implementation
**Date:** Nov 4, 2025
**Priority:** HIGH - This is the core staking functionality
