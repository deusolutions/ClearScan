import sqlite3

def create_connection(db_file):
    conn = sqlite3.connect(db_file)
    return conn

def create_tables(conn):
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scan_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subnet TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            results TEXT NOT NULL
        )
    ''')
    conn.commit()

def insert_scan_result(conn, subnet, results):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO scan_results (subnet, results)
        VALUES (?, ?)
    ''', (subnet, results))
    conn.commit()

def fetch_scan_history(conn):
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM scan_results ORDER BY timestamp DESC')
    return cursor.fetchall()