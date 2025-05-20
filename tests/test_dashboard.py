import pytest
from flask import session
from src import scanner, comparator
from src.dashboard import app
import os
import tempfile

@pytest.fixture
def client():
    # Используем отдельную временную БД для теста
    with tempfile.NamedTemporaryFile(delete=False) as tf:
        test_db_path = tf.name
    app.config['TESTING'] = True
    app.config['DB_PATH'] = test_db_path
    scanner.DATABASE_PATH = test_db_path
    comparator.DATABASE_PATH = test_db_path
    # Создаём таблицы
    scanner.init_db()
    comparator.ensure_history_table()
    yield app.test_client()
    # Удаляем временную БД после теста
    try:
        os.remove(test_db_path)
    except PermissionError:
        pass

def test_login_logout(client):
    # Проверка неавторизованного доступа
    resp = client.get('/dashboard')
    assert resp.status_code == 302  # редирект на логин
    # Логин с неверными данными
    resp = client.post('/', data={'username': 'bad', 'password': 'bad'})
    assert 'Неверные данные' in resp.data.decode('utf-8')
    # Логин с верными данными
    import yaml
    with open("config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    username = config["dashbord_credentials"]["username"]
    password = config["dashbord_credentials"]["password"]
    resp = client.post('/', data={'username': username, 'password': password}, follow_redirects=True)
    assert 'ClearScan Dashboard' in resp.data.decode('utf-8')
    # Логаут
    resp = client.get('/logout', follow_redirects=True)
    assert 'Вход в ClearScan' in resp.data.decode('utf-8')

def test_dashboard_render(client):
    # Логин
    import yaml
    with open("config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    username = config["dashbord_credentials"]["username"]
    password = config["dashbord_credentials"]["password"]
    client.post('/', data={'username': username, 'password': password})
    resp = client.get('/dashboard')
    assert 'Последние сканы' in resp.data.decode('utf-8')
    assert 'Изменения' in resp.data.decode('utf-8')
