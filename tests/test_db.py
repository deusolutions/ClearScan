import pytest
import sqlite3
import os
from src import db

@pytest.fixture
def db_conn(tmp_path):
    db_file = tmp_path / "test.db"
    conn = sqlite3.connect(db_file)
    # Переопределяем путь к БД и инициализируем таблицы
    db.DB_PATH = str(db_file)
    db.init_db()
    yield conn
    conn.close()
    os.remove(db_file)

def test_insert_and_fetch(db_conn):
    db.insert_scan_result(db_conn, '192.168.1.1', 22, 'tcp', 'open', 'ssh')
    results = db.fetch_last_scan(db_conn)
    assert results[0][:3] == ('192.168.1.1', 22, 'tcp')

def test_compare_scans():
    old = [('192.168.1.1', 22, 'tcp', 'open', 'ssh')]
    new = [('192.168.1.1', 22, 'tcp', 'open', 'ssh'), ('192.168.1.2', 80, 'tcp', 'open', 'http')]
    added, removed = db.compare_scans(old, new)
    assert ('192.168.1.2', 80, 'tcp', 'open', 'http') in added
    assert not removed
