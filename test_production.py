#!/usr/bin/env python3
"""
Test production endpoints to verify they work
"""

import requests
import json

PROD_URL = "https://my-ton-pull.onrender.com"

def test_health():
    """Test health endpoint"""
    print("=" * 60)
    print("TEST 1: /api/health/ton")
    print("=" * 60)
    try:
        response = requests.get(f"{PROD_URL}/api/health/ton")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_pool_stats():
    """Test pool stats"""
    print("\n" + "=" * 60)
    print("TEST 2: /api/pool/stats")
    print("=" * 60)
    try:
        response = requests.get(f"{PROD_URL}/api/pool/stats")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_user_balance():
    """Test user balance"""
    print("\n" + "=" * 60)
    print("TEST 3: /api/user/<address>/balance")
    print("=" * 60)
    
    # Use a real address
    address = "UQCX5LAULpXTcXEPJ_J6sTXhSYfJK_U6f4aVsL7OxUPmLHQh"
    
    try:
        response = requests.get(f"{PROD_URL}/api/user/{address}/balance")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    print("\n🧪 Production API Tests\n")
    
    results = []
    results.append(("Health", test_health()))
    results.append(("Pool Stats", test_pool_stats()))
    results.append(("User Balance", test_user_balance()))
    
    print("\n" + "=" * 60)
    print("📊 Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {test_name}")
    
    print(f"\nPassed: {passed}/{total}")

if __name__ == "__main__":
    main()
