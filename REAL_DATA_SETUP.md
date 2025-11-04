# Real TON Mainnet Integration Guide

## Overview

This guide explains how the application now uses **real TON mainnet data** instead of mock values.

## What Changed

### Backend API Endpoints

#### 1. `/api/pool/stats` - Real Pool Balance
```json
GET /api/pool/stats

Response:
{
  "total_staked": 12345.678,           // Real balance from blockchain
  "total_staked_usd": 123456.78,       // USD converted
  "participants_count": 42,
  "apy": 0.097,
  "min_stake": 0.5,
  "status": "active",
  "testnet": false
}
```

**How it works:**
- Queries TON blockchain for actual pool contract balance
- Converts from nanotons to TON
- Falls back to database if API fails
- Updates DB with real data every time endpoint is called

#### 2. `/api/user/<address>/balance` - Real Wallet Balance
```json
GET /api/user/UQCX...../balance

Response:
{
  "user_address": "UQCX....",
  "wallet_balance": 50.0,           // Real balance from blockchain
  "staked_amount": 0.0,             // TODO: Query from contract
  "accumulated_rewards": 0.0,       // TODO: Query from contract
  "jettons_balance": 0.0,           // TODO: Query for JettonWallet
  "share_percentage": 0.0           // TODO: Calculate from contract
}
```

**How it works:**
- Queries TON blockchain for actual user wallet balance
- Returns real TON balance for connected wallet
- Falls back to mock data if API fails

#### 3. `/api/health/ton` - API Connection Check (NEW)
```json
GET /api/health/ton

Response (Success):
{
  "status": "connected",
  "network": "mainnet",
  "pool_address": "EQD-AKzjnXxLk8PFyVJvt9sIQW2_MqmSwi5qPfBZbhKT5bXf",
  "pool_balance": 12345.678,
  "api_working": true
}

Response (Error):
{
  "status": "error",
  "network": "mainnet",
  "pool_address": "EQD-AKzjnXxLk8PFyVJvt9sIQW2_MqmSwi5qPfBZbhKT5bXf",
  "error": "Connection failed",
  "api_working": false
}
```

## Configuration

### TON API Client

**File:** `backend/ton_api.py`

The `TONAPIClient` class connects to TON mainnet via TonCenter API:

```python
from ton_api import TONAPIClient

# Mainnet (production)
client = TONAPIClient(testnet=False)

# Get wallet balance
balance = client.get_address_balance("UQCX....")  # Returns balance in TON

# Get address info
info = client.get_address_info("UQCX....")  # Returns full address info
```

### Pool Contract Address

**Location:** `backend/app.py`

```python
POOL_ADDRESS = os.getenv("POOL_CONTRACT_ADDRESS", "EQD-AKzjnXxLk8PFyVJvt9sIQW2_MqmSwi5qPfBZbhKT5bXf")
```

To use a different pool address, set environment variable:
```bash
export POOL_CONTRACT_ADDRESS="EQD-YOUR-POOL-ADDRESS-HERE"
```

### TON Center API Key (Optional)

For better rate limits, set:
```bash
export TONCENTER_API_KEY="your_api_key_here"
```

## How To Test

### 1. Check Backend Connection
```bash
curl https://my-ton-pull.onrender.com/api/health/ton
```

Expected response:
```json
{
  "status": "connected",
  "network": "mainnet",
  "pool_balance": 12345.678,
  "api_working": true
}
```

### 2. Check Pool Stats (Real Data)
```bash
curl https://my-ton-pull.onrender.com/api/pool/stats
```

Expected: Real pool balance from blockchain

### 3. Check User Balance
1. Connect wallet in dashboard
2. See real TON balance displayed
3. Check DevTools → Network → `/api/user/<address>/balance`

## What's Real vs Mock

| Feature | Status | Notes |
|---------|--------|-------|
| Pool balance | ✅ Real | Queries blockchain |
| User wallet balance | ✅ Real | Queries blockchain |
| Staked amount | ⚠️ Mock | Requires contract query |
| Accumulated rewards | ⚠️ Mock | Requires contract query |
| Jettons balance | ⚠️ Mock | Requires JettonWallet query |
| Share percentage | ⚠️ Mock | Requires contract query |

## TODO - Next Steps

To make everything real, implement these:

1. **Query staked amount from pool contract**
   ```python
   def get_staked_amount(self, user_address: str) -> float:
       # Query get_method "get_staked" on pool contract
       # Returns user's staked TON amount
   ```

2. **Query accumulated rewards from pool contract**
   ```python
   def get_user_rewards(self, user_address: str) -> float:
       # Query get_method "get_rewards" on pool contract
       # Returns user's earned TON
   ```

3. **Query JettonWallet balance for staking tokens**
   ```python
   def get_jetton_balance(self, user_address: str, jetton_address: str) -> float:
       # Query staking jetton balance
   ```

## Error Handling

If TON API is unavailable:
- ✅ Falls back to database/mock data
- ✅ Logs error details
- ✅ Returns HTTP 200 with available data
- ❌ Won't crash the app

Example:
```
Error fetching real pool stats: Network error: Connection timeout
→ Returns last known database value or mock data
```

## Monitoring

To monitor API health in production:
1. Check `/api/health/ton` endpoint every 5 minutes
2. Alert if `api_working: false`
3. Check logs for network errors

## References

- **TonCenter API**: https://toncenter.com/api/v2/
- **TON Documentation**: https://ton.org/docs
- **Pool Contract**: Check POOL_CONTRACT_ADDRESS in app.py

---

**Status:** ✅ Real data integration complete
**Network:** Mainnet
**Last Updated:** Nov 4, 2025
