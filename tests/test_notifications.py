import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime

class TestNotifications(unittest.TestCase):
    def setUp(self):
        self.changes = [
            {
                'timestamp': datetime.now(),
                'ip': '127.0.0.1',
                'port': 80,
                'old_status': 'open',
                'new_status': 'closed'
            },
            {
                'timestamp': datetime.now(),
                'ip': '127.0.0.1',
                'port': 443,
                'old_status': 'closed',
                'new_status': 'open'
            }
        ]

    @patch('bot.bot.send_telegram_message')
    def test_notification_format(self, mock_send):
        """Тест форматирования уведомлений"""
        from bot.bot import format_notification
        
        # Форматируем уведомление
        message = format_notification(self.changes)
        
        # Проверяем формат
        self.assertIn('127.0.0.1', message)
        self.assertIn('80', message)
        self.assertIn('443', message)
        self.assertIn('open', message)
        self.assertIn('closed', message)
        
        print("\nФормат уведомления:")
        print(message)

    @patch('bot.bot.send_telegram_message')
    def test_notification_sending(self, mock_send):
        """Тест отправки уведомлений"""
        from bot.bot import send_notification
        
        # Отправляем уведомление
        send_notification(self.changes)
        
        # Проверяем, что функция отправки была вызвана
        self.assertTrue(mock_send.called)
        
        # Проверяем, что сообщение содержит нужную информацию
        message = mock_send.call_args[0][0]
        self.assertIn('127.0.0.1', message)
        self.assertIn('80', message)
        self.assertIn('443', message)

if __name__ == '__main__':
    unittest.main() 