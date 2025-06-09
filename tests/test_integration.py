import unittest
import os
import sqlite3
from datetime import datetime
from core.scanner import Scanner
from core.diff import Diff
from db.database import Database

class FakePortScanner:
    def __init__(self, tcp_state):
        self.data = {
            '127.0.0.1': {
                'tcp': tcp_state
            }
        }
    def all_hosts(self):
        return ['127.0.0.1']
    def __getitem__(self, key):
        return self.data[key]
    def scan(self, *args, **kwargs):
        pass

class TestIntegration(unittest.TestCase):
    def setUp(self):
        # Тестовая БД
        self.test_db = 'test_clearscan.db'
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
        
        # Инициализация компонентов
        self.db = Database(self.test_db)
        self.scanner = Scanner(["127.0.0.1"], [80, 443])
        self.diff = Diff()

    def tearDown(self):
        if os.path.exists(self.test_db):
            os.remove(self.test_db)

    def test_full_cycle(self):
        # Первое сканирование (open/closed)
        self.scanner.nm = FakePortScanner({'80': {'state': 'open'}, '443': {'state': 'closed'}})
        print("\nВыполняем первое сканирование...")
        first_scan = self.scanner.scan()
        self.db.save_scan_results(first_scan)
        
        # Проверяем сохранение
        with sqlite3.connect(self.test_db) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM scans")
            first_count = cursor.fetchone()[0]
            print(f"Сохранено записей: {first_count}")
            self.assertGreater(first_count, 0)

        # Второе сканирование (closed/open)
        print("\nИмитируем изменения в сети...")
        self.scanner.nm = FakePortScanner({'80': {'state': 'closed'}, '443': {'state': 'open'}})
        print("Выполняем второе сканирование...")
        second_scan = self.scanner.scan()
        self.db.save_scan_results(second_scan)

        # Получаем предпоследний скан для сравнения
        prev_results = self.db.get_nth_last_scan(2)
        
        # Сравниваем результаты
        print("\nСравниваем результаты...")
        changes = self.diff.compare(second_scan, prev_results)
        
        # Проверяем изменения
        self.assertGreater(len(changes), 0)
        print(f"Обнаружено изменений: {len(changes)}")
        
        # Сохраняем изменения
        self.db.save_changes(changes)
        
        # Проверяем сохранение изменений
        with sqlite3.connect(self.test_db) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM changes")
            changes_count = cursor.fetchone()[0]
            print(f"Сохранено изменений: {changes_count}")
            self.assertEqual(changes_count, len(changes))

        # Выводим детали изменений
        print("\nДетали изменений:")
        for change in changes:
            print(f"IP: {change['ip']}, Port: {change['port']}")
            print(f"Старый статус: {change['old_status']}")
            print(f"Новый статус: {change['new_status']}")
            print("---")

if __name__ == '__main__':
    unittest.main() 