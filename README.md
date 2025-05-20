# ClearScan

[![CI](https://github.com/deusolutions/ClearScan/actions/workflows/ci.yml/badge.svg)](https://github.com/deusolutions/ClearScan/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> **ClearScan** — автоматизированный сканер подсетей с веб-дашбордом, Telegram-ботом, хранением истории в SQLite и полной автоматизацией. Разработано и поддерживается [Deus Solutions](https://deusolutions.ru).

---

## Важно

**ClearScan поддерживается и предназначен только для Linux-серверов. Запуск на Windows не поддерживается и не рекомендуется.**

---

## О проекте

ClearScan — это open-source система для регулярного сканирования подсетей с помощью nmap, хранения истории изменений, мгновенных уведомлений через Telegram-бота и современного веб-дашборда на Flask. Проект ориентирован на безопасность, автоматизацию и простоту внедрения в инфраструктуру любого масштаба.

- **Автоматизация:** cron/systemd, скрипты установки, безопасный запуск.
- **Безопасность:** отдельный пользователь, UFW, рекомендации по защите.
- **CI/CD:** GitHub Actions (flake8, pytest).
- **Документация:** подробные гайды, примеры, рекомендации.

---

## Установка и запуск (Linux, production-ready)

1. **Клонируйте репозиторий:**
   ```bash
   git clone https://github.com/deusolutions/ClearScan.git
   cd ClearScan
   ```
2. **Запустите скрипт установки:**
   ```bash
   sudo bash install.sh
   ```
   Скрипт установит nmap, python3-pip, gunicorn, создаст структуру `/opt/clearscan/` и пример конфига `/opt/clearscan/config.yaml`.
3. **Отредактируйте /opt/clearscan/config.yaml** под ваши подсети, порты, токен Telegram, логин/пароль.
4. **Инициализируйте БД:**
   ```bash
   sudo python3 /opt/clearscan/src/db.py
   ```
5. **Настройте автозапуск через systemd:**
   ```bash
   sudo cp systemd/clearscan.service /etc/systemd/system/clearscan.service
   sudo systemctl daemon-reload
   sudo systemctl enable clearscan
   sudo systemctl start clearscan
   sudo systemctl status clearscan
   ```
   После этого ClearScan будет работать как демон: сканер, дашборд и Telegram-бот будут запускаться автоматически.

---

## Безопасность и эксплуатация
- Рекомендуется запускать ClearScan только от отдельного системного пользователя (см. install.sh и secure_setup.sh).
- Используйте UFW/firewalld для ограничения доступа к дашборду и сервисам.
- Не храните реальные токены и пароли в публичных репозиториях.
- Все логи и база данных по умолчанию размещаются в /opt/clearscan/.

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