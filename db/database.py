import sqlite3
from typing import List, Dict, Any
import datetime

class Database:
    def __init__(self, db_path: str = 'clearscan.db'):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Инициализация базы данных и создание таблиц"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Создание таблицы сканов
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS scans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME,
                    ip TEXT,
                    port INTEGER,
                    status TEXT
                )
            ''')
            
            # Создание таблицы изменений
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS changes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME,
                    ip TEXT,
                    port INTEGER,
                    old_status TEXT,
                    new_status TEXT
                )
            ''')
            
            conn.commit()

    def save_scan_results(self, results: List[Dict[str, Any]]):
        """Сохранение результатов сканирования"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for result in results:
                cursor.execute('''
                    INSERT INTO scans (timestamp, ip, port, status)
                    VALUES (?, ?, ?, ?)
                ''', (
                    result['timestamp'],
                    result['ip'],
                    result['port'],
                    result['status']
                ))
            conn.commit()

    def get_last_scan(self) -> List[Dict[str, Any]]:
        """Получение результатов последнего сканирования"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT timestamp, ip, port, status
                FROM scans
                WHERE timestamp = (
                    SELECT MAX(timestamp) FROM scans
                )
            ''')
            return [
                {
                    'timestamp': row[0],
                    'ip': row[1],
                    'port': row[2],
                    'status': row[3]
                }
                for row in cursor.fetchall()
            ]

    def get_nth_last_scan(self, n: int = 2) -> List[Dict[str, Any]]:
        """Получение N-го с конца сканирования (по умолчанию предпоследнего)"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT timestamp FROM scans
                GROUP BY timestamp
                ORDER BY timestamp DESC
                LIMIT 1 OFFSET ?
            ''', (n-1,))
            row = cursor.fetchone()
            if not row:
                return []
            timestamp = row[0]
            cursor.execute('''
                SELECT timestamp, ip, port, status
                FROM scans
                WHERE timestamp = ?
            ''', (timestamp,))
            return [
                {
                    'timestamp': r[0],
                    'ip': r[1],
                    'port': r[2],
                    'status': r[3]
                }
                for r in cursor.fetchall()
            ]

    def save_changes(self, changes: List[Dict[str, Any]]):
        """Сохранение изменений"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for change in changes:
                cursor.execute('''
                    INSERT INTO changes (timestamp, ip, port, old_status, new_status)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    change['timestamp'],
                    change['ip'],
                    change['port'],
                    change['old_status'],
                    change['new_status']
                ))
            conn.commit() 