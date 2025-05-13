"""Tests for Telegram bot functionality."""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from telegram import Update
from telegram.ext import ContextTypes
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from clearscan.models import Base, Network, NetworkChange, ChangeNotification, TelegramChat
from clearscan.telegram.bot import ClearScanBot
from clearscan.telegram.notifications import NotificationManager

@pytest.fixture
def db_engine():
    """Create a test database."""
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    return engine

@pytest.fixture
def db_session(db_engine):
    """Create a new database session for a test."""
    Session = sessionmaker(bind=db_engine)
    session = Session()
    yield session
    session.rollback()
    session.close()

@pytest.fixture
def bot(db_session):
    """Create a test bot instance."""
    return ClearScanBot("test_token", db_session)

@pytest.fixture
def notification_manager(bot, db_session):
    """Create a test notification manager instance."""
    return NotificationManager(bot, db_session)

@pytest.fixture
def network(db_session):
    """Create a test network."""
    network = Network(
        name="Test Network",
        ip_range="192.168.1.0/24",
        scan_interval=3600
    )
    db_session.add(network)
    db_session.commit()
    return network

@pytest.fixture
def telegram_chat(db_session, network):
    """Create a test Telegram chat."""
    chat = TelegramChat(
        chat_id=123456789,
        network_id=network.id,
        is_active=True
    )
    db_session.add(chat)
    db_session.commit()
    return chat

@pytest.fixture
def network_change(db_session, network):
    """Create a test network change."""
    change = NetworkChange(
        network_id=network.id,
        scan_id=1,
        previous_scan_id=1,
        timestamp=datetime.utcnow(),
        new_hosts=['192.168.1.100'],
        removed_hosts=['192.168.1.50'],
        changed_hosts={
            '192.168.1.1': {
                'new_ports': [443],
                'service_changes': {
                    '443': {'added': 'https'}
                }
            }
        },
        severity='medium'
    )
    db_session.add(change)
    db_session.commit()
    return change

async def test_start_command(bot):
    """Test the /start command."""
    update = MagicMock(spec=Update)
    update.message.reply_text = AsyncMock()
    context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
    
    await bot._start_command(update, context)
    
    update.message.reply_text.assert_called_once()
    call_args = update.message.reply_text.call_args[0][0]
    assert "Welcome to ClearScan Bot!" in call_args
    assert "/help" in call_args
    assert "/status" in call_args
    assert "/networks" in call_args
    assert "/scan" in call_args

async def test_help_command(bot):
    """Test the /help command."""
    update = MagicMock(spec=Update)
    update.message.reply_text = AsyncMock()
    context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
    
    await bot._help_command(update, context)
    
    update.message.reply_text.assert_called_once()
    call_args = update.message.reply_text.call_args[0][0]
    assert "ClearScan Bot Help" in call_args
    assert all(cmd in call_args for cmd in ["/start", "/help", "/status", "/networks", "/scan"])

async def test_status_command(bot, network, db_session):
    """Test the /status command."""
    update = MagicMock(spec=Update)
    update.message.reply_text = AsyncMock()
    context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
    
    await bot._status_command(update, context)
    
    update.message.reply_text.assert_called_once()
    call_args = update.message.reply_text.call_args[0][0]
    assert "ClearScan Status" in call_args
    assert "Monitored Networks: 1" in call_args
    assert "Operational" in call_args

async def test_list_networks_command(bot, network, db_session):
    """Test the /networks command."""
    update = MagicMock(spec=Update)
    update.message.reply_text = AsyncMock()
    context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
    
    await bot._list_networks(update, context)
    
    update.message.reply_text.assert_called_once()
    call_args = update.message.reply_text.call_args[0][0]
    assert "Test Network" in call_args
    assert "192.168.1.0/24" in call_args

async def test_start_scan_command_with_valid_network(bot, network, db_session):
    """Test the /scan command with a valid network name."""
    update = MagicMock(spec=Update)
    update.message.reply_text = AsyncMock()
    context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
    context.args = ["Test", "Network"]
    
    await bot._start_scan(update, context)
    
    update.message.reply_text.assert_called_once()
    call_args = update.message.reply_text.call_args[0][0]
    assert "Starting scan for network 'Test Network'" in call_args

async def test_start_scan_command_with_invalid_network(bot, db_session):
    """Test the /scan command with an invalid network name."""
    update = MagicMock(spec=Update)
    update.message.reply_text = AsyncMock()
    context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
    context.args = ["Invalid", "Network"]
    
    await bot._start_scan(update, context)
    
    update.message.reply_text.assert_called_once()
    call_args = update.message.reply_text.call_args[0][0]
    assert "Network 'Invalid Network' not found" in call_args

async def test_notification_sending(notification_manager, network_change, telegram_chat):
    """Test sending notifications about network changes."""
    with patch('clearscan.telegram.bot.ClearScanBot.send_notification') as mock_send:
        mock_send.return_value = None
        
        await notification_manager.notify_change(network_change)
        
        mock_send.assert_called_once()
        chat_id, notification = mock_send.call_args[0]
        assert chat_id == telegram_chat.chat_id
        assert notification.severity == network_change.severity
        assert "New Hosts" in notification.message
        assert "192.168.1.100" in notification.message
        assert "Removed Hosts" in notification.message
        assert "192.168.1.50" in notification.message
        assert "Changed Hosts" in notification.message
        assert "192.168.1.1" in notification.message

def test_subscribe_chat(notification_manager, network):
    """Test subscribing a chat to network notifications."""
    chat_id = 987654321
    
    success = notification_manager.subscribe_chat(chat_id, network.id)
    assert success
    
    chat = notification_manager.db_session.query(TelegramChat).filter_by(
        chat_id=chat_id,
        network_id=network.id
    ).first()
    assert chat is not None
    assert chat.is_active

def test_unsubscribe_chat(notification_manager, telegram_chat):
    """Test unsubscribing a chat from network notifications."""
    success = notification_manager.unsubscribe_chat(
        telegram_chat.chat_id,
        telegram_chat.network_id
    )
    assert success
    
    chat = notification_manager.db_session.query(TelegramChat).filter_by(
        id=telegram_chat.id
    ).first()
    assert chat is not None
    assert not chat.is_active 