# services/enhanced_alerts.py
import os
import logging
from datetime import datetime
from typing import Dict, List, Optional
from telegram import Bot
from telegram.error import TelegramError
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json

class EnhancedAlertsService:
    def __init__(self):
        self.telegram_bot = None
        self.telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.logger = logging.getLogger(__name__)
        
        # Initialize Telegram bot if token is available
        telegram_token = os.getenv("TELEGRAM_TOKEN")
        if telegram_token:
            try:
                self.telegram_bot = Bot(token=telegram_token)
            except Exception as e:
                self.logger.error(f"Failed to initialize Telegram bot: {e}")
        
        # Email configuration
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.email_user = os.getenv("EMAIL_USER")
        self.email_password = os.getenv("EMAIL_PASSWORD")
        self.recipient_email = os.getenv("RECIPIENT_EMAIL")
        
        # Alert history for rate limiting
        self.alert_history = []
        self.max_alerts_per_hour = 10
        
    def format_funding_alert(self, coin: str, funding_rate: float, threshold: float) -> str:
        """Format funding rate alert message"""
        direction = "HIGH" if funding_rate > 0 else "LOW"
        emoji = "🚀" if funding_rate > 0 else "📉"
        
        message = f"""
{emoji} FUNDING RATE ALERT {emoji}

🪙 Asset: {coin}/USDT
📊 Current Rate: {funding_rate:.4f}%
⚠️ Threshold: ±{threshold:.2f}%
📈 Direction: {direction}
🕐 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

{'🐂 Bullish sentiment detected' if funding_rate > 0 else '🐻 Bearish sentiment detected'}
        """
        return message.strip()
    
    def format_whale_alert(self, whale_data: Dict) -> str:
        """Format whale activity alert"""
        emoji_map = {
            'Open Long': '🟢',
            'Open Short': '🔴', 
            'Close Long': '🟡',
            'Close Short': '🟠'
        }
        
        emoji = emoji_map.get(whale_data['activity'], '⚪')
        
        message = f"""
🐋 WHALE ACTIVITY DETECTED 🐋

{emoji} Action: {whale_data['activity']}
🪙 Asset: {whale_data['symbol']}
💰 Size: ${whale_data['position_size']:,.0f}
💲 Price: ${whale_data['price']:,.2f}
🏦 Exchange: {whale_data.get('exchange', 'Unknown')}
🕐 Time: {whale_data['timestamp'].strftime('%H:%M:%S UTC')}

📊 Address: {whale_data['address']}
        """
        return message.strip()
    
    def format_liquidation_alert(self, liquidation_data: Dict) -> str:
        """Format liquidation alert"""
        total_liq = liquidation_data['total'] / 1000000  # Convert to millions
        
        message = f"""
💥 MASS LIQUIDATION ALERT 💥

🔥 Total Liquidated: ${total_liq:.1f}M
📊 Long Liquidations: ${liquidation_data['long_liquidations']/1000000:.1f}M
📊 Short Liquidations: ${liquidation_data['short_liquidations']/1000000:.1f}M
🎯 Ratio: {liquidation_data['liquidation_ratio']*100:.1f}% Long
⚡ Events: {liquidation_data['liquidation_count']} trades
🕐 Time: {datetime.now().strftime('%H:%M:%S UTC')}

⚠️ High volatility expected
        """
        return message.strip()
    
    def format_market_summary(self, market_data: Dict) -> str:
        """Format comprehensive market summary"""
        message = f"""
📊 MARKET SUMMARY REPORT 📊

🏆 Top Performer: {market_data.get('top_performer', 'N/A')}
📉 Worst Performer: {market_data.get('worst_performer', 'N/A')}
💰 Total OI: ${market_data.get('total_oi', 0)/1000000:.1f}M
🐋 Active Whales: {market_data.get('whale_count', 0)}
💥 24h Liquidations: ${market_data.get('total_liquidations', 0)/1000000:.1f}M

📈 Market Sentiment: {market_data.get('sentiment', 'Neutral')}
⚡ Volatility: {market_data.get('volatility', 'Normal')}
🕐 Updated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}
        """
        return message.strip()
    
    async def send_telegram_alert(self, message: str, parse_mode: str = 'HTML') -> bool:
        """Send alert via Telegram"""
        if not self.telegram_bot or not self.telegram_chat_id:
            self.logger.warning("Telegram not configured")
            return False
        
        try:
            await self.telegram_bot.send_message(
                chat_id=self.telegram_chat_id,
                text=message,
                parse_mode=parse_mode
            )
            self.logger.info("Telegram alert sent successfully")
            return True
            
        except TelegramError as e:
            self.logger.error(f"Failed to send Telegram alert: {e}")
            return False
    
    def send_email_alert(self, subject: str, message: str) -> bool:
        """Send alert via email"""
        if not all([self.email_user, self.email_password, self.recipient_email]):
            self.logger.warning("Email not configured")
            return False
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_user
            msg['To'] = self.recipient_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(message, 'plain'))
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_user, self.email_password)
            
            server.send_message(msg)
            server.quit()
            
            self.logger.info("Email alert sent successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send email alert: {e}")
            return False
    
    def should_send_alert(self, alert_type: str) -> bool:
        """Rate limiting for alerts"""
        now = datetime.now()
        
        # Remove alerts older than 1 hour
        self.alert_history = [
            alert for alert in self.alert_history 
            if (now - alert['timestamp']).seconds < 3600
        ]
        
        # Check if we've exceeded the hourly limit
        if len(self.alert_history) >= self.max_alerts_per_hour:
            return False
        
        # Check for duplicate alerts in the last 15 minutes
        recent_alerts = [
            alert for alert in self.alert_history
            if (now - alert['timestamp']).seconds < 900  # 15 minutes
            and alert['type'] == alert_type
        ]
        
        if len(recent_alerts) > 0:
            return False
        
        return True
    
    async def send_funding_alert(self, coin: str, funding_rate: float, threshold: float):
        """Send funding rate alert"""
        if not self.should_send_alert('funding'):
            return
        
        message = self.format_funding_alert(coin, funding_rate, threshold)
        
        # Send via Telegram
        await self.EnhancedAlertsService.send_telegram_alert(message)
        
        # Send via email
        self.send_email_alert(f"Funding Rate Alert - {coin}", message)
        
        # Record alert
        self.alert_history.append({
            'type': 'funding',
            'timestamp': datetime.now(),
            'coin': coin,
            'rate': funding_rate
        })
    
    async def send_whale_alert(self, whale_data: Dict):
        """Send whale activity alert"""
        if not self.should_send_alert('whale'):
            return
        
        message = self.format_whale_alert(whale_data)
        
        await self.EnhancedAlertsService.send_telegram_alert(message)
        self.send_email_alert(f"Whale Alert - {whale_data['symbol']}", message)
        
        self.alert_history.append({
            'type': 'whale',
            'timestamp': datetime.now(),
            'coin': whale_data['symbol'],
            'size': whale_data['position_size']
        })
    
    async def send_liquidation_alert(self, coin: str, liquidation_data: Dict):
        """Send liquidation alert"""
        if not self.should_send_alert('liquidation'):
            return
        
        message = self.format_liquidation_alert(liquidation_data)
        
        await self.EnhancedAlertsService.send_telegram_alert(message)
        self.send_email_alert(f"Liquidation Alert - {coin}", message)
        
        self.alert_history.append({
            'type': 'liquidation',
            'timestamp': datetime.now(),
            'coin': coin,
            'amount': liquidation_data['total']
        })
    
    async def send_market_summary(self, market_data: Dict):
        """Send periodic market summary"""
        message = self.format_market_summary(market_data)
        
        await self.EnhancedAlertsService.send_telegram_alert(message)
        self.send_email_alert("Market Summary Report", message)
    
    def get_alert_stats(self) -> Dict:
        """Get alert statistics"""
        now = datetime.now()
        
        # Alerts in last hour
        recent_alerts = [
            alert for alert in self.alert_history
            if (now - alert['timestamp']).seconds < 3600
        ]
        
        # Count by type
        alert_counts = {}
        for alert in recent_alerts:
            alert_type = alert['type']
            alert_counts[alert_type] = alert_counts.get(alert_type, 0) + 1
        
        return {
            'total_alerts_last_hour': len(recent_alerts),
            'alerts_by_type': alert_counts,
            'rate_limit_status': f"{len(recent_alerts)}/{self.max_alerts_per_hour}",
            'last_alert': recent_alerts[-1]['timestamp'] if recent_alerts else None
        }