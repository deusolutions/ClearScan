"""
comparator.py - модуль для сравнения результатов сканирования и фиксации
изменений в истории
"""

import sqlite3
import datetime
from src.config import DATABASE_PATH


def get_last_scan_id(conn):
    c = conn.cursor()
    c.execute(
        "SELECT scan_id FROM scan_results ORDER BY scan_time DESC LIMIT 1"
    )
    row = c.fetchone()
    return row[0] if row else None


def get_scan_results(conn, scan_id):
    c = conn.cursor()
    c.execute(
        "SELECT ip, port, status FROM scan_results WHERE scan_id = ?",
        (scan_id,)
    )
    return set(c.fetchall())


def compare_scans(old, new):
    """
    Сравнивает два множества (ip, port, status).
    Возвращает (added, removed):
    - added: новые открытые порты
    - removed: закрытые порты
    """
    added = new - old
    removed = old - new
    return list(added), list(removed)


def save_changes_to_history(conn, scan_id, added, removed):
    """
    Сохраняет изменения в таблицу scan_history.
    Формат: scan_id, change_time, change_type, ip, port, status
    """
    c = conn.cursor()
    now = datetime.datetime.now().isoformat()
    for ip, port, status in added:
        c.execute(
            """
            INSERT INTO scan_history (
                scan_id, change_time, change_type, ip, port, status
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (scan_id, now, 'opened', ip, port, status)
        )
    for ip, port, status in removed:
        c.execute(
            """
            INSERT INTO scan_history (
                scan_id, change_time, change_type, ip, port, status
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (scan_id, now, 'closed', ip, port, status)
        )
    conn.commit()


def ensure_history_table():
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute(
        '''
        CREATE TABLE IF NOT EXISTS scan_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scan_id TEXT NOT NULL,
            change_time DATETIME NOT NULL,
            change_type TEXT NOT NULL,
            ip TEXT NOT NULL,
            port INTEGER NOT NULL,
            status TEXT NOT NULL
        )
        '''
    )
    conn.commit()
    conn.close()


if __name__ == "__main__":
    ensure_history_table()
    conn = sqlite3.connect(DATABASE_PATH)
    last_scan_id = get_last_scan_id(conn)
    prev_scan_id = None
    # Получить предыдущий scan_id (до последнего)
    c = conn.cursor()
    c.execute(
        "SELECT scan_id FROM scan_results ORDER BY scan_time DESC LIMIT 2"
    )
    rows = c.fetchall()
    if len(rows) == 2:
        prev_scan_id = rows[1][0]
    if last_scan_id and prev_scan_id:
        old = get_scan_results(conn, prev_scan_id)
        new = get_scan_results(conn, last_scan_id)
        added, removed = compare_scans(old, new)
        save_changes_to_history(conn, last_scan_id, added, removed)
    conn.close()
