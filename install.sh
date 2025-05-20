#!/bin/bash
# install.sh - Полностью автоматическая установка ClearScan
set -e

# Проверка root
if [[ $EUID -ne 0 ]]; then
  echo "Пожалуйста, запускайте скрипт через sudo или от root!"
  exit 1
fi

# Установка зависимостей
apt update
apt install -y nmap python3-pip
pip3 install gunicorn

# Создание пользователя clearscan, если не существует
id clearscan &>/dev/null || useradd --system --no-create-home --shell /usr/sbin/nologin clearscan

# Копирование файлов проекта в /opt/clearscan
mkdir -p /opt/clearscan
cp -r . /opt/clearscan/
chown -R clearscan:clearscan /opt/clearscan

# Копирование systemd unit-файлов
cp /opt/clearscan/systemd/clearscan.service /etc/systemd/system/clearscan.service
cp /opt/clearscan/systemd/clearscan-bot.service /etc/systemd/system/clearscan-bot.service

# Копирование примера конфигурации (только если нет)
if [ ! -f /opt/clearscan/config.yaml ]; then
  tee /opt/clearscan/config.yaml > /dev/null <<EOCFG
# Пример конфигурации
subnets:
  - "10.0.0.0/24"
  - "192.168.1.0/24"
ports:
  - 22
  - 80
  - 443
database_path: '/opt/clearscan/clearscan.db'
telegram_bot_token: 'your_telegram_bot_token'
scan_interval: 3600
nmap_path: '/usr/bin/nmap'
http_auth_username: 'admin'
http_auth_password: 'password'
EOCFG
  chown clearscan:clearscan /opt/clearscan/config.yaml
fi

# Явно создаём файл БД, если его нет, и задаём права
if [ ! -f /opt/clearscan/clearscan.db ]; then
  sudo -u clearscan touch /opt/clearscan/clearscan.db
  chown clearscan:clearscan /opt/clearscan/clearscan.db
fi
chmod 660 /opt/clearscan/clearscan.db

# Инициализация БД (от пользователя clearscan)
sudo -u clearscan python3 /opt/clearscan/src/db.py || {
  echo "[ERROR] Не удалось инициализировать БД. Проверьте права на /opt/clearscan и clearscan.db";
  exit 1;
}

# Включение и запуск сервисов
systemctl daemon-reload
systemctl enable clearscan clearscan-bot
systemctl restart clearscan clearscan-bot

cat <<EOF
Установка завершена!
- Пример конфигурации: /opt/clearscan/config.yaml
- Каталог приложения: /opt/clearscan/
- Dashboard: http://<сервер>:80
- Для управления: systemctl [status|restart|stop] clearscan clearscan-bot
EOF
