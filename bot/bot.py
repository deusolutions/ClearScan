"""
Telegram-бот для отправки уведомлений об изменениях.
Интегрируется с модулем diff для отслеживания изменений.
"""
from typing import List, Dict, Any
from datetime import datetime

def format_notification(changes: List[Dict[str, Any]]) -> str:
    """
    Форматирует список изменений в читаемое сообщение.
    """
    if not changes:
        return "Изменений не обнаружено"

    message = "🔔 Обнаружены изменения в сети:\n\n"
    
    for change in changes:
        message += f"📍 {change['ip']}:{change['port']}\n"
        message += f"   Старый статус: {change['old_status']}\n"
        message += f"   Новый статус: {change['new_status']}\n"
        message += "---\n"
    
    return message

def send_telegram_message(message: str) -> bool:
    """
    Отправляет сообщение в Telegram.
    В текущей версии просто имитирует отправку.
    """
    print("\n[Telegram] Отправка сообщения:")
    print(message)
    return True

def send_notification(changes: List[Dict[str, Any]]) -> bool:
    """
    Отправляет уведомление об изменениях.
    """
    message = format_notification(changes)
    return send_telegram_message(message) 