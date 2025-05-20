# Hourly Subnet Scanner

This project is a lightweight application designed to perform hourly subnet scanning using `nmap`, store the results in an SQLite database, send notifications via a Telegram bot, and provide a web dashboard using Flask with HTTP Basic Auth.

## Project Structure

```
hourly-subnet-scanner
├── src
│   ├── scanner.py          # Responsible for scanning subnets and saving results
│   ├── db.py               # Manages SQLite database operations
│   ├── notifier.py          # Implements Telegram bot notifications
│   ├── dashboard
│   │   ├── __init__.py     # Initializes the Flask application
│   │   ├── routes.py       # Defines web dashboard routes
│   │   └── auth.py         # Handles HTTP Basic Authentication
│   └── config.py           # Contains configuration settings
├── requirements.txt         # Lists project dependencies
└── README.md                # Project documentation
```

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd hourly-subnet-scanner
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Configure the application:
   - Update the `src/config.py` file with your database path and Telegram bot token.

## Установка

1. Запустите bash-скрипт установки (требуются права sudo):
   ```bash
   bash install.sh
   ```
   Скрипт установит зависимости (nmap, python3-pip, gunicorn), создаст структуру `/opt/clearscan/` и пример конфигурации `/opt/clearscan/config.yaml`.

2. Проверьте и настройте параметры в `/opt/clearscan/config.yaml` под свои нужды.

## Пример config.yaml

```yaml
# Пример конфигурационного файла для ClearScan
subnets:
  - "87.252.250.0/24"
  - "87.252.245.0/24"
ports:
  - 22
  - 80
  - 443
telegram_token: "your_telegram_bot_token"
dashbord_credentials:
  username: "admin"
  password: "password"
```

> **Безопасность:**
> Никогда не публикуйте свой реальный telegram_token в публичных репозиториях. Для продакшена используйте переменные окружения или секреты CI/CD для хранения токенов и паролей.

## Usage

1. Run the application:
   ```
   python src/scanner.py
   ```

2. Access the web dashboard:
   - Open your web browser and navigate to `http://localhost:80`.

3. Set up your Telegram bot:
   - Follow the instructions provided by the Telegram Bot API to create a bot and obtain your bot token.

## Настройка Telegram-бота

1. Получите токен у @BotFather и добавьте его в config.yaml (или config.py).
2. Укажите разрешённые user_id в ALLOWED_USERS в telegram_bot.py.
3. Запустите бота:
   ```bash
   python3 src/telegram_bot.py
   ```
4. Доступные команды:
   - /start — приветствие
   - /status — последние результаты сканирования
   - /changes — последние изменения (открытие/закрытие портов)

> **Безопасность:**
> Не публикуйте токен и user_id в открытых репозиториях. Для продакшена используйте переменные окружения или секреты CI/CD.

## Веб-дашборд

1. Запуск:
   ```bash
   sudo python3 src/dashboard.py
   ```
2. Откройте http://<ваш_сервер>:80 в браузере.
3. Авторизация: логин/пароль из config.yaml.
4. Используется Tailwind CSS для современного интерфейса.
5. Шаблоны — в папке templates/, статика — в static/.

## Настройка планировщика (cron)

1. Запустите скрипт для настройки cron:
   ```bash
   bash setup_cron.sh
   ```
   Это добавит задачу, которая будет запускать scanner.py и comparator.py каждый час.
   Логи выполнения: /var/log/clearscan/scanner.log и /var/log/clearscan/comparator.log

2. Для проверки статуса cron используйте:
   ```bash
   crontab -l
   tail -f /var/log/clearscan/scanner.log
   tail -f /var/log/clearscan/comparator.log
   ```

## Автозапуск через systemd

1. Скопируйте шаблон сервиса:
   ```bash
   sudo cp systemd/clearscan.service /etc/systemd/system/clearscan.service
   ```
2. Перезапустите systemd и включите сервис:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable clearscan
   sudo systemctl start clearscan
   sudo systemctl status clearscan
   ```
3. Сервис автоматически запускает дашборд (gunicorn) и Telegram-бота от пользователя clearscan.

## Features

- Hourly subnet scanning using `nmap`.
- Results stored in an SQLite database.
- Notifications sent via a Telegram bot.
- Web dashboard for monitoring scan results with HTTP Basic Auth.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

---

## Быстрый старт

1. **Установка зависимостей и структуры**
   ```powershell
   bash install.sh
   ```
2. **Настройка безопасности**
   ```powershell
   bash secure_setup.sh
   ```
3. **Настройка cron (автоматизация сканирования)**
   ```powershell
   bash setup_cron.sh
   ```
4. **Настройка автозапуска (systemd)**
   ```powershell
   sudo cp systemd/clearscan.service /etc/systemd/system/clearscan.service
   sudo systemctl daemon-reload
   sudo systemctl enable clearscan
   sudo systemctl start clearscan
   sudo systemctl status clearscan
   ```
5. **Настройка Telegram-бота**
   - Получите токен у @BotFather, добавьте в config.yaml
   - Укажите разрешённые user_id в telegram_bot.py
   - Запустите:
     ```powershell
     python3 src/telegram_bot.py
     ```

---

## Пример config.yaml
```yaml
subnets:
  - "87.252.250.0/24"
  - "87.252.245.0/24"
ports:
  - 22
  - 80
  - 443
telegram_token: "your_telegram_bot_token"
dashbord_credentials:
  username: "admin"
  password: "password"
```

---

## Использование
- Веб-дашборд: http://<сервер>:80 (логин/пароль из config.yaml)
- Telegram-бот: команды /status, /changes
- Логи: /var/log/clearscan.log (ротация, см. docs/logging.md)
- Интеграционные тесты: pytest tests/integration/

---

## Документация
- [docs/db_schema.md](docs/db_schema.md) — структура базы данных и формат изменений
- [docs/security.md](docs/security.md) — рекомендации по безопасности, права, firewall
- [docs/logging.md](docs/logging.md) — формат логов, ротация

---

## Вклад и поддержка
- Pull requests приветствуются!
- Перед коммитом: убедитесь, что проходят все тесты (pytest, flake8)
- Вопросы и баги — через Issues

---

## Лицензия
MIT License