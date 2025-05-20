import os
import sqlite3
import yaml
from flask import Flask, render_template, request, redirect, url_for, session
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
    ip_filter = request.args.get('ip', '')
    port_filter = request.args.get('port', '')
    conn = sqlite3.connect(
        app.config.get('DB_PATH', config.get('database_path', 'clearscan.db'))
    )
    c = conn.cursor()
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
    c.execute(query, params)
    rows = c.fetchall()
    # Изменения
    c.execute(
        "SELECT change_type, ip, port, status, change_time FROM scan_history "
        "ORDER BY change_time DESC LIMIT 20"
    )
    changes = c.fetchall()
    conn.close()
    return render_template(
        'dashboard.html', rows=rows, changes=changes,
        ip_filter=ip_filter, port_filter=port_filter
    )


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
