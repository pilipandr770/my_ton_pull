# backend/email_service.py
"""
Email notification service using SendGrid API
Sends email alerts for stake/unstake transactions and rewards
"""

import os
from typing import Optional, Dict, List
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content, Personalization
from dotenv import load_dotenv

load_dotenv()

class EmailService:
    """Send emails via SendGrid"""
    
    def __init__(self):
        """Initialize SendGrid client"""
        self.api_key = os.getenv("SENDGRID_API_KEY", "")
        self.from_email = os.getenv("EMAIL_FROM", "noreply@tonstakingpool.io")
        self.from_name = os.getenv("EMAIL_FROM_NAME", "TON Staking Pool")
        self.client = SendGridAPIClient(self.api_key) if self.api_key else None
        
    def is_configured(self) -> bool:
        """Check if SendGrid is properly configured"""
        return bool(self.api_key and self.client)
    
    def send_email(
        self,
        to_email: str,
        to_name: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """
        Send email via SendGrid
        
        Args:
            to_email: Recipient email address
            to_name: Recipient name
            subject: Email subject
            html_content: HTML email body
            text_content: Plain text email body (optional)
            
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.is_configured():
            print(f"⚠️  SendGrid not configured, skipping email to {to_email}")
            return False
        
        try:
            message = Mail(
                from_email=Email(self.from_email, self.from_name),
                to_emails=To(to_email, to_name),
                subject=subject,
                plain_text_content=text_content or "N/A",
                html_content=html_content
            )
            
            response = self.client.send(message)
            
            if response.status_code in [200, 201, 202]:
                print(f"✅ Email sent to {to_email}")
                return True
            else:
                print(f"⚠️  Failed to send email to {to_email}: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error sending email to {to_email}: {str(e)}")
            return False
    
    def send_stake_confirmation(self, email: str, name: str, amount: float, tx_hash: str) -> bool:
        """Send stake confirmation email"""
        subject = f"✅ TON Staking Pool - Stake Confirmation ({amount} TON)"
        
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f9f9f9; border-radius: 10px;">
                    <h1 style="color: #2563eb; text-align: center;">💎 Stake Successful</h1>
                    
                    <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <p>Hi <strong>{name}</strong>,</p>
                        
                        <p>Your stake transaction has been recorded on the TON Staking Pool.</p>
                        
                        <div style="background: #f0f9ff; padding: 15px; border-left: 4px solid #2563eb; margin: 15px 0;">
                            <p><strong>Transaction Details:</strong></p>
                            <p>Amount: <strong>{amount} TON</strong></p>
                            <p>Status: <strong>⏳ Pending Confirmation</strong></p>
                            <p>Transaction Hash: <code style="background: #e5e7eb; padding: 5px; border-radius: 3px;">{tx_hash[:20]}...</code></p>
                        </div>
                        
                        <p>Your stake will be confirmed once the transaction is processed on the blockchain (usually within a few minutes).</p>
                        
                        <p>You can track your transaction on <a href="https://tonscan.org/tx/{tx_hash}" style="color: #2563eb; text-decoration: none;">TonScan</a>.</p>
                        
                        <p style="margin-top: 20px; color: #666; font-size: 12px;">
                            This is an automated message. Please do not reply to this email.
                        </p>
                    </div>
                </div>
            </body>
        </html>
        """
        
        return self.send_email(email, name, subject, html_content)
    
    def send_unstake_confirmation(self, email: str, name: str, tx_hash: str, lock_days: int = 7) -> bool:
        """Send unstake confirmation email with withdrawal lock info"""
        subject = f"📤 TON Staking Pool - Unstake Initiated (Locked for {lock_days} days)"
        
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f9f9f9; border-radius: 10px;">
                    <h1 style="color: #ea580c; text-align: center;">📤 Unstake Initiated</h1>
                    
                    <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <p>Hi <strong>{name}</strong>,</p>
                        
                        <p>Your unstake request has been submitted to the TON Staking Pool.</p>
                        
                        <div style="background: #fff7ed; padding: 15px; border-left: 4px solid #ea580c; margin: 15px 0;">
                            <p><strong>⏱️ Withdrawal Lock Notice:</strong></p>
                            <p>Your funds will be locked for <strong>{lock_days} days</strong> for processing and security.</p>
                            <p>Transaction Hash: <code style="background: #e5e7eb; padding: 5px; border-radius: 3px;">{tx_hash[:20]}...</code></p>
                        </div>
                        
                        <p><strong>What happens next:</strong></p>
                        <ol>
                            <li>Your transaction is processed on the blockchain</li>
                            <li>Funds are locked for {lock_days} days</li>
                            <li>After the lock period, you can claim your withdrawn TON</li>
                            <li>We'll send you an email when funds are ready to withdraw</li>
                        </ol>
                        
                        <p>You can track your transaction on <a href="https://tonscan.org/tx/{tx_hash}" style="color: #ea580c; text-decoration: none;">TonScan</a>.</p>
                        
                        <p style="margin-top: 20px; color: #666; font-size: 12px;">
                            This is an automated message. Please do not reply to this email.
                        </p>
                    </div>
                </div>
            </body>
        </html>
        """
        
        return self.send_email(email, name, subject, html_content)
    
    def send_transaction_confirmed(self, email: str, name: str, amount: float, tx_hash: str, tx_type: str) -> bool:
        """Send transaction confirmation email"""
        is_stake = tx_type == "stake"
        icon = "💎" if is_stake else "💸"
        action = "Stake" if is_stake else "Unstake"
        
        subject = f"✅ {icon} TON Staking Pool - {action} Confirmed"
        
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f9f9f9; border-radius: 10px;">
                    <h1 style="color: #16a34a; text-align: center;">✅ {action} Confirmed</h1>
                    
                    <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <p>Hi <strong>{name}</strong>,</p>
                        
                        <p>Great news! Your <strong>{action.lower()}</strong> transaction has been confirmed on the blockchain.</p>
                        
                        <div style="background: #f0fdf4; padding: 15px; border-left: 4px solid #16a34a; margin: 15px 0;">
                            <p><strong>Transaction Details:</strong></p>
                            <p>Type: <strong>{action}</strong></p>
                            <p>Amount: <strong>{amount} TON</strong></p>
                            <p>Status: <strong>✅ Confirmed</strong></p>
                            <p>Transaction Hash: <code style="background: #e5e7eb; padding: 5px; border-radius: 3px;">{tx_hash[:20]}...</code></p>
                        </div>
                        
                        <p>Your transaction is now permanently recorded on the TON blockchain.</p>
                        
                        <p style="margin-top: 20px; color: #666; font-size: 12px;">
                            This is an automated message. Please do not reply to this email.
                        </p>
                    </div>
                </div>
            </body>
        </html>
        """
        
        return self.send_email(email, name, subject, html_content)
    
    def send_withdrawal_ready(self, email: str, name: str, amount: float, tx_hash: str) -> bool:
        """Send notification that withdrawal is ready to claim"""
        subject = "💰 TON Staking Pool - Your Withdrawal is Ready!"
        
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f9f9f9; border-radius: 10px;">
                    <h1 style="color: #16a34a; text-align: center;">💰 Withdrawal Ready!</h1>
                    
                    <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <p>Hi <strong>{name}</strong>,</p>
                        
                        <p>Your withdrawal lock has expired and your funds are now ready to claim!</p>
                        
                        <div style="background: #f0fdf4; padding: 15px; border-left: 4px solid #16a34a; margin: 15px 0;">
                            <p><strong>Withdrawal Details:</strong></p>
                            <p>Amount: <strong>{amount} TON</strong></p>
                            <p>Status: <strong>🔓 Ready to Withdraw</strong></p>
                            <p>Transaction Hash: <code style="background: #e5e7eb; padding: 5px; border-radius: 3px;">{tx_hash[:20]}...</code></p>
                        </div>
                        
                        <p>Log in to your TON Staking Pool account to complete your withdrawal.</p>
                        
                        <p style="margin-top: 20px; color: #666; font-size: 12px;">
                            This is an automated message. Please do not reply to this email.
                        </p>
                    </div>
                </div>
            </body>
        </html>
        """
        
        return self.send_email(email, name, subject, html_content)


# Singleton instance
_email_service = None

def get_email_service() -> EmailService:
    """Get or create email service instance"""
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service
