# ClearScan

[![CI](https://github.com/deusolutions/ClearScan/actions/workflows/ci.yml/badge.svg)](https://github.com/deusolutions/ClearScan/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> **ClearScan** — автоматизированный сканер подсетей с веб-дашбордом, Telegram-ботом, хранением истории в SQLite и полной автоматизацией. Разработано и поддерживается [Deus Solutions](https://deusolutions.ru).

---

## О проекте

ClearScan — это open-source система для регулярного сканирования подсетей с помощью nmap, хранения истории изменений, мгновенных уведомлений через Telegram-бота и современного веб-дашборда на Flask. Проект ориентирован на безопасность, автоматизацию и простоту внедрения в инфраструктуру любого масштаба.

- **Автоматизация:** cron/systemd, скрипты установки, безопасный запуск.
- **Безопасность:** отдельный пользователь, UFW, рекомендации по защите.
- **CI/CD:** GitHub Actions (flake8, pytest).
- **Документация:** подробные гайды, примеры, рекомендации.

---

## Быстрый старт

1. **Клонируйте репозиторий:**
   ```powershell
   git clone https://github.com/deusolutions/ClearScan.git
   cd ClearScan
   ```
2. **Установите зависимости:**
   ```powershell
   pip install -r requirements.txt
   ```
3. **Настройте конфиг:**
   - Отредактируйте `config.yaml` (подсети, порты, токен Telegram, логин/пароль).
4. **Инициализируйте БД:**
   ```powershell
   python src/db.py
   ```
5. **Запустите сканер или дашборд:**
   ```powershell
   python src/scanner.py
   python src/dashboard.py
   ```
6. **Запустите Telegram-бота:**
   ```powershell
   python src/telegram_bot.py
   ```

---

## Основные возможности

- Сканирование подсетей по расписанию (nmap)
- Хранение истории изменений (SQLite)
- Telegram-уведомления о новых/закрытых портах
- Веб-дашборд (Flask, авторизация)
- Логирование и автоматизация (cron, systemd)
- Интеграционные и unit-тесты (pytest)
- CI/CD (GitHub Actions)

---

## Документация
- [docs/db_schema.md](docs/db_schema.md) — структура БД
- [docs/security.md](docs/security.md) — безопасность
- [docs/logging.md](docs/logging.md) — логирование
- [CONTRIBUTING.md](CONTRIBUTING.md) — вклад в проект

---

## Пример config.yaml
```yaml
subnets:
  - "10.0.0.0/24"
  - "192.168.1.0/24"
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

## CI/CD
- Все коммиты и pull requests автоматически проверяются через GitHub Actions (flake8, pytest).
- Для релиза используйте git tag и GitHub Releases.

---

## Вклад
- Pull requests и Issues приветствуются!
- Перед коммитом: убедитесь, что проходят все тесты (`pytest`, `flake8`).
- Следуйте [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Лицензия

ClearScan распространяется под лицензией MIT. (c) 2023-2025 Deus Solutions

---

## Контакты
- [Deus Solutions](https://deusolutions.ru)
- Вопросы и предложения: через Issues или PR на GitHub