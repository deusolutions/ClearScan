"""
ClearScan - Network Monitoring Tool
Main entry point for the application
"""

import asyncio
import logging
import signal
import sys
from argparse import ArgumentParser
import yaml
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .scanner import NetworkScanner
from .telegram import TelegramBot

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_config():
    """Загрузка конфигурации."""
    try:
        with open('config.yaml', 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Ошибка загрузки конфигурации: {e}")
        sys.exit(1)

async def main():
    """Основная функция приложения."""
    parser = ArgumentParser(description='ClearScan - Network Monitoring Tool')
    parser.add_argument('--config', default='config.yaml', help='Путь к файлу конфигурации')
    args = parser.parse_args()

    # Загрузка конфигурации
    config = load_config()
    
    # Инициализация базы данных
    engine = create_engine(config['database']['url'])
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Инициализация сканера
        scanner = NetworkScanner(
            session,
            batch_size=config['scanner']['batch_size'],
            timeout=config['scanner']['timeout']
        )

        # Инициализация Telegram бота если включен
        bot = None
        if config['notifications']['telegram']['enabled']:
            bot = TelegramBot(
                token=config['notifications']['telegram']['bot_token'],
                allowed_chat_id=config['notifications']['telegram']['chat_id'],
                db_session=session
            )
            await bot.start()

        # Запуск основного цикла сканирования
        while True:
            try:
                # Сканирование сети
                changes = await scanner.scan_all_networks()
                
                # Отправка уведомлений если есть изменения
                if changes and bot:
                    for change in changes:
                        await bot.send_notification(
                            message=change.message,
                            severity=change.severity
                        )
                
                # Ожидание следующего цикла
                await asyncio.sleep(config['scanner']['scan_interval'])
                
            except Exception as e:
                logger.error(f"Ошибка в цикле сканирования: {e}")
                await asyncio.sleep(60)  # Пауза перед повторной попыткой

    except KeyboardInterrupt:
        logger.info("Получен сигнал завершения")
    finally:
        if bot:
            await bot.stop()
        session.close()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Программа остановлена пользователем")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        sys.exit(1) 