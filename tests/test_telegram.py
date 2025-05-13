"""Tests for Telegram bot and notification system."""

import pytest
from datetime import datetime, timedelta
import json
from unittest.mock import AsyncMock, MagicMock, patch

from telegram import Update, Chat, Message
from telegram.ext import ContextTypes

from clearscan.models import Network, NetworkChange, TelegramChat, ChangeNotification
from clearscan.telegram.bot import ClearScanBot
from clearscan.telegram.notifications import NotificationManager

@pytest.fixture
def mock_update():
    """Create a mock Telegram update."""
    update = MagicMock(spec=Update)
    update.effective_chat = MagicMock(spec=Chat)
    update.effective_chat.id = "123456789"
    update.message = MagicMock(spec=Message)
    update.message.reply_text = AsyncMock()
    return update

@pytest.fixture
def mock_context():
    """Create a mock context."""
    return MagicMock(spec=ContextTypes.DEFAULT_TYPE)

@pytest.fixture
def bot(db_session):
    """Create a ClearScanBot instance."""
    return ClearScanBot(
        token="test_token",
        allowed_chat_ids=["123456789"],
        db_session=db_session
    )

@pytest.fixture
def notification_manager(bot, db_session):
    """Create a NotificationManager instance."""
    return NotificationManager(bot, db_session)

@pytest.fixture
def network(db_session):
    """Create a test network."""
    network = Network(
        name="Test Network",
        ip_range="192.168.1.0/24",
        description="Test network for Telegram notifications",
        is_active=True,
        scan_interval=3600
    )
    db_session.add(network)
    db_session.commit()
    return network

@pytest.fixture
def network_change(db_session, network):
    """Create a test network change."""
    change = NetworkChange(
        network_id=network.id,
        scan_id=1,
        previous_scan_id=1,
        severity="high",
        new_hosts=json.dumps(["192.168.1.100"]),
        removed_hosts=json.dumps(["192.168.1.50"]),
        changed_hosts=json.dumps({
            "192.168.1.1": {
                "new_ports": [443],
                "service_changes": {
                    "443": {"added": "https"}
                }
            }
        })
    )
    db_session.add(change)
    db_session.commit()
    return change

@pytest.mark.asyncio
async def test_bot_access_control(bot, mock_update, mock_context):
    """Test bot access control."""
    # Test with allowed chat
    mock_update.effective_chat.id = "123456789"
    await bot._start_command(mock_update, mock_context)
    mock_update.message.reply_text.assert_called_once()
    assert "У вас нет доступа" not in mock_update.message.reply_text.call_args[0][0]
    
    # Test with disallowed chat
    mock_update.message.reply_text.reset_mock()
    mock_update.effective_chat.id = "987654321"
    await bot._start_command(mock_update, mock_context)
    mock_update.message.reply_text.assert_called_once_with("⛔ У вас нет доступа к этому боту.")

@pytest.mark.asyncio
async def test_bot_commands(bot, mock_update, mock_context):
    """Test bot commands."""
    # Test /start command
    await bot._start_command(mock_update, mock_context)
    assert mock_update.message.reply_text.called
    assert "👋 Добро пожаловать" in mock_update.message.reply_text.call_args[0][0]
    
    # Test /help command
    mock_update.message.reply_text.reset_mock()
    await bot._help_command(mock_update, mock_context)
    assert mock_update.message.reply_text.called
    assert "🔍 <b>Команды ClearScan:</b>" in mock_update.message.reply_text.call_args[0][0]
    
    # Test /status command with no changes
    mock_update.message.reply_text.reset_mock()
    await bot._status_command(mock_update, mock_context)
    assert mock_update.message.reply_text.called
    assert "❓ Сканирование еще не проводилось" in mock_update.message.reply_text.call_args[0][0]

