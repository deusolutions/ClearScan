"""
Telegram Notifications Module

This module handles notification management and delivery for the Telegram bot.
"""

from typing import List, Dict, Optional
from datetime import datetime
import asyncio
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
                await self.bot.send_notification(chat.chat_id, notification)
                self.logger.info(f"Notification sent to chat {chat.chat_id}")
            except Exception as e:
                self.logger.error(f"Failed to send notification to chat {chat.chat_id}: {e}")
                
    def _format_change_message(self, change: NetworkChange) -> str:
        """Format change details into a human-readable message."""
        network = self.db_session.query(Network).get(change.network_id)
        
        message_parts = [
            f"Network: {network.name} ({network.ip_range})",
            f"Scan Time: {change.timestamp}",
            ""
        ]
        
        # Add change details
        if change.new_hosts:
            message_parts.extend([
                "🆕 New Hosts:",
                ", ".join(sorted(change.new_hosts)),
                ""
            ])
            
        if change.removed_hosts:
            message_parts.extend([
                "❌ Removed Hosts:",
                ", ".join(sorted(change.removed_hosts)),
                ""
            ])
            
        if change.changed_hosts:
            message_parts.append("📝 Changed Hosts:")
            for host, details in sorted(change.changed_hosts.items()):
                changes = []
                if 'new_ports' in details:
                    changes.append(f"New ports: {', '.join(map(str, sorted(details['new_ports'])))}")
                if 'closed_ports' in details:
                    changes.append(f"Closed ports: {', '.join(map(str, sorted(details['closed_ports'])))}")
                if 'service_changes' in details:
                    for port, service_change in sorted(details['service_changes'].items()):
                        if 'added' in service_change:
                            changes.append(f"New service on port {port}: {service_change['added']}")
                        elif 'removed' in service_change:
                            changes.append(f"Removed service on port {port}: {service_change['removed']}")
                        else:
                            changes.append(
                                f"Service changed on port {port}: "
                                f"{service_change['old']} → {service_change['new']}"
                            )
                message_parts.extend([f"  {host}:", "    - " + "\n    - ".join(changes), ""])
                
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
        
        # Get all active chats
        chats = self.db_session.query(TelegramChat).filter_by(is_active=True).all()
        
        # Send notifications
        for chat in chats:
            try:
                await self.bot.send_notification(chat.chat_id, notification)
                self.logger.info(f"System notification sent to chat {chat.chat_id}")
            except Exception as e:
                self.logger.error(f"Failed to send system notification to chat {chat.chat_id}: {e}")
                
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
            chat = TelegramChat(
                chat_id=chat_id,
                network_id=network_id,
                is_active=True
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
                network_id=network_id
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