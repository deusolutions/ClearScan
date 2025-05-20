import pytest
import os
import tempfile
import sqlite3
from src import scanner

def test_parse_nmap_xml():
    """Проверяет корректность парсинга XML nmap."""
    xml = '''<nmaprun><host><address addr="192.168.1.1"/><ports>
    <port protocol="tcp" portid="22"><state state="open"/></port>
    <port protocol="tcp" portid="80"><state state="closed"/></port>
    </ports></host></nmaprun>'''
    results = scanner.parse_nmap_xml(xml)
    assert ('192.168.1.1', 22, 'open') in results
    assert ('192.168.1.1', 80, 'closed') in results

def test_save_scan_results():
    """Проверяет сохранение результатов сканирования в БД."""
    with tempfile.NamedTemporaryFile(delete=False) as tf:
        db_path = tf.name
    try:
        # Переопределяем путь к БД
        scanner.DATABASE_PATH = db_path
        scanner.init_db()
        scan_id = 'test-scan-1'
        results = [('10.0.0.1', 22, 'open'), ('10.0.0.1', 80, 'closed')]
        scanner.save_scan_results(results, scan_id, '2025-05-20T12:00:00')
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('SELECT ip, port, status, scan_id FROM scan_results')
        rows = c.fetchall()
        assert ('10.0.0.1', 22, 'open', 'test-scan-1') in rows
        assert ('10.0.0.1', 80, 'closed', 'test-scan-1') in rows
        conn.close()
    finally:
        os.remove(db_path)
