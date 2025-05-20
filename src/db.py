import sqlite3
import logging
from logging.handlers import RotatingFileHandler
import os

DB_PATH = "clearscan.db"
LOG_PATH = '/var/log/clearscan.log'
LOG_MAX_BYTES = 10 * 1024 * 1024  # 10 MB
LOG_BACKUP_COUNT = 3


def setup_logger():
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    logger = logging.getLogger('clearscan')
    logger.setLevel(logging.INFO)
    handler = RotatingFileHandler(
        LOG_PATH, maxBytes=LOG_MAX_BYTES, backupCount=LOG_BACKUP_COUNT
    )
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s %(module)s: %(message)s'
    )
    handler.setFormatter(formatter)
    if not logger.hasHandlers():
        logger.addHandler(handler)
    return logger


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Таблица с последними результатами сканирования
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS scan_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip TEXT NOT NULL,
            port INTEGER NOT NULL,
            protocol TEXT NOT NULL,
            state TEXT NOT NULL,
            service TEXT,
            scan_time DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    # История сканирований (для сравнения)
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS scan_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip TEXT NOT NULL,
            port INTEGER NOT NULL,
            protocol TEXT NOT NULL,
            state TEXT NOT NULL,
            service TEXT,
            scan_time DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    conn.close()


def insert_scan_result(conn, ip, port, protocol, state, service):
    c = conn.cursor()
    c.execute(
        """
        INSERT INTO scan_results (ip, port, protocol, state, service)
        VALUES (?, ?, ?, ?, ?)
        """,
        (ip, port, protocol, state, service)
    )
    conn.commit()


def insert_scan_history(conn, ip, port, protocol, state, service):
    c = conn.cursor()
    c.execute(
        """
        INSERT INTO scan_history (ip, port, protocol, state, service)
        VALUES (?, ?, ?, ?, ?)
        """,
        (ip, port, protocol, state, service)
    )
    conn.commit()


def fetch_last_scan(conn):
    c = conn.cursor()
    c.execute(
        """
        SELECT ip, port, protocol, state, service FROM scan_results
        """
    )
    return c.fetchall()


def fetch_scan_history(conn, limit=10):
    c = conn.cursor()
    c.execute(
        """
        SELECT ip, port, protocol, state, service, scan_time FROM scan_history
        ORDER BY scan_time DESC LIMIT ?
        """,
        (limit,)
    )
    return c.fetchall()


def compare_scans(old_scan, new_scan):
    """
    Сравнивает два списка результатов сканирования.
    Возвращает кортеж (added, removed):
    - added: элементы, появившиеся в новом скане
    - removed: элементы, исчезнувшие в новом скане
    """
    old_set = set(tuple(row) for row in old_scan)
    new_set = set(tuple(row) for row in new_scan)
    added = new_set - old_set
    removed = old_set - new_set
    return list(added), list(removed)


if __name__ == "__main__":
    init_db()
