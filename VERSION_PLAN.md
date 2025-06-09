# План версий ClearScan

## v0.1.0 — Ядро и CLI
- ⚙️ Сканер на nmap с параметрами из config.yaml
- 🗃 Хранение результатов в SQLite
- 🔁 Diff-сравнение результатов
- 🧪 Базовые unit-тесты на Scanner и Diff
- ⚒ CLI-интерфейс для запуска: `python scan.py`
- 📂 Структура проекта и setup
- 📜 Пример config.yaml
- 🐳 Dockerfile (одиночный контейнер)

## v0.2.0 — Telegram + Dashboard
- Telegram-бот: отправка дельт
- Flask-dashboard: авторизация, таблица сканов
- systemd-юниты для бота и веб-сервера
- cron/systemd для запуска сканирования

## v0.3.0 — Интеграции, безопасность
- Защита dashboard (IP whitelist, basic auth)
- Шифрование токенов Telegram
- IP-ротация, логирование
- Export в CSV

