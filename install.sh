#!/bin/bash
# install.sh - Установка ClearScan и зависимостей
set -e

# Установка зависимостей
sudo apt update
sudo apt install -y nmap python3-pip
sudo pip3 install gunicorn

# Создание структуры
sudo mkdir -p /opt/clearscan/

# Копирование примера конфигурации
echo "# Пример конфигурации\ndatabase_path: '/opt/clearscan/clearscan.db'\ntelegram_bot_token: 'your_telegram_bot_token'\nscan_interval: 3600\nnmap_path: '/usr/bin/nmap'\nhttp_auth_username: 'admin'\nhttp_auth_password: 'password'\n" | sudo tee /opt/clearscan/config.yaml > /dev/null

# Инструкция
cat <<EOF
Установка завершена!
- Пример конфигурации: /opt/clearscan/config.yaml
- Установлены зависимости: nmap, python3-pip, gunicorn
- Каталог приложения: /opt/clearscan/
EOF
