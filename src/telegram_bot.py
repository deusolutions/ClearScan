"""
telegram_bot.py - Telegram-бот для ClearScan
"""
import logging
from telegram import Update, Bot
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)
import sqlite3
import os
import sys

# Добавляем путь к src в PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.config import DATABASE_PATH, ALLOWED_USERS, TELEGRAM_TOKEN

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/clearscan/telegram_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('telegram_bot')


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    username = update.effective_user.username
    logger.info(f"Пользователь {username} (ID: {user_id}) запустил бота")
    
    if user_id not in ALLOWED_USERS:
        logger.warning(f"Попытка доступа от неавторизованного пользователя {username} (ID: {user_id})")
        await update.message.reply_text("Извините, у вас нет доступа к этому боту.")
        return

    await update.message.reply_text(
        "Привет! Я бот для мониторинга сканирования портов.\n"
        "Доступные команды:\n"
        "/status - показать текущий статус сканирования\n"
        "/history - показать историю изменений\n"
        "/help - показать это сообщение"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    username = update.effective_user.username
    logger.info(f"Пользователь {username} (ID: {user_id}) запросил помощь")
    
    if user_id not in ALLOWED_USERS:
        logger.warning(f"Попытка доступа к help от неавторизованного пользователя {username} (ID: {user_id})")
        await update.message.reply_text("Извините, у вас нет доступа к этому боту.")
        return

    await update.message.reply_text(
        "Доступные команды:\n"
        "/status - показать текущий статус сканирования\n"
        "/history - показать историю изменений\n"
        "/help - показать это сообщение"
    )


async def get_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    username = update.effective_user.username
    logger.info(f"Пользователь {username} (ID: {user_id}) запросил статус")
    
    if user_id not in ALLOWED_USERS:
        logger.warning(f"Попытка доступа к статусу от неавторизованного пользователя {username} (ID: {user_id})")
        await update.message.reply_text("Извините, у вас нет доступа к этому боту.")
        return

    try:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        
        # Получаем последние результаты сканирования
        c.execute(
            "SELECT ip, port, status, scan_time FROM scan_results "
            "ORDER BY scan_time DESC LIMIT 10"
        )
        results = c.fetchall()
        
        if not results:
            logger.info("Нет данных о сканировании")
            await update.message.reply_text("Нет данных о сканировании.")
            return

        message = "Последние результаты сканирования:\n\n"
        for ip, port, status, scan_time in results:
            message += f"IP: {ip}\nПорт: {port}\nСтатус: {status}\nВремя: {scan_time}\n\n"
        
        logger.info(f"Отправлено {len(results)} результатов сканирования")
        await update.message.reply_text(message)
        
    except sqlite3.Error as e:
        logger.error(f"Ошибка базы данных при получении статуса: {str(e)}", exc_info=True)
        await update.message.reply_text("Произошла ошибка при получении данных.")
    except Exception as e:
        logger.error(f"Неожиданная ошибка при получении статуса: {str(e)}", exc_info=True)
        await update.message.reply_text("Произошла внутренняя ошибка.")
    finally:
        if 'conn' in locals():
            conn.close()


async def get_history(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    username = update.effective_user.username
    logger.info(f"Пользователь {username} (ID: {user_id}) запросил историю")
    
    if user_id not in ALLOWED_USERS:
        logger.warning(f"Попытка доступа к истории от неавторизованного пользователя {username} (ID: {user_id})")
        await update.message.reply_text("Извините, у вас нет доступа к этому боту.")
        return

    try:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        
        # Получаем последние изменения
        c.execute(
            "SELECT change_type, ip, port, status, change_time FROM scan_history "
            "ORDER BY change_time DESC LIMIT 10"
        )
        changes = c.fetchall()
        
        if not changes:
            logger.info("Нет данных об изменениях")
            await update.message.reply_text("Нет данных об изменениях.")
            return

        message = "Последние изменения:\n\n"
        for change_type, ip, port, status, change_time in changes:
            message += f"Тип: {change_type}\nIP: {ip}\nПорт: {port}\nСтатус: {status}\nВремя: {change_time}\n\n"
        
        logger.info(f"Отправлено {len(changes)} записей истории")
        await update.message.reply_text(message)
        
    except sqlite3.Error as e:
        logger.error(f"Ошибка базы данных при получении истории: {str(e)}", exc_info=True)
        await update.message.reply_text("Произошла ошибка при получении данных.")
    except Exception as e:
        logger.error(f"Неожиданная ошибка при получении истории: {str(e)}", exc_info=True)
        await update.message.reply_text("Произошла внутренняя ошибка.")
    finally:
        if 'conn' in locals():
            conn.close()


def send_port_changes(token, chat_id, added, removed):
    """
    Отправляет уведомление о новых/закрытых портах.
    """
    bot = Bot(token)
    msg = ""
    if added:
        msg += (
            "🟢 Новые доступы:\n" +
            "\n".join([
                f"{ip}:{port} {status}" for ip, port, status in added
            ]) + "\n"
        )
    if removed:
        msg += (
            "🔴 Пропавшие доступы:\n" +
            "\n".join([
                f"{ip}:{port} {status}" for ip, port, status in removed
            ])
        )
    if not msg:
        msg = "Изменений не обнаружено."
    bot.send_message(chat_id=chat_id, text=msg)


def main() -> None:
    logger.info("Запуск телеграм бота")
    
    # Создаем приложение
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Добавляем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", get_status))
    application.add_handler(CommandHandler("history", get_history))

    # Запускаем бота
    logger.info("Бот запущен и готов к работе")
    application.run_polling()


if __name__ == "__main__":
    main()
