#!/bin/bash
# secure_setup.sh - базовая настройка безопасности для ClearScan
set -e

# Создать пользователя clearscan, если не существует
if ! id "clearscan" &>/dev/null; then
    sudo useradd -r -m -d /opt/clearscan -s /usr/sbin/nologin clearscan
fi

# Установить права на /opt/clearscan
sudo chown -R clearscan:clearscan /opt/clearscan
sudo chmod -R 750 /opt/clearscan

# Ограничить права на конфиг и базу
sudo chmod 640 /opt/clearscan/config.yaml || true
sudo chmod 640 /opt/clearscan/clearscan.db || true

# Настроить UFW
sudo ufw allow 80/tcp
sudo ufw allow 22/tcp
sudo ufw default deny incoming
sudo ufw --force enable

echo "Безопасность настроена: пользователь clearscan, права на файлы, ufw (80, 22)"
