#!/bin/bash
# setup_cron.sh - настройка cron для ClearScan
set -e

LOGDIR="/var/log/clearscan"
mkdir -p "$LOGDIR"

CRON_JOB="0 * * * * cd /opt/clearscan && /usr/bin/python3 /opt/clearscan/src/scanner.py >> $LOGDIR/scanner.log 2>&1 && /usr/bin/python3 /opt/clearscan/src/comparator.py >> $LOGDIR/comparator.log 2>&1"

# Удаляем старые задачи ClearScan
crontab -l | grep -v 'clearscan' > /tmp/cron_clearscan || true
# Добавляем новую задачу
{
  cat /tmp/cron_clearscan
  echo "$CRON_JOB # clearscan"
} | crontab -

# Инструкция
cat <<EOF
Cron-задача для ClearScan настроена!
- scanner.py и comparator.py будут запускаться каждый час.
- Логи: $LOGDIR/scanner.log, $LOGDIR/comparator.log
EOF
