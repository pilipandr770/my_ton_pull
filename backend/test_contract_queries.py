#!/usr/bin/env python3
"""
Test script to verify smart contract queries
Запросити дані з пула контракту для тестування
"""

import sys
from ton_api import TONAPIClient, PoolService

# Configuration
POOL_ADDRESS = "EQD-AKzjnXxLk8PFyVJvt9sIQW2_MqmSwi5qPfBZbhKT5bXf"  # Mainnet pool
TEST_USER = "UQCX5LAULpXTcXEPJ_J6sTXhSYfJK_U6f4aVsL7OxUPmLHQh"  # Test wallet address

def test_pool_balance():
    """Test getting pool balance"""
    print("=" * 60)
    print("TEST 1: Pool Balance")
    print("=" * 60)
    
    try:
        client = TONAPIClient(testnet=False)  # Mainnet
        balance = client.get_address_balance(POOL_ADDRESS)
        print(f"✅ Pool balance: {balance} TON")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_wallet_balance():
    """Test getting wallet balance"""
    print("\n" + "=" * 60)
    print("TEST 2: Wallet Balance")
    print("=" * 60)
    
    try:
        client = TONAPIClient(testnet=False)  # Mainnet
        balance = client.get_address_balance(TEST_USER)
        print(f"✅ Wallet balance: {balance} TON")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_pool_service():
    """Test pool service methods"""
    print("\n" + "=" * 60)
    print("TEST 3: Pool Service - get_pool_stats()")
    print("=" * 60)
    
    try:
        pool = PoolService(POOL_ADDRESS, testnet=False)
        stats = pool.get_pool_stats()
        
        print(f"✅ Pool stats retrieved:")
        for key, value in stats.items():
            print(f"   {key}: {value}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_user_staked_amount():
    """Test getting user staked amount"""
    print("\n" + "=" * 60)
    print("TEST 4: User Staked Amount")
    print("=" * 60)
    
    try:
        pool = PoolService(POOL_ADDRESS, testnet=False)
        staked = pool.get_user_staked_amount(TEST_USER)
        print(f"✅ User staked amount: {staked} TON")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        print("   (This is OK - user might not have stake or method name might differ)")
        return False

def test_user_rewards():
    """Test getting user rewards"""
    print("\n" + "=" * 60)
    print("TEST 5: User Accumulated Rewards")
    print("=" * 60)
    
    try:
        pool = PoolService(POOL_ADDRESS, testnet=False)
        rewards = pool.get_user_rewards(TEST_USER)
        print(f"✅ User rewards: {rewards} TON")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        print("   (This is OK - user might not have rewards or method name might differ)")
        return False

def test_user_balance():
    """Test getting complete user balance"""
    print("\n" + "=" * 60)
    print("TEST 6: Complete User Balance (All Data)")
    print("=" * 60)
    
    try:
        pool = PoolService(POOL_ADDRESS, testnet=False)
        balance_data = pool.get_user_balance(TEST_USER)
        
        print(f"✅ User balance data retrieved:")
        for key, value in balance_data.items():
            print(f"   {key}: {value}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all tests"""
    print("\n")
    print("🧪 Smart Contract Query Tests")
    print("=" * 60)
    print(f"Pool Address: {POOL_ADDRESS}")
    print(f"Test User: {TEST_USER}")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("Pool Balance", test_pool_balance()))
    results.append(("Wallet Balance", test_wallet_balance()))
    results.append(("Pool Service Stats", test_pool_service()))
    results.append(("User Staked Amount", test_user_staked_amount()))
    results.append(("User Rewards", test_user_rewards()))
    results.append(("Complete User Balance", test_user_balance()))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "⚠️  WARN/FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nResult: {passed}/{total} tests passed/completed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n⚠️  Some tests failed or API methods might have different names")
        print("   This is expected if contract methods differ from standard names")
        return 1

if __name__ == "__main__":
    sys.exit(main())
