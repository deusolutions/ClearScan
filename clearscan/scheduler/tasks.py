"""
Predefined tasks for ClearScan scheduler.

This module contains task definitions for:
- Network scanning
- Result comparison
- Notification delivery
"""

import logging
from typing import Optional
from sqlalchemy.orm import Session
from datetime import datetime

from ..models import Network
from ..scanner import NetworkScanner
from ..comparator import ResultsComparator
from ..telegram.notifications import NotificationManager

logger = logging.getLogger(__name__)

class ScanTask:
    """Network scanning task."""
    
    def __init__(self, db_session: Session, network_id: int):
        """
        Initialize scanning task.
        
        Args:
            db_session: Database session
            network_id: ID of network to scan
        """
        self.db_session = db_session
        self.network_id = network_id
        self.scanner = NetworkScanner(db_session)
        self.comparator = ResultsComparator(db_session)
        
    async def __call__(self) -> None:
        """Execute the scanning task."""
        network = self.db_session.get(Network, self.network_id)
        if not network or not network.is_active:
            logger.warning(f"Network {self.network_id} not found or inactive")
            return
            
        logger.info(f"Starting scan for network {network.name} ({network.ip_range})")
        
        # Perform scan
        scan_id = await self.scanner.scan_network(
            network.ip_range,
            network.id
        )
        
        if not scan_id:
            logger.error(f"Scan failed for network {network.name}")
            return
            
        # Compare results
        changes = await self.comparator.compare_with_previous(
            network.id,
            scan_id
        )
        
        if changes:
            logger.info(f"Found {len(changes)} changes in network {network.name}")
        else:
            logger.info(f"No changes detected in network {network.name}")
            
class NotificationTask:
    """Notification delivery task."""
    
    def __init__(self, db_session: Session, bot, notification_manager: Optional[NotificationManager] = None):
        """
        Initialize notification task.
        
        Args:
            db_session: Database session
            bot: Telegram bot instance
            notification_manager: Optional notification manager instance
        """
        self.db_session = db_session
        self.notification_manager = notification_manager or NotificationManager(bot, db_session)
        
    async def __call__(self) -> None:
        """Execute the notification task."""
        # Process pending notifications
        await self.notification_manager.process_pending_notifications()
        
def create_scan_task(db_session: Session, network_id: int) -> ScanTask:
    """Create a network scanning task."""
    return ScanTask(db_session, network_id)
    
def create_notification_task(db_session: Session, bot) -> NotificationTask:
    """Create a notification delivery task."""
    return NotificationTask(db_session, bot) 