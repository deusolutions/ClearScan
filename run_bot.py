#!/usr/bin/env python3
"""
Скрипт запуска Telegram бота ClearScan
"""

import asyncio
import logging
import yaml
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from clearscan.telegram import TelegramBot

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_config():
    """Загрузка конфигурации из файла."""
    try:
        with open('config.yaml', 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Ошибка загрузки конфигурации: {e}")
        raise

async def main():
    """Основная функция запуска бота."""
    try:
        # Загрузка конфигурации
        config = load_config()
        
        # Подключение к базе данных
        engine = create_engine(config['database']['url'])
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Создание и запуск бота
        bot = TelegramBot(
            token=config['notifications']['telegram']['bot_token'],
            allowed_chat_id=config['notifications']['telegram']['chat_id'],
            db_session=session
        )
        
        logger.info("Запуск Telegram бота...")
        await bot.start()
        
    except Exception as e:
        logger.error(f"Ошибка запуска бота: {e}")
        raise
    finally:
        session.close()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        exit(1) 