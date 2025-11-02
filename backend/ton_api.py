# backend/ton_api.py
"""
TON Blockchain API Integration
Підключення до TON через TonCenter API для читання on-chain даних
"""

import os
import requests
from typing import Dict, Optional, List
from dotenv import load_dotenv

load_dotenv()

class TONAPIClient:
    """Клієнт для роботи з TON blockchain через TonCenter API"""
    
    def __init__(self, testnet: bool = True):
        """
        Ініціалізація клієнта
        
        Args:
            testnet: True для testnet, False для mainnet
        """
        self.testnet = testnet
        self.base_url = (
            "https://testnet.toncenter.com/api/v2"
            if testnet
            else "https://toncenter.com/api/v2"
        )
        self.api_key = os.getenv("TONCENTER_API_KEY", "")  # Опційно для більше rate limit
        
    def _make_request(self, method: str, params: Dict = None) -> Dict:
        """
        Виконати HTTP запит до TON API
        
        Args:
            method: Назва методу API
            params: Параметри запиту
            
        Returns:
            JSON відповідь від API
        """
        url = f"{self.base_url}/{method}"
        headers = {}
        if self.api_key:
            headers["X-API-Key"] = self.api_key
            
        try:
            response = requests.get(url, params=params or {}, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if not data.get("ok"):
                raise Exception(f"API error: {data.get('error', 'Unknown error')}")
                
            return data.get("result", {})
        except requests.exceptions.RequestException as e:
            raise Exception(f"Network error: {str(e)}")
    
    def get_address_info(self, address: str) -> Dict:
        """
        Отримати інформацію про адресу
        
        Args:
            address: TON адреса (user-friendly або raw)
            
        Returns:
            Dict з balance, state, last_transaction_id, etc.
        """
        return self._make_request("getAddressInformation", {"address": address})
    
    def get_address_balance(self, address: str) -> float:
        """
        Отримати баланс адреси в TON
        
        Args:
            address: TON адреса
            
        Returns:
            Баланс у TON (не в nanoton)
        """
        info = self.get_address_info(address)
        balance_nanoton = int(info.get("balance", 0))
        return balance_nanoton / 1_000_000_000  # Convert to TON
    
    def get_transactions(self, address: str, limit: int = 10) -> List[Dict]:
        """
        Отримати історію транзакцій адреси
        
        Args:
            address: TON адреса
            limit: Максимальна кількість транзакцій
            
        Returns:
            List транзакцій
        """
        return self._make_request("getTransactions", {
            "address": address,
            "limit": limit
        })
    
    def run_get_method(self, address: str, method: str, stack: List = None) -> Dict:
        """
        Виконати get-метод смарт-контракту
        
        Args:
            address: Адреса контракту
            method: Назва методу
            stack: Параметри для методу
            
        Returns:
            Результат виконання методу
        """
        params = {
            "address": address,
            "method": method
        }
        if stack:
            params["stack"] = stack
            
        return self._make_request("runGetMethod", params)


class PoolService:
    """Сервіс для роботи з TON Pool контрактом"""
    
    def __init__(self, pool_address: str, testnet: bool = True):
        """
        Ініціалізація Pool Service
        
        Args:
            pool_address: Адреса pool контракту
            testnet: Testnet чи mainnet
        """
        self.pool_address = pool_address
        self.api = TONAPIClient(testnet=testnet)
        
    def get_pool_stats(self) -> Dict:
        """
        Отримати статистику пулу
        
        Returns:
            Dict з total_staked, participants_count, apy, etc.
        """
        # TODO: Використовувати реальні get-методи контракту
        # Зараз mock дані для розробки
        
        try:
            # Баланс контракту
            balance = self.api.get_address_balance(self.pool_address)
            
            # TODO: Викликати get-методи контракту для отримання:
            # - кількість учасників (nominators_count)
            # - total staked amount
            # - validator rewards
            
            # Mock дані (замінити на реальні)
            return {
                "total_staked": balance,  # Реальний баланс контракту
                "total_staked_usd": balance * 2.5,  # Приблизна ціна TON
                "participants_count": 0,  # TODO: з контракту
                "apy": 9.7,  # TODO: розрахувати з validator rewards
                "pool_address": self.pool_address,
                "status": "active",
                "min_stake": 1,  # Змінено: 1 TON мінімум
                "max_participants": 100000,  # Практично необмежено
                "testnet": self.api.testnet
            }
        except Exception as e:
            return {
                "error": str(e),
                "total_staked": 0,
                "participants_count": 0,
                "apy": 0
            }
    
    def get_user_balance(self, user_address: str) -> Dict:
        """
        Отримати баланс користувача в пулі
        
        Args:
            user_address: Адреса користувача
            
        Returns:
            Dict з staked amount, rewards, jettons balance
        """
        try:
            # Баланс гаманця користувача
            wallet_balance = self.api.get_address_balance(user_address)
            
            # TODO: Отримати з контракту:
            # - staked amount (скільки користувач застейкав)
            # - jettons balance (pool share tokens)
            # - accumulated rewards
            
            # Mock дані (замінити на реальні з контракту)
            return {
                "user_address": user_address,
                "wallet_balance": wallet_balance,
                "staked_amount": 0,  # TODO: з контракту
                "jettons_balance": 0,  # TODO: з контракту
                "accumulated_rewards": 0,  # TODO: розрахувати
                "share_percentage": 0,  # TODO: розрахувати
            }
        except Exception as e:
            return {
                "error": str(e),
                "user_address": user_address,
                "wallet_balance": 0,
                "staked_amount": 0
            }
    
    def get_user_transactions(self, user_address: str, limit: int = 10) -> List[Dict]:
        """
        Отримати історію транзакцій користувача з пулом
        
        Args:
            user_address: Адреса користувача
            limit: Кількість транзакцій
            
        Returns:
            List транзакцій (deposit, withdraw, rewards)
        """
        try:
            transactions = self.api.get_transactions(user_address, limit)
            
            # TODO: Фільтрувати тільки транзакції з pool_address
            # TODO: Парсити тип транзакції (deposit/withdraw/reward)
            
            parsed_txs = []
            for tx in transactions:
                # Спрощений парсинг (потрібно покращити)
                parsed_txs.append({
                    "hash": tx.get("transaction_id", {}).get("hash", ""),
                    "timestamp": tx.get("utime", 0),
                    "type": "unknown",  # TODO: визначити тип
                    "amount": 0,  # TODO: парсити з in_msg/out_msg
                    "status": "completed"
                })
            
            return parsed_txs
        except Exception as e:
            return []
    
    def prepare_deposit_transaction(self, user_address: str, amount_ton: float) -> Dict:
        """
        Підготувати дані для deposit транзакції
        
        Args:
            user_address: Адреса користувача
            amount_ton: Сума для стейкінгу в TON
            
        Returns:
            Dict з даними для транзакції (to, amount, payload)
        """
        # TODO: Сформувати правильний payload для deposit операції
        # Зараз - базова структура
        
        amount_nanoton = int(amount_ton * 1_000_000_000)
        
        return {
            "to": self.pool_address,
            "amount": str(amount_nanoton),
            "payload": "",  # TODO: cell with deposit message
            "from": user_address,
            "valid_until": None,  # TODO: додати expiration
            "type": "deposit"
        }
    
    def prepare_withdraw_transaction(self, user_address: str, amount_ton: float) -> Dict:
        """
        Підготувати дані для withdraw транзакції
        
        Args:
            user_address: Адреса користувача
            amount_ton: Сума для виведення в TON
            
        Returns:
            Dict з даними для транзакції
        """
        # TODO: Сформувати правильний payload для withdraw операції
        
        amount_nanoton = int(amount_ton * 1_000_000_000)
        
        return {
            "to": self.pool_address,
            "amount": "50000000",  # Gas fee (0.05 TON)
            "payload": "",  # TODO: cell with withdraw message + amount
            "from": user_address,
            "valid_until": None,
            "type": "withdraw",
            "withdraw_amount": str(amount_nanoton)
        }


# Singleton instance (можна налаштувати через environment variables)
_pool_service = None

def get_pool_service() -> PoolService:
    """
    Отримати singleton instance PoolService
    
    Returns:
        PoolService instance
    """
    global _pool_service
    if _pool_service is None:
        # TODO: Взяти pool_address з environment або config
        pool_address = os.getenv("TON_POOL_ADDRESS", "EQDk2VTvn04SUKJrW7rXahzdF8_Qi6utb0wj43InCu9vdjrR")
        testnet = os.getenv("TON_TESTNET", "true").lower() == "true"
        _pool_service = PoolService(pool_address, testnet)
    return _pool_service