@pytest.mark.asyncio
async def test_subscription_workflow(bot, mock_update, mock_context, network):
    """Test subscription workflow."""
    # Test /subscribe command
    mock_update.message.reply_text.reset_mock()
    result = await bot._subscribe_command(mock_update, mock_context)
    assert result == 1  # SELECTING_NETWORK state
    assert "Выберите сеть для подписки" in mock_update.message.reply_text.call_args[0][0]
    
    # Test network selection
    mock_update.message.reply_text.reset_mock()
    mock_update.message.text = network.name
    result = await bot._handle_network_selection(mock_update, mock_context)
    assert result == -1  # ConversationHandler.END
    assert "✅ Вы успешно подписались" in mock_update.message.reply_text.call_args[0][0]
    
    # Test /list command
    mock_update.message.reply_text.reset_mock()
    await bot._list_subscriptions(mock_update, mock_context)
    assert mock_update.message.reply_text.called
    message = mock_update.message.reply_text.call_args[0][0]
    assert network.name in message
    assert network.ip_range in message

@pytest.mark.asyncio
async def test_notification_sending(notification_manager, network_change):
    """Test notification sending."""
    # Create a notification
    notification = ChangeNotification(
        change_id=network_change.id,
        severity="high",
        message="Test notification"
    )
    
    # Subscribe a chat
    notification_manager.subscribe_chat(123456789, network_change.network_id)
    
    # Test sending notification
    with patch.object(notification_manager.bot, 'send_notification', new_callable=AsyncMock) as mock_send:
        await notification_manager.notify_change(network_change)
        assert mock_send.called
        
        # Check notification format
        call_args = mock_send.call_args
        assert call_args[0][0] == "123456789"  # chat_id
        assert isinstance(call_args[0][1], ChangeNotification)
        assert "🔍 <b>Изменения в сети" in call_args[0][1].message

def test_notification_formatting(notification_manager, network_change):
    """Test notification message formatting."""
    message = notification_manager._format_change_message(network_change)
    
    # Check message structure
    assert "🔍 <b>Изменения в сети" in message
    assert "192.168.1.100" in message  # new host
    assert "192.168.1.50" in message  # removed host
    assert "192.168.1.1" in message  # changed host
    assert "новый сервис на порту 443: https" in message 

@pytest.mark.asyncio
async def test_rate_limiting(bot, mock_update, mock_context):
    """Test bot rate limiting."""
    # Test normal usage within limits
    for _ in range(30):  # Maximum allowed requests
        mock_update.message.reply_text.reset_mock()
        await bot._start_command(mock_update, mock_context)
        assert mock_update.message.reply_text.called
        assert "Превышен лимит запросов" not in mock_update.message.reply_text.call_args[0][0]
    
    # Test exceeding rate limit
    mock_update.message.reply_text.reset_mock()
    await bot._start_command(mock_update, mock_context)
    assert mock_update.message.reply_text.called
    assert "⚠️ Превышен лимит запросов" in mock_update.message.reply_text.call_args[0][0]
    
    # Test rate limit reset after window
    bot._rate_limits[str(mock_update.effective_chat.id)]['window_start'] -= timedelta(minutes=2)
    mock_update.message.reply_text.reset_mock()
    await bot._start_command(mock_update, mock_context)
    assert mock_update.message.reply_text.called
    assert "Превышен лимит запросов" not in mock_update.message.reply_text.call_args[0][0]

@pytest.mark.asyncio
async def test_rate_limit_per_chat(bot, mock_update, mock_context):
    """Test rate limiting is applied per chat."""
    # Use up rate limit for first chat
    for _ in range(31):
        await bot._start_command(mock_update, mock_context)
    
    # Test different chat ID still has its own limit
    mock_update.effective_chat.id = "987654321"
    mock_update.message.reply_text.reset_mock()
    await bot._start_command(mock_update, mock_context)
    assert mock_update.message.reply_text.called
    assert "⛔ У вас нет доступа к этому боту." in mock_update.message.reply_text.call_args[0][0]  # Should fail due to access control, not rate limit 