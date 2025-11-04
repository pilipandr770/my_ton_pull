# backend/transaction_monitor.py
"""
Background task to monitor transaction status on blockchain
Polls pending transactions and updates their status
Sends email notifications for transaction status changes
"""

import os
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from models import db, Transaction, User
from ton_api import TONAPIClient
from email_service import get_email_service

scheduler = None
_initialized = False

def init_scheduler(app):
    """Initialize the background scheduler"""
    global scheduler, _initialized
    
    if _initialized:
        return
    
    scheduler = BackgroundScheduler()
    
    # Add polling job
    scheduler.add_job(
        func=poll_pending_transactions,
        trigger="interval",
        seconds=30,  # Poll every 30 seconds
        id="transaction_poller",
        name="Poll pending transactions",
        replace_existing=True,
        max_instances=1  # Only one instance can run at a time
    )
    
    scheduler.start()
    print("✅ Transaction monitor started (polling every 30s)")
    _initialized = True

def stop_scheduler():
    """Stop the background scheduler"""
    global scheduler
    if scheduler and scheduler.running:
        scheduler.shutdown()
        print("⏹️  Transaction monitor stopped")

def poll_pending_transactions():
    """
    Poll all pending transactions and update their status
    This runs in background every 30 seconds
    """
    try:
        # Query all pending transactions
        pending_txs = Transaction.query.filter_by(status='pending').all()
        
        if not pending_txs:
            return
        
        print(f"🔄 Checking {len(pending_txs)} pending transactions...")
        
        api_client = TONAPIClient(testnet=False)  # Use mainnet
        email_service = get_email_service()
        updated_count = 0
        
        for tx in pending_txs:
            try:
                # Check if transaction is confirmed
                status_data = api_client.check_transaction_status(tx.tx_hash)
                
                new_status = status_data.get("status", "unknown")
                
                # Update transaction status if changed
                if new_status in ['confirmed', 'failed']:
                    old_status = tx.status
                    tx.update_status(new_status)
                    db.session.add(tx)
                    updated_count += 1
                    print(f"  ✅ TX {tx.tx_hash[:10]}... status: {old_status} → {new_status}")
                    
                    # Send email notification
                    if tx.user_id:
                        user = User.query.get(tx.user_id)
                        if user and user.email:
                            try:
                                if new_status == 'confirmed':
                                    email_service.send_transaction_confirmed(
                                        user.email,
                                        user.email.split('@')[0],  # Use email prefix as name
                                        float(tx.amount) if tx.amount else 0,
                                        tx.tx_hash,
                                        tx.type
                                    )
                                elif new_status == 'failed':
                                    # Could send failure notification here
                                    print(f"  ⚠️  TX {tx.tx_hash[:10]}... failed for user {user.email}")
                            except Exception as e:
                                print(f"  ❌ Error sending email: {str(e)}")
                    
            except Exception as e:
                print(f"  ❌ Error checking TX {tx.tx_hash[:10]}...: {str(e)}")
                continue
        
        if updated_count > 0:
            try:
                db.session.commit()
                print(f"💾 Updated {updated_count} transactions")
            except Exception as e:
                db.session.rollback()
                print(f"❌ Database error: {str(e)}")
        
    except Exception as e:
        print(f"❌ Error in transaction polling: {str(e)}")

def check_transaction_status_sync(tx_hash: str) -> dict:
    """
    Synchronously check transaction status (for on-demand checks)
    
    Args:
        tx_hash: Transaction hash to check
        
    Returns:
        Status dictionary
    """
    try:
        api_client = TONAPIClient(testnet=False)
        return api_client.check_transaction_status(tx_hash)
    except Exception as e:
        return {
            "status": "unknown",
            "error": str(e),
            "tx_hash": tx_hash
        }

def update_transaction_status(tx_hash: str, new_status: str) -> bool:
    """
    Manually update a transaction status in database
    
    Args:
        tx_hash: Transaction hash
        new_status: New status ('pending', 'confirmed', 'failed')
        
    Returns:
        True if successful, False otherwise
    """
    try:
        tx = Transaction.query.filter_by(tx_hash=tx_hash).first()
        if not tx:
            return False
        
        result = tx.update_status(new_status)
        if result:
            db.session.add(tx)
            db.session.commit()
            print(f"✅ Updated TX {tx_hash[:10]}... to {new_status}")
        return result
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error updating transaction: {str(e)}")
        return False
