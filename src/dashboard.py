from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import yaml
import os
import logging
from src.config import HTTP_AUTH_USERNAME, HTTP_AUTH_PASSWORD, DATABASE_PATH

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/clearscan/dashboard.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('dashboard')

# Загрузка конфигурации
with open(os.path.join(os.path.dirname(__file__), '../config.yaml'), 'r') as f:
    config = yaml.safe_load(f)

app = Flask(
    __name__, template_folder="../templates", static_folder="../static"
)
app.secret_key = os.urandom(24)
app.config['DB_PATH'] = DATABASE_PATH

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        logger.info(f"Попытка входа пользователя: {username}")
        
        if username == HTTP_AUTH_USERNAME and password == HTTP_AUTH_PASSWORD:
            logger.info(f"Успешная аутентификация для пользователя: {username}")
            session['user'] = username
            return redirect(url_for('dashboard'))
        
        logger.warning(f"Неудачная попытка входа для пользователя: {username}")
        return render_template('login.html', error='Неверные данные')
    
    logger.info("Отображение страницы входа")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        logger.warning("Попытка доступа к dashboard без аутентификации")
        return redirect(url_for('login'))
    
    try:
        ip_filter = request.args.get('ip', '')
        port_filter = request.args.get('port', '')
        logger.info(f"Запрос dashboard с фильтрами: ip={ip_filter}, port={port_filter}")
        
        conn = sqlite3.connect(app.config['DB_PATH'])
        c = conn.cursor()
        
        # Проверяем существование таблиц
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='scan_results'")
        if not c.fetchone():
            logger.error("Таблица scan_results не найдена в базе данных")
            return render_template('dashboard.html', error='База данных не инициализирована')
        
        query = "SELECT ip, port, status, scan_time FROM scan_results"
        params = []
        if ip_filter:
            query += " WHERE ip = ?"
            params.append(ip_filter)
        if port_filter:
            query += (
                " AND port = ?" if ip_filter else " WHERE port = ?"
            )
            params.append(port_filter)
        query += " ORDER BY scan_time DESC LIMIT 100"
        
        logger.info(f"Выполнение запроса: {query} с параметрами: {params}")
        c.execute(query, params)
        rows = c.fetchall()
        logger.info(f"Получено {len(rows)} результатов сканирования")
        
        # Получаем историю изменений
        c.execute(
            "SELECT change_type, ip, port, status, change_time FROM scan_history "
            "ORDER BY change_time DESC LIMIT 20"
        )
        changes = c.fetchall()
        logger.info(f"Получено {len(changes)} записей истории")
        
        conn.close()
        
        return render_template(
            'dashboard.html', 
            rows=rows, 
            changes=changes,
            ip_filter=ip_filter, 
            port_filter=port_filter
        )
    except sqlite3.Error as e:
        logger.error(f"Ошибка базы данных: {str(e)}", exc_info=True)
        return render_template('dashboard.html', error=f'Ошибка базы данных: {str(e)}')
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {str(e)}", exc_info=True)
        return render_template('dashboard.html', error='Произошла внутренняя ошибка')

@app.route('/logout')
def logout():
    if 'user' in session:
        logger.info(f"Выход пользователя: {session['user']}")
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
