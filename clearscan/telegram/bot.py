"""
Telegram Bot Module for ClearScan

This module handles all Telegram bot interactions, including:
- User notifications
- Command handling
- Status updates
"""

import logging
from typing import Optional
from datetime import datetime

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from sqlalchemy.orm import Session

from ..models import User, NetworkChange, ChangeNotification
from ..security import SecurityManager

logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self, token: str, allowed_chat_id: str, db_session: Session):
        """
        Initialize Telegram bot.
        
        Args:
            token: Telegram bot token
            allowed_chat_id: Allowed chat ID for notifications
            db_session: Database session
        """
        self.token = token
        self.allowed_chat_id = allowed_chat_id
        self.db_session = db_session
        self.security = SecurityManager(db_session)
        self.application = None

    async def start(self):
        """Start the Telegram bot."""
        self.application = Application.builder().token(self.token).build()
        
        # Add handlers
        self.application.add_handler(CommandHandler("start", self._start_command))
        self.application.add_handler(CommandHandler("help", self._help_command))
        self.application.add_handler(CommandHandler("status", self._status_command))
        self.application.add_handler(CommandHandler("recent", self._recent_changes))
        
        # Start bot
        await self.application.initialize()
        await self.application.start()
        await self.application.run_polling()

    async def stop(self):
        """Stop the Telegram bot."""
        if self.application:
            await self.application.stop()

    async def send_notification(self, message: str, severity: str = "info") -> bool:
        """
        Send notification message.
        
        Args:
            message: Message to send
            severity: Message severity level
            
        Returns:
            bool: Whether message was sent successfully
        """
        if not self.application:
            logger.error("Bot not initialized")
            return False

        try:
            emoji = self._get_severity_emoji(severity)
            formatted_message = f"{emoji} {message}"
            
            await self.application.bot.send_message(
                chat_id=self.allowed_chat_id,
                text=formatted_message,
                parse_mode='HTML'
            )
            return True
        except Exception as e:
            logger.error(f"Failed to send notification: {str(e)}")
            return False

    def _get_severity_emoji(self, severity: str) -> str:
        """Get emoji for severity level."""
        return {
            "critical": "🚨",
            "high": "⚠️",
            "medium": "⚡",
            "low": "ℹ️",
            "info": "📝"
        }.get(severity.lower(), "ℹ️")

    async def _start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        welcome_message = (
            "👋 Добро пожаловать в ClearScan!\n\n"
            "Я буду отправлять вам уведомления об изменениях в вашей сети.\n\n"
            "Доступные команды:\n"
            "/help - Показать справку\n"
            "/status - Показать текущий статус\n"
            "/recent - Показать последние изменения"
        )
        await update.message.reply_text(welcome_message)

    async def _help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command."""
        help_message = (
            "🔍 <b>Команды ClearScan:</b>\n\n"
            "/start - Начать работу с ботом\n"
            "/help - Показать это сообщение\n"
            "/status - Показать текущий статус сканирования\n"
            "/recent - Показать последние изменения в сети\n\n"
            "При обнаружении изменений в сети я автоматически отправлю уведомление."
        )
        await update.message.reply_text(help_message, parse_mode='HTML')

    async def _status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command."""
        # Get latest scan info from database
        latest_scan = self.db_session.query(NetworkChange).order_by(
            NetworkChange.timestamp.desc()
        ).first()
        
        if latest_scan:
            status = (
                "📊 <b>Текущий статус:</b>\n\n"
                f"Последнее сканирование: {latest_scan.timestamp}\n"
                f"Статус: {self._get_severity_emoji(latest_scan.severity)} {latest_scan.severity}\n"
            )
        else:
            status = "❓ Сканирование еще не проводилось"
            
        await update.message.reply_text(status, parse_mode='HTML')

    async def _recent_changes(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /recent command."""
        # Get 5 most recent changes
        recent = self.db_session.query(NetworkChange).order_by(
            NetworkChange.timestamp.desc()
        ).limit(5).all()
        
        if not recent:
            await update.message.reply_text("🔍 Изменений пока не обнаружено")
            return
            
        message = "📝 <b>Последние изменения:</b>\n\n"
        for change in recent:
            message += (
                f"{self._get_severity_emoji(change.severity)} "
                f"{change.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"Severity: {change.severity}\n\n"
            )
            
        await update.message.reply_text(message, parse_mode='HTML') 