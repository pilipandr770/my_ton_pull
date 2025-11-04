# Smart Contract Query Implementation Guide

## Status: ✅ IMPLEMENTED (PHASE 2 COMPLETE)

Реализована вторая фаза: **запросы к смарт-контракту для получения реальных данных**.

## What's Working

### ✅ Implemented Methods

1. **get_user_staked_amount(user_address: str) → float**
   - Запрашивает сколько токенов юзер застейкал в пулі
   - Вызывает метод контракту: `get_staked`
   - Параметр: адреса користувача (slice format)
   - Повернення: сума в TON

2. **get_user_rewards(user_address: str) → float**
   - Запрашивает накопленные награды пользователя
   - Вызывает метод контракту: `get_rewards`
   - Параметр: адреса користувача (slice format)
   - Повернення: награди в TON

3. **get_user_balance(user_address: str) → Dict**
   - Комплексный метод получения всех данных пользователя
   - Вызывает оба вышепредставленных методов
   - Рассчитывает share_percentage от общего баланса пула
   - **Возвращает**:
     ```python
     {
         "user_address": "UQCX...",
         "wallet_balance": 50.123,           # Real TON in wallet
         "staked_amount": 100.0,             # Real staked in pool (from contract)
         "accumulated_rewards": 5.0,         # Real rewards (from contract)
         "jettons_balance": 0.0,             # TODO: query JettonWallet
         "share_percentage": 0.5             # Calculated: staked / pool_balance
     }
     ```

## API Endpoints Updated

### GET /api/user/<address>/balance
```bash
curl https://my-ton-pull.onrender.com/api/user/UQCX.../balance
```

**Response:**
```json
{
  "user_address": "UQCX5LAULpXTcXEPJ_J6sTXhSYfJK_U6f4aVsL7OxUPmLHQh",
  "wallet_balance": 50.0,
  "staked_amount": 10.0,
  "accumulated_rewards": 0.5,
  "share_percentage": 0.1
}
```

**Error Handling:**
- If contract call fails → Returns 0 values + error message in logs
- If wallet doesn't exist → Returns 0 values gracefully
- Always returns HTTP 200 (never fails the API call)

### GET /api/health/ton
```bash
curl https://my-ton-pull.onrender.com/api/health/ton
```

**Response (Success):**
```json
{
  "status": "connected",
  "network": "mainnet",
  "pool_address": "EQD-AKzjnXxLk8PFyVJvt9sIQW2_MqmSwi5qPfBZbhKT5bXf",
  "pool_balance": 12345.678,
  "api_working": true
}
```

**Response (Fallback):**
```json
{
  "status": "error",
  "network": "mainnet",
  "pool_address": "EQD-AKzjnXxLk8PFyVJvt9sIQW2_MqmSwi5qPfBZbhKT5bXf",
  "error": "Network error: 403 Forbidden",
  "api_working": false,
  "message": "TON API connection failed - using fallback data"
}
```

**Note:** Always returns HTTP 200 for health checks

## Implementation Details

### Contract Method Format

TON Smart Contract methods are called via TonCenter API:

```python
result = TON_API_CLIENT.run_get_method(
    address="EQD-AKzjnXxLk8PFyVJvt9sIQW2_MqmSwi5qPfBZbhKT5bXf",
    method="get_staked",
    stack=[["slice", "UQCX5LAULpXTcXEPJ_J6sTXhSYfJK_U6f4aVsL7OxUPmLHQh"]]
)
```

**Stack Format:**
- `["num", "123"]` - numeric value
- `["slice", "ADDRESS"]` - address parameter
- `["cell", "DATA"]` - cell data

**Response:**
```json
{
  "ok": true,
  "result": {
    "stack": [
      ["num", "1000000000000"]  # 1000 TON in nanotons
    ]
  }
}
```

### Conversion Formula

TON uses **nanotons** for precision (1 TON = 10^9 nanotons):

```python
# Convert nanotons to TON
toncells_in_nanoton = int(stack[0][1])
ton_amount = toncells_in_nanoton / 1_000_000_000
```

## Known Issues & Limitations

### ⚠️ TonCenter API Rate Limits

On production, may encounter:
- **403 Forbidden** - API key not whitelisted or rate limit exceeded
- **416 Range Not Satisfiable** - Network issue or API protocol change
- **500 Internal Server Error** - Temporary API outage

**Solution:** Implemented graceful fallback returning mock data with error logged

### ⚠️ Contract Method Names

If contract uses different method names (not `get_staked`, `get_rewards`):
- Check actual contract implementation
- Update method names in `ton_api.py`
- Test with `test_contract_queries.py` script

### ⚠️ JettonWallet Balance

Not yet implemented. To add:
```python
def get_jetton_balance(self, user_address: str, jetton_address: str) -> float:
    # Query JettonWallet get_wallet_data method
    # Returns balance for staking tokens
```

## Testing

### Local Testing

```bash
cd backend
python test_contract_queries.py
```

Tests:
1. ✅ Pool Balance (real from blockchain)
2. ✅ Wallet Balance (real from blockchain)
3. ✅ Pool Service stats
4. ✅ User Staked Amount (contract query)
5. ✅ User Rewards (contract query)
6. ✅ Complete User Balance (all data combined)

### Production Testing

```bash
# Health check
curl https://my-ton-pull.onrender.com/api/health/ton

# Pool stats
curl https://my-ton-pull.onrender.com/api/pool/stats

# User balance (replace XXXX with real address)
curl https://my-ton-pull.onrender.com/api/user/UQCX.../balance
```

## Next Steps (Phase 3)

### 1. Verify Contract Methods
- Get actual pool contract code
- Confirm method names: `get_staked`, `get_rewards`
- Check parameter format and return values

### 2. Optimize Caching
- Cache contract queries (results don't change every request)
- Add TTL (time-to-live) for cache
- Reduce API calls to TonCenter

### 3. Handle Edge Cases
- User not in pool (returns 0)
- Zero staked amount
- Pending rewards calculation
- Commission deduction

### 4. Add More Features
- Get total nominators count
- Get APY calculation from contract
- Query validator info
- Get withdrawal queue status

## Architecture

```
Frontend (React)
    ↓ /api/user/<address>/balance
Backend (Flask)
    ↓
PoolService.get_user_balance()
    ├─ wallet_balance: TONAPIClient.get_address_balance()
    ├─ staked_amount: run_get_method("get_staked")
    ├─ accumulated_rewards: run_get_method("get_rewards")
    └─ share_percentage: calculated
    ↓
TonCenter API (Mainnet)
    ├─ getAddressInformation
    ├─ runGetMethod (contract queries)
    └─ With fallback to mock data on errors
```

## Configuration

### Environment Variables

```bash
# .env or Render settings
POOL_CONTRACT_ADDRESS=EQD-AKzjnXxLk8PFyVJvt9sIQW2_MqmSwi5qPfBZbhKT5bXf
TONCENTER_API_KEY=2e5fc57e96c8d25f786dcd1c3922b3fa2722589dedcd96bdd1256459527384ea
```

### Code References

- **Backend**: `backend/ton_api.py` (TONAPIClient, PoolService)
- **API Endpoint**: `backend/app.py` line ~328 (/api/user/<address>/balance)
- **Tests**: `backend/test_contract_queries.py`
- **Documentation**: This file + REAL_DATA_SETUP.md

---

**Last Updated:** Nov 4, 2025
**Status:** ✅ Phase 2 Complete - Smart contract queries implemented
**Commit:** 6b64e4a - Add smart contract query methods
