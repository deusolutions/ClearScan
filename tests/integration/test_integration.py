import os
import tempfile
import sqlite3
import pytest
from src import scanner, comparator, telegram_bot

@pytest.fixture(scope="module")
def test_db():
    tf = tempfile.NamedTemporaryFile(delete=False)
    db_path = tf.name
    tf.close()
    scanner.DATABASE_PATH = db_path
    comparator.DATABASE_PATH = db_path
    yield db_path
    # Закрываем все соединения с БД перед удалением файла
    try:
        os.remove(db_path)
    except PermissionError:
        pass

def test_full_scan_compare_notify(monkeypatch, test_db):
    # 1. Инициализация БД
    scanner.init_db()
    comparator.ensure_history_table()
    # 2. Первый скан (старое состояние)
    scan_id1 = 'scan-1'
    results1 = [('10.0.0.1', 22, 'open'), ('10.0.0.2', 80, 'open')]
    scanner.save_scan_results(results1, scan_id1, '2025-05-20T12:00:00')
    # 3. Второй скан (новое состояние)
    scan_id2 = 'scan-2'
    results2 = [('10.0.0.1', 22, 'open'), ('10.0.0.3', 443, 'open')]
    scanner.save_scan_results(results2, scan_id2, '2025-05-20T13:00:00')
    # 4. Сравнение и запись изменений
    conn = sqlite3.connect(test_db)
    old = comparator.get_scan_results(conn, scan_id1)
    new = comparator.get_scan_results(conn, scan_id2)
    added, removed = comparator.compare_scans(old, new)
    comparator.save_changes_to_history(conn, scan_id2, added, removed)
    # 5. Проверка истории изменений
    c = conn.cursor()
    c.execute("SELECT change_type, ip, port, status FROM scan_history WHERE scan_id=?", (scan_id2,))
    changes = c.fetchall()
    assert ('opened', '10.0.0.3', 443, 'open') in changes
    assert ('closed', '10.0.0.2', 80, 'open') in changes
    # 6. Проверка уведомления (мокаем отправку)
    conn.close()
    sent = {}
    def fake_send(token, chat_id, added_ports, removed_ports):
        sent['added'] = added_ports
        sent['removed'] = removed_ports
    monkeypatch.setattr(telegram_bot, 'send_port_changes', fake_send)
    telegram_bot.send_port_changes('token', 1, added, removed)
    assert sent['added'] == [('10.0.0.3', 443, 'open')]
    assert sent['removed'] == [('10.0.0.2', 80, 'open')]
    conn.close()
