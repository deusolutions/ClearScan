"""
Telegram Notifications Module

This module handles notification management and delivery for the Telegram bot.
"""

from typing import List, Dict, Optional
from datetime import datetime
import asyncio
import json
import logging
from sqlalchemy.orm import Session
from ..models import Network, NetworkChange, ChangeNotification, TelegramChat
from .bot import ClearScanBot

class NotificationManager:
    def __init__(self, bot: ClearScanBot, db_session: Session):
        """
        Initialize the notification manager.
        
        Args:
            bot: ClearScanBot instance
            db_session: SQLAlchemy database session
        """
        self.bot = bot
        self.db_session = db_session
        self.logger = logging.getLogger(__name__)
        
    async def notify_change(self, change: NetworkChange):
        """
        Send notifications about network changes to all subscribed chats.
        
        Args:
            change: NetworkChange instance containing the changes to notify about
        """
        notification = ChangeNotification(
            change_id=change.id,
            severity=change.severity,
            timestamp=datetime.utcnow(),
            message=self._format_change_message(change)
        )
        self.db_session.add(notification)
        
        # Get all subscribed chats
        chats = self.db_session.query(TelegramChat).filter_by(
            network_id=change.network_id,
            is_active=True
        ).all()
        
        # Send notifications
        for chat in chats:
            try:
                await self.bot.send_notification(str(chat.chat_id), notification)
                chat.last_notification = datetime.utcnow()
                self.logger.info(f"Notification sent to chat {chat.chat_id}")
            except Exception as e:
                self.logger.error(f"Failed to send notification to chat {chat.chat_id}: {e}")
                
        self.db_session.commit()
                
    def _format_change_message(self, change: NetworkChange) -> str:
        """Format change details into a human-readable message."""
        network = self.db_session.get(Network, change.network_id)
        
        message_parts = [
            f"🔍 <b>Изменения в сети {network.name}</b>",
            f"IP диапазон: {network.ip_range}",
            f"Время сканирования: {change.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            ""
        ]
        
        # Add change details
        new_hosts = json.loads(change.new_hosts)
        removed_hosts = json.loads(change.removed_hosts)
        changed_hosts = json.loads(change.changed_hosts)
        
        # Add summary counts
        total_changes = len(new_hosts) + len(removed_hosts) + len(changed_hosts)
        message_parts.append(f"Всего изменений: {total_changes}")
        
        if new_hosts:
            message_parts.extend([
                "",
                "🆕 <b>Новые хосты:</b>",
                ", ".join(sorted(new_hosts))
            ])
            
        if removed_hosts:
            message_parts.extend([
                "",
                "❌ <b>Недоступные хосты:</b>",
                ", ".join(sorted(removed_hosts))
            ])
            
        if changed_hosts:
            message_parts.extend([
                "",
                "📝 <b>Измененные хосты:</b>"
            ])
            for host, details in sorted(changed_hosts.items()):
                changes = []
                if 'new_ports' in details:
                    changes.append(f"новые порты: {', '.join(map(str, sorted(details['new_ports'])))}")
                if 'closed_ports' in details:
                    changes.append(f"закрытые порты: {', '.join(map(str, sorted(details['closed_ports'])))}")
                if 'service_changes' in details:
                    for port, service_change in sorted(details['service_changes'].items()):
                        if 'added' in service_change:
                            changes.append(f"новый сервис на порту {port}: {service_change['added']}")
                        elif 'removed' in service_change:
                            changes.append(f"удален сервис на порту {port}: {service_change['removed']}")
                        else:
                            changes.append(
                                f"изменен сервис на порту {port}: "
                                f"{service_change['old']} → {service_change['new']}"
                            )
                message_parts.extend([
                    f"\n<b>{host}:</b>",
                    "• " + "\n• ".join(changes)
                ])
                
        return "\n".join(message_parts)
        
    async def send_system_notification(self, message: str, severity: str = 'info'):
        """
        Send a system notification to all active chats.
        
        Args:
            message: Notification message
            severity: Notification severity level
        """
        notification = ChangeNotification(
            severity=severity,
            timestamp=datetime.utcnow(),
            message=message
        )
        self.db_session.add(notification)
        
        # Get all active chats
        chats = self.db_session.query(TelegramChat).filter_by(is_active=True).all()
        
        # Send notifications
        for chat in chats:
            try:
                await self.bot.send_notification(str(chat.chat_id), notification)
                chat.last_notification = datetime.utcnow()
                self.logger.info(f"System notification sent to chat {chat.chat_id}")
            except Exception as e:
                self.logger.error(f"Failed to send system notification to chat {chat.chat_id}: {e}")
                
        self.db_session.commit()
                
    def subscribe_chat(self, chat_id: int, network_id: int) -> bool:
        """
        Subscribe a chat to notifications for a specific network.
        
        Args:
            chat_id: Telegram chat ID
            network_id: Network ID to subscribe to
            
        Returns:
            bool: True if subscription was successful, False otherwise
        """
        try:
            # Check if subscription already exists
            existing = self.db_session.query(TelegramChat).filter_by(
                chat_id=chat_id,
                network_id=network_id
            ).first()
            
            if existing:
                if existing.is_active:
                    return True  # Already subscribed
                else:
                    existing.is_active = True
                    existing.created_at = datetime.utcnow()
            else:
                chat = TelegramChat(
                    chat_id=chat_id,
                    network_id=network_id,
                    is_active=True,
                    created_at=datetime.utcnow()
                )
                self.db_session.add(chat)
                
            self.db_session.commit()
            return True
        except Exception as e:
            self.logger.error(f"Failed to subscribe chat {chat_id} to network {network_id}: {e}")
            self.db_session.rollback()
            return False
            
    def unsubscribe_chat(self, chat_id: int, network_id: int) -> bool:
        """
        Unsubscribe a chat from notifications for a specific network.
        
        Args:
            chat_id: Telegram chat ID
            network_id: Network ID to unsubscribe from
            
        Returns:
            bool: True if unsubscription was successful, False otherwise
        """
        try:
            chat = self.db_session.query(TelegramChat).filter_by(
                chat_id=chat_id,
                network_id=network_id,
                is_active=True
            ).first()
            
            if chat:
                chat.is_active = False
                self.db_session.commit()
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to unsubscribe chat {chat_id} from network {network_id}: {e}")
            self.db_session.rollback()
            return False

    async def process_pending_notifications(self):
        """Process all pending notifications."""
        try:
            # Get all pending notifications
            pending = self.db_session.query(ChangeNotification).filter_by(
                status='pending'
            ).order_by(ChangeNotification.timestamp.asc()).all()

            for notification in pending:
                try:
                    # Get all active chats for the network
                    if notification.change:
                        chats = self.db_session.query(TelegramChat).filter_by(
                            network_id=notification.change.network_id,
                            is_active=True
                        ).all()
                    else:
                        # For system notifications, get all active chats
                        chats = self.db_session.query(TelegramChat).filter_by(
                            is_active=True
                        ).all()

                    # Send notification to each chat
                    for chat in chats:
                        try:
                            success = await self.bot.send_notification(
                                str(chat.chat_id),
                                notification
                            )
                            if success:
                                chat.last_notification = datetime.utcnow()
                                self.logger.info(f"Notification sent to chat {chat.chat_id}")
                            else:
                                self.logger.error(f"Failed to send notification to chat {chat.chat_id}")
                        except Exception as e:
                            self.logger.error(f"Error sending notification to chat {chat.chat_id}: {e}")

                    # Update notification status
                    notification.status = 'sent'
                    self.db_session.commit()

                except Exception as e:
                    self.logger.error(f"Error processing notification {notification.id}: {e}")
                    notification.status = 'failed'
                    notification.error_message = str(e)
                    self.db_session.commit()

        except Exception as e:
            self.logger.error(f"Error processing pending notifications: {e}")
            self.db_session.rollback() 