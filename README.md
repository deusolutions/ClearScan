# ClearScan

[![CI](https://github.com/deusolutions/ClearScan/actions/workflows/ci.yml/badge.svg)](https://github.com/deusolutions/ClearScan/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)](https://github.com/deusolutions/ClearScan/releases)

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

> Установка полностью автоматизирована, никаких ручных действий с пользователями и правами не требуется. Просто запустите install.sh от root или через sudo.

1. **Запустите установку одной командой:**
   ```bash
   sudo bash install.sh
   ```
   Скрипт автоматически:
   - установит зависимости (nmap, python3-pip, python3-venv)
   - создаст пользователя clearscan
   - скопирует все файлы в /opt/clearscan
   - создаст виртуальное окружение и установит зависимости в него
   - настроит права
   - скопирует и активирует systemd-сервисы (dashboard и Telegram-бот)
   - инициализирует базу данных
   - сгенерирует безопасный пароль для веб-панели, выведет его в терминал и запишет в config.yaml
   - запустит сервисы

2. **Пароль для входа в веб-панель** будет показан в терминале после установки и автоматически записан в /opt/clearscan/config.yaml. Логин: admin

3. **Проверьте статус сервисов:**
   ```bash
   systemctl status clearscan clearscan-bot
   ```

4. **(Опционально) Измените другие параметры в /opt/clearscan/config.yaml** (подсети, порты, Telegram-токен и т.д.)

5. **Доступ к Dashboard:**
   - Dashboard: http://<сервер>:8080

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

## Текущая версия (v0.1.0)

### Основные функции
- Сканирование подсетей с помощью nmap
- Хранение истории в SQLite
- Сравнение результатов сканирования (diff)
- Базовые уведомления через Telegram
- Простой веб-интерфейс
- Конфигурация через YAML

### Структура проекта
- `core/` — ядро сканера и основная логика
- `db/` — работа с SQLite и миграции
- `services/` — фоновые сервисы
- `web/` — веб-интерфейс на Flask
- `bot/` — Telegram-бот
- `cli/` — командная строка
- `tests/` — модульные и интеграционные тесты

### Планы на v0.2.0
- Улучшенный веб-интерфейс с графиками
- Расширенные уведомления
- API для интеграции
- Поддержка Docker
- Улучшенная документация