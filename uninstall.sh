#!/bin/bash
# uninstall.sh - Полное удаление ClearScan и всех его следов
set -e

# Остановить и отключить сервисы
systemctl stop clearscan || true
systemctl stop clearscan-bot || true
systemctl disable clearscan || true
systemctl disable clearscan-bot || true
systemctl daemon-reload

# Удалить systemd unit-файлы
rm -f /etc/systemd/system/clearscan.service
rm -f /etc/systemd/system/clearscan-bot.service
systemctl daemon-reload

# Удалить пользователя clearscan (если не используется другими сервисами)
id clearscan &>/dev/null && userdel clearscan

# Удалить каталог приложения
rm -rf /opt/clearscan

# Удалить базу данных, если она вне каталога
rm -f /opt/clearscan/clearscan.db

# Удалить логи (если есть)
rm -f /var/log/clearscan.log

# Готово
cat <<EOF
ClearScan полностью удалён!
EOF
