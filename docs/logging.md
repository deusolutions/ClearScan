# Logging format for ClearScan

- Log file: `/var/log/clearscan.log`
- Rotation: 10 MB, 3 backups (clearscan.log.1, clearscan.log.2, ...)
- Format:
  - `2025-05-20 12:00:00,123 INFO scanner: Scan started`
  - `2025-05-20 12:01:00,456 ERROR comparator: Exception ...`
- Fields:
  - Timestamp (ISO format)
  - Log level (INFO, ERROR, etc)
  - Module name
  - Message

Пример:
```
2025-05-20 12:00:00,123 INFO scanner: Scan started
2025-05-20 12:01:00,456 ERROR comparator: Exception: Connection refused
```
