"""
telegram_bot.py - Telegram-бот для ClearScan
"""
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import sqlite3
from src.config import DATABASE_PATH

# Разрешённые пользователи (ID)
ALLOWED_USERS = {123456789}  # Замените на свои Telegram user_id


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ALLOWED_USERS:
        await update.message.reply_text("Access denied.")
        return
    await update.message.reply_text(
        "ClearScan Bot: используйте /status или /changes."
    )


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ALLOWED_USERS:
        await update.message.reply_text("Access denied.")
        return
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT ip, port, status, scan_time FROM scan_results "
        "ORDER BY scan_time DESC LIMIT 10"
    )
    rows = c.fetchall()
    conn.close()
    if not rows:
        await update.message.reply_text("Нет данных о сканировании.")
        return
    msg = "Последние результаты:\n"
    for ip, port, status, scan_time in rows:
        msg += f"{ip}:{port} {status} ({scan_time})\n"
    await update.message.reply_text(msg)


async def changes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ALLOWED_USERS:
        await update.message.reply_text("Access denied.")
        return
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT change_type, ip, port, status, change_time FROM scan_history "
        "ORDER BY change_time DESC LIMIT 10"
    )
    rows = c.fetchall()
    conn.close()
    if not rows:
        await update.message.reply_text("Нет изменений.")
        return
    msg = "Последние изменения:\n"
    for change_type, ip, port, status, change_time in rows:
        emoji = "🟢" if change_type == "opened" else "🔴"
        msg += f"{emoji} {ip}:{port} {status} ({change_time})\n"
    await update.message.reply_text(msg)


def send_port_changes(token, chat_id, added, removed):
    """
    Отправляет уведомление о новых/закрытых портах.
    """
    from telegram import Bot
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


if __name__ == "__main__":
    import src.config as config
    import asyncio
    app = ApplicationBuilder().token(config.TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("changes", changes))
    print("ClearScan Telegram Bot запущен.")
    asyncio.run(app.run_polling())
