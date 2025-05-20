import pytest
from unittest.mock import AsyncMock, MagicMock
from src import telegram_bot

class DummyUser:
    def __init__(self, id):
        self.id = id
class DummyMessage:
    def __init__(self):
        self.text = None
        self.reply_text = AsyncMock()
class DummyUpdate:
    def __init__(self, user_id):
        self.effective_user = DummyUser(user_id)
        self.message = DummyMessage()

@pytest.mark.asyncio
async def test_start_access():
    update = DummyUpdate(123456789)  # Разрешённый ID
    context = MagicMock()
    await telegram_bot.start(update, context)
    update.message.reply_text.assert_called_with("ClearScan Bot: используйте /status или /changes.")

@pytest.mark.asyncio
async def test_start_denied():
    update = DummyUpdate(111)
    context = MagicMock()
    await telegram_bot.start(update, context)
    update.message.reply_text.assert_called_with("Access denied.")
