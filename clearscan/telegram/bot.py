"""
Telegram Bot Module for ClearScan

This module handles all Telegram bot interactions, including:
- User notifications
- Command handling
- Status updates
"""

import logging
from typing import Optional, List, Dict
from datetime import datetime, timedelta

from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    ConversationHandler,
)
from sqlalchemy.orm import Session

from ..models import User, NetworkChange, ChangeNotification, Network, TelegramChat
from ..security import SecurityManager

logger = logging.getLogger(__name__)

# Состояния для ConversationHandler
SELECTING_NETWORK = 1

class ClearScanBot:
    def __init__(self, token: str, allowed_chat_ids: List[str], db_session: Session):
        """
        Initialize Telegram bot.
        
        Args:
            token: Telegram bot token
            allowed_chat_ids: List of allowed chat IDs for notifications
            db_session: Database session
        """
        self.token = token
        self.allowed_chat_ids = set(map(str, allowed_chat_ids))
        self.db_session = db_session
        self.security = SecurityManager(db_session)
        self.application = None
        self._rate_limits: Dict[str, Dict] = {}  # Chat ID -> rate limit info
        self._rate_limit_interval = timedelta(minutes=1)  # 1 minute window
        self._rate_limit_max_requests = 30  # Maximum requests per window

    async def start(self):
        """Start the Telegram bot."""
        self.application = Application.builder().token(self.token).build()
        
        # Add handlers
        self.application.add_handler(CommandHandler("start", self._start_command))
        self.application.add_handler(CommandHandler("help", self._help_command))
        self.application.add_handler(CommandHandler("status", self._status_command))
        self.application.add_handler(CommandHandler("recent", self._recent_changes))
        
        # Add subscription handlers
        subscribe_handler = ConversationHandler(
            entry_points=[CommandHandler("subscribe", self._subscribe_command)],
            states={
                SELECTING_NETWORK: [MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_network_selection)]
            },
            fallbacks=[CommandHandler("cancel", self._cancel_subscription)]
        )
        self.application.add_handler(subscribe_handler)
        self.application.add_handler(CommandHandler("unsubscribe", self._unsubscribe_command))
        self.application.add_handler(CommandHandler("list", self._list_subscriptions))
        
        # Start bot
        await self.application.initialize()
        await self.application.start()
        await self.application.run_polling()

    async def stop(self):
        """Stop the Telegram bot."""
        if self.application:
            await self.application.stop()

    def _check_access(self, chat_id: str) -> bool:
        """Check if chat has access to bot commands."""
        return str(chat_id) in self.allowed_chat_ids

    def _check_rate_limit(self, chat_id: str) -> bool:
        """Check if a chat has exceeded its rate limit."""
        now = datetime.utcnow()
        
        # Initialize or reset rate limit info if window has passed
        if chat_id not in self._rate_limits or \
           now - self._rate_limits[chat_id]['window_start'] > self._rate_limit_interval:
            self._rate_limits[chat_id] = {
                'window_start': now,
                'request_count': 0
            }
            
        # Increment request count
        self._rate_limits[chat_id]['request_count'] += 1
        
        # Check if limit exceeded
        return self._rate_limits[chat_id]['request_count'] <= self._rate_limit_max_requests

    async def _handle_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE, handler):
        """Generic command handler with rate limiting."""
        if not self._check_access(update.effective_chat.id):
            await update.message.reply_text("⛔ У вас нет доступа к этому боту.")
            return
            
        if not self._check_rate_limit(str(update.effective_chat.id)):
            await update.message.reply_text(
                "⚠️ Превышен лимит запросов. Пожалуйста, подождите минуту."
            )
            return
            
        return await handler(update, context)

    async def send_notification(self, chat_id: str, notification: ChangeNotification) -> bool:
        """
        Send notification message.
        
        Args:
            chat_id: Telegram chat ID
            notification: ChangeNotification instance
            
        Returns:
            bool: Whether message was sent successfully
        """
        if not self.application or not self._check_access(chat_id):
            logger.error(f"Cannot send notification to chat {chat_id}")
            return False

        try:
            emoji = self._get_severity_emoji(notification.severity)
            formatted_message = f"{emoji} {notification.message}"
            
            await self.application.bot.send_message(
                chat_id=chat_id,
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
        return await self._handle_command(update, context, self._start_handler)

    async def _start_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Actual /start command implementation."""
        welcome_message = (
            "👋 Добро пожаловать в ClearScan!\n\n"
            "Я буду отправлять вам уведомления об изменениях в вашей сети.\n\n"
            "Доступные команды:\n"
            "/help - Показать справку\n"
            "/status - Показать текущий статус\n"
            "/recent - Показать последние изменения\n"
            "/subscribe - Подписаться на уведомления\n"
            "/unsubscribe - Отписаться от уведомлений\n"
            "/list - Показать текущие подписки"
        )
        await update.message.reply_text(welcome_message)

    async def _help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command."""
        return await self._handle_command(update, context, self._help_handler)

    async def _help_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Actual /help command implementation."""
        help_message = (
            "🔍 <b>Команды ClearScan:</b>\n\n"
            "/start - Начать работу с ботом\n"
            "/help - Показать это сообщение\n"
            "/status - Показать текущий статус сканирования\n"
            "/recent - Показать последние изменения в сети\n"
            "/subscribe - Подписаться на уведомления для сети\n"
            "/unsubscribe - Отписаться от уведомлений для сети\n"
            "/list - Показать текущие подписки\n\n"
            "При обнаружении изменений в сети я автоматически отправлю уведомление."
        )
        await update.message.reply_text(help_message, parse_mode='HTML')

    async def _status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command."""
        return await self._handle_command(update, context, self._status_handler)

    async def _status_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Actual /status command implementation."""
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
        return await self._handle_command(update, context, self._recent_changes_handler)

    async def _recent_changes_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Actual /recent command implementation."""
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

    async def _subscribe_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /subscribe command."""
        result = await self._handle_command(update, context, self._subscribe_handler)
        return result if result is not None else ConversationHandler.END

    async def _subscribe_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Actual /subscribe command implementation."""
        # Get available networks
        networks = self.db_session.query(Network).filter_by(is_active=True).all()
        if not networks:
            await update.message.reply_text("❌ Нет доступных сетей для подписки")
            return ConversationHandler.END

        # Create keyboard with network names
        keyboard = [[network.name] for network in networks]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

        await update.message.reply_text(
            "Выберите сеть для подписки:",
            reply_markup=reply_markup
        )
        return SELECTING_NETWORK

    async def _handle_network_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle network selection for subscription."""
        network_name = update.message.text
        network = self.db_session.query(Network).filter_by(name=network_name).first()

        if not network:
            await update.message.reply_text(
                "❌ Сеть не найдена",
                reply_markup=ReplyKeyboardRemove()
            )
            return ConversationHandler.END

        # Subscribe chat to network
        from .notifications import NotificationManager
        notification_manager = NotificationManager(self, self.db_session)
        if notification_manager.subscribe_chat(update.effective_chat.id, network.id):
            await update.message.reply_text(
                f"✅ Вы успешно подписались на уведомления для сети {network.name}",
                reply_markup=ReplyKeyboardRemove()
            )
        else:
            await update.message.reply_text(
                f"❌ Не удалось подписаться на уведомления для сети {network.name}",
                reply_markup=ReplyKeyboardRemove()
            )

        return ConversationHandler.END

    async def _cancel_subscription(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cancel subscription process."""
        await update.message.reply_text(
            "Подписка отменена",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END

    async def _unsubscribe_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /unsubscribe command."""
        return await self._handle_command(update, context, self._unsubscribe_handler)

    async def _unsubscribe_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Actual /unsubscribe command implementation."""
        # Get subscribed networks
        from .notifications import NotificationManager
        notification_manager = NotificationManager(self, self.db_session)
        subscriptions = self.db_session.query(Network).join(
            TelegramChat
        ).filter(
            TelegramChat.chat_id == update.effective_chat.id,
            TelegramChat.is_active == True
        ).all()

        if not subscriptions:
            await update.message.reply_text("❌ У вас нет активных подписок")
            return

        # Create keyboard with network names
        keyboard = [[network.name] for network in subscriptions]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

        await update.message.reply_text(
            "Выберите сеть для отписки:",
            reply_markup=reply_markup
        )

    async def _list_subscriptions(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /list command."""
        return await self._handle_command(update, context, self._list_subscriptions_handler)

    async def _list_subscriptions_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Actual /list command implementation."""
        # Get subscribed networks
        subscriptions = self.db_session.query(Network).join(
            TelegramChat
        ).filter(
            TelegramChat.chat_id == update.effective_chat.id,
            TelegramChat.is_active == True
        ).all()

        if not subscriptions:
            await update.message.reply_text("📝 У вас нет активных подписок")
            return

        message = "📝 <b>Ваши подписки:</b>\n\n"
        for network in subscriptions:
            message += f"• {network.name} ({network.ip_range})\n"

        await update.message.reply_text(message, parse_mode='HTML') 