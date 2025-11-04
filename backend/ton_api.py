# backend/ton_api.py
"""
TON Blockchain API Integration
Підключення до TON через TonCenter API для читання on-chain даних
"""

import os
import json
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
        headers = {
            "User-Agent": "TON-Pool-Backend/1.0"
        }
        if self.api_key:
            headers["X-API-Key"] = self.api_key
            
        try:
            # Set timeout and retry logic
            response = requests.get(
                url, 
                params=params or {}, 
                headers=headers, 
                timeout=15,
                allow_redirects=True
            )
            
            # Log response for debugging
            if response.status_code != 200:
                print(f"API Response ({response.status_code}): {response.text[:200]}")
            
            response.raise_for_status()
            data = response.json()
            
            if not data.get("ok"):
                raise Exception(f"API error: {data.get('error', 'Unknown error')}")
                
            return data.get("result", {})
        except requests.exceptions.RequestException as e:
            # Log full error for debugging
            print(f"API Request Error: {str(e)}")
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
    
    def check_transaction_status(self, tx_hash: str) -> Dict:
        """
        Перевірити статус транзакції на blockchain
        
        Args:
            tx_hash: BOC хеш транзакції (Transaction ID з blockchain)
            
        Returns:
            Dict з информацією про транзакцію:
            {
                "status": "not_found" | "pending" | "confirmed",
                "confirmations": int,
                "block_time": int (unix timestamp),
                "block_height": int,
                "fee": int (nanotons),
                "amount": int (nanotons),
                "from": str,
                "to": str,
                "message": str,
            }
        """
        try:
            # BOC transactions can be queried directly by hash
            # We need to search for the transaction in blocks or by hash
            # TonCenter API doesn't have direct transaction lookup by hash
            # So we'll return "pending" status since we can't verify yet
            # Later, we'll need to implement better verification
            
            # For now, we return a structure that indicates transaction is still pending
            # In production, you'd want to implement block explorer integration
            return {
                "status": "pending",
                "confirmations": 0,
                "block_time": None,
                "block_height": None,
                "fee": None,
                "amount": None,
                "from": None,
                "to": None,
                "message": "Transaction status will be updated when confirmed",
                "tx_hash": tx_hash
            }
        except Exception as e:
            print(f"Error checking transaction status: {str(e)}")
            return {
                "status": "unknown",
                "error": str(e),
                "tx_hash": tx_hash
            }
    
    def run_get_method(self, address: str, method: str, stack: List = None) -> Dict:
        """
        Виконати get-метод смарт-контракту
        
        Args:
            address: Адреса контракту
            method: Назва методу
            stack: Параметри для методу у форматі [[type, value], ...]
                   Приклад: [["tblkarg", "0QD-AKzjnXxLk8PFyVJvt9sIQW2_MqmSwi5qPfBZbhKT5bXf"]]
            
        Returns:
            Результат виконання методу з stack-ом відповідей
        """
        params = {
            "address": address,
            "method": method
        }
        if stack:
            # Конвертувати stack у правильний формат для TonCenter
            # TonCenter очікує stack у форматі: [["num", "123"], ["slice", "..."], ...]
            params["stack"] = json.dumps(stack)
            
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
    
    def get_user_staked_amount(self, user_address: str) -> float:
        """
        Отримати скільки користувач застейкав у пулі
        
        Args:
            user_address: Адреса користувача (user-friendly)
            
        Returns:
            Сума в TON або 0 якщо користувач не в пулі
        """
        try:
            # Виконати get-метод "get_staked" на контракту пула
            # Метод очікує адресу користувача як параметр
            result = self.api.run_get_method(
                self.pool_address,
                "get_staked",
                [["slice", user_address]]  # Параметр: адреса користувача
            )
            
            # Парсити результат
            if result and "stack" in result:
                stack = result["stack"]
                if len(stack) > 0:
                    # Перший елемент - staked amount
                    # TonCenter повертає у форматі ["num", "123456789"]
                    staked_data = stack[0]
                    if len(staked_data) > 1:
                        staked_nanoton = int(staked_data[1])
                        return staked_nanoton / 1_000_000_000  # У TON
            
            return 0.0
        except Exception as e:
            print(f"Error getting staked amount for {user_address}: {str(e)}")
            return 0.0
    
    def get_user_rewards(self, user_address: str) -> float:
        """
        Отримати накопичені награди користувача
        
        Args:
            user_address: Адреса користувача (user-friendly)
            
        Returns:
            Сума награди в TON
        """
        try:
            # Виконати get-метод "get_rewards" на контракту пула
            result = self.api.run_get_method(
                self.pool_address,
                "get_rewards",
                [["slice", user_address]]  # Параметр: адреса користувача
            )
            
            # Парсити результат
            if result and "stack" in result:
                stack = result["stack"]
                if len(stack) > 0:
                    # Перший елемент - rewards
                    rewards_data = stack[0]
                    if len(rewards_data) > 1:
                        rewards_nanoton = int(rewards_data[1])
                        return rewards_nanoton / 1_000_000_000  # У TON
            
            return 0.0
        except Exception as e:
            print(f"Error getting rewards for {user_address}: {str(e)}")
            return 0.0
    
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
            
            # Отримати з контракту реальні дані
            staked_amount = self.get_user_staked_amount(user_address)
            accumulated_rewards = self.get_user_rewards(user_address)
            
            # Розрахувати share percentage
            try:
                total_pool_balance = self.api.get_address_balance(self.pool_address)
                share_percentage = (staked_amount / total_pool_balance * 100) if total_pool_balance > 0 else 0.0
            except:
                share_percentage = 0.0
            
            return {
                "user_address": user_address,
                "wallet_balance": wallet_balance,  # Реальний баланс гаманця
                "staked_amount": staked_amount,  # Реальні дані з контракту
                "jettons_balance": 0,  # TODO: з контракту JettonWallet
                "accumulated_rewards": accumulated_rewards,  # Реальні награди з контракту
                "share_percentage": share_percentage,  # Розраховано з балансу
            }
        except Exception as e:
            print(f"Error getting user balance: {str(e)}")
            return {
                "error": str(e),
                "user_address": user_address,
                "wallet_balance": 0,
                "staked_amount": 0,
                "accumulated_rewards": 0,
                "share_percentage": 0,
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
    
    def check_transaction_confirmed(self, tx_hash: str) -> Dict:
        """
        Перевірити, чи підтверджена транзакція на blockchain
        
        Args:
            tx_hash: BOC хеш транзакції
            
        Returns:
            Dict з статусом:
            {
                "confirmed": bool,
                "status": "pending" | "confirmed" | "failed" | "unknown",
                "message": str
            }
        """
        try:
            # Спроба перевірити статус транзакції через API
            status_data = self.api.check_transaction_status(tx_hash)
            
            is_confirmed = status_data.get("status") == "confirmed"
            
            return {
                "confirmed": is_confirmed,
                "status": status_data.get("status", "unknown"),
                "confirmations": status_data.get("confirmations", 0),
                "block_time": status_data.get("block_time"),
                "message": status_data.get("message", ""),
                "tx_hash": tx_hash
            }
        except Exception as e:
            print(f"Error checking transaction confirmation: {str(e)}")
            return {
                "confirmed": False,
                "status": "unknown",
                "message": f"Error: {str(e)}",
                "tx_hash": tx_hash
            }
    
    def prepare_deposit_transaction(self, user_address: str, amount_ton: float) -> Dict:
        """
        Підготувати дані для deposit транзакції
        Номіноване просто відправляє TON на адресу пулу з op=1
        
        Args:
            user_address: Адреса користувача (user-friendly)
            amount_ton: Сума для стейкінгу в TON
            
        Returns:
            Dict з даними для транзакції (ready for TonConnect signing)
        """
        amount_nanoton = int(amount_ton * 1_000_000_000)
        
        # Simple deposit: send TON to pool with op=1
        # No payload needed - just send coins with op=1 opcode
        payload = bytes([0x00, 0x00, 0x00, 0x01])  # op=1
        
        return {
            "to": self.pool_address,
            "amount": str(amount_nanoton),
            "payload": payload.hex(),
            "from": user_address,
            "type": "deposit",
            "description": f"Stake {amount_ton} TON in pool"
        }
    
    def prepare_withdraw_transaction(self, user_address: str, amount_ton: float = None) -> Dict:
        """
        Підготувати дані для withdraw транзакції
        Номіноване відправляє op=2 з limit для обробки запиту на вихід
        
        Args:
            user_address: Адреса користувача (user-friendly)
            amount_ton: Сума для виведення (не використовується, опціонально)
            
        Returns:
            Dict з даними для транзакції (ready for TonConnect signing)
        """
        # Withdraw: send op=2 with limit parameter
        # op=2: process withdraw requests (limit=255 means process all)
        gas_fee = 50_000_000  # 0.05 TON for gas
        
        # Build payload: op=2 (4 bytes) + limit=255 (1 byte)
        payload_data = bytes([0x00, 0x00, 0x00, 0x02]) + bytes([0xFF])  # op=2, limit=255
        
        return {
            "to": self.pool_address,
            "amount": str(gas_fee),
            "payload": payload_data.hex(),
            "from": user_address,
            "type": "withdraw",
            "description": "Request withdrawal from pool"
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
