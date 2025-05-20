import xml.etree.ElementTree as ET
import subprocess
import sqlite3
import datetime
from src.config import DATABASE_PATH


def init_db():
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute(
        '''
        CREATE TABLE IF NOT EXISTS scan_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scan_id TEXT NOT NULL,
            ip TEXT NOT NULL,
            port INTEGER NOT NULL,
            status TEXT NOT NULL,
            scan_time DATETIME NOT NULL
        )
        '''
    )
    conn.commit()
    conn.close()


def run_nmap(subnet, ports=None):
    """
    Запускает nmap для заданной подсети и портов, возвращает XML-вывод.
    """
    if ports is None:
        ports = [22, 80, 443]
    port_str = ','.join(str(p) for p in ports)
    cmd = [
        'nmap', '-T2', '-p', port_str, '-oX', '-', subnet
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout


def parse_nmap_xml(xml_data):
    """
    Парсит XML-вывод nmap и возвращает список кортежей (ip, port, status).
    """
    hosts = []
    root = ET.fromstring(xml_data)
    for host in root.findall('host'):
        ip_elem = host.find('address')
        if ip_elem is not None:
            ip = ip_elem.get('addr')
        else:
            continue
        for port in host.findall('.//port'):
            portid = int(port.get('portid'))
            state = port.find('state').get('state')
            hosts.append((ip, portid, state))
    return hosts


def save_scan_results(results, scan_id, scan_time=None):
    """
    Сохраняет результаты сканирования в таблицу scan_results.
    results: список (ip, port, status)
    scan_id: уникальный идентификатор скана
    scan_time: время сканирования (по умолчанию текущее)
    """
    if scan_time is None:
        scan_time = datetime.datetime.now().isoformat()
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    for ip, port, status in results:
        c.execute(
            '''
            INSERT INTO scan_results (scan_id, ip, port, status, scan_time)
            VALUES (?, ?, ?, ?, ?)''',
            (scan_id, ip, port, status, scan_time)
        )
    conn.commit()
    conn.close()


if __name__ == "__main__":
    import uuid
    from src.config import subnets, ports
    init_db()
    scan_id = str(uuid.uuid4())
    for subnet in subnets:
        xml = run_nmap(subnet, ports)
        results = parse_nmap_xml(xml)
        save_scan_results(results, scan_id)
