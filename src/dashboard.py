from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import yaml
import os
from src.config import HTTP_AUTH_USERNAME, HTTP_AUTH_PASSWORD, DATABASE_PATH

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
        username = request.form['username']
        password = request.form['password']
        if username == HTTP_AUTH_USERNAME and password == HTTP_AUTH_PASSWORD:
            session['user'] = username
            return redirect(url_for('dashboard'))
        return render_template('login.html', error='Неверные данные')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    try:
        ip_filter = request.args.get('ip', '')
        port_filter = request.args.get('port', '')
        
        conn = sqlite3.connect(app.config['DB_PATH'])
        c = conn.cursor()
        
        # Проверяем существование таблиц
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='scan_results'")
        if not c.fetchone():
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
            'dashboard.html', 
            rows=rows, 
            changes=changes,
            ip_filter=ip_filter, 
            port_filter=port_filter
        )
    except sqlite3.Error as e:
        return render_template('dashboard.html', error=f'Ошибка базы данных: {str(e)}')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
