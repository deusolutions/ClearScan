"""
Simple Telegram bot for network scan notifications
"""

import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .models import Network, ScanResult, NetworkChange

logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self, token: str):
        """Initialize bot with token."""
        self.token = token
        self.app = Application.builder().token(token).build()
        
        # Setup database
        engine = create_engine('sqlite:///clearscan.db')
        self.Session = sessionmaker(bind=engine)
        
        # Add handlers
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(CommandHandler("help", self.help))
        self.app.add_handler(CommandHandler("status", self.status))
        self.app.add_handler(CommandHandler("networks", self.list_networks))
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send welcome message."""
        await update.message.reply_text(
            "Welcome to ClearScan! 🔍\n"
            "I will notify you about network changes.\n"
            "Use /help to see available commands."
        )
    
    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send help message."""
        await update.message.reply_text(
            "Available commands:\n"
            "/start - Start the bot\n"
            "/help - Show this help message\n"
            "/status - Show system status\n"
            "/networks - List monitored networks"
        )
    
    async def status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show system status."""
        session = self.Session()
        try:
            networks = session.query(Network).count()
            active = session.query(Network).filter_by(is_active=True).count()
            scans = session.query(ScanResult).count()
            changes = session.query(NetworkChange).count()
            
            await update.message.reply_text(
                f"📊 System Status\n"
                f"Networks: {networks} (Active: {active})\n"
                f"Total Scans: {scans}\n"
                f"Changes Detected: {changes}"
            )
        finally:
            session.close()
    
    async def list_networks(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """List monitored networks."""
        session = self.Session()
        try:
            networks = session.query(Network).all()
            if not networks:
                await update.message.reply_text("No networks configured.")
                return
            
            text = "📡 Monitored Networks:\n\n"
            for net in networks:
                status = "✅ Active" if net.is_active else "❌ Inactive"
                text += f"{net.name} ({net.ip_range})\n{status}\n\n"
            
            await update.message.reply_text(text)
        finally:
            session.close()
    
    async def send_change_notification(self, change: NetworkChange):
        """Send notification about network changes."""
        session = self.Session()
        try:
            network = session.query(Network).get(change.network_id)
            text = (
                f"🔔 Network Change Detected!\n"
                f"Network: {network.name}\n"
                f"Severity: {change.severity.upper()}\n\n"
                f"{change.message}"
            )
            # В реальном боте здесь будет отправка в настроенные чаты
            logger.info(f"Would send notification: {text}")
        finally:
            session.close()
    
    def run(self):
        """Start the bot."""
        self.app.run_polling() 