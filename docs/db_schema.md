# DB Schema Documentation for ClearScan

## scan_results
- id: INTEGER PRIMARY KEY AUTOINCREMENT
- scan_id: TEXT — уникальный идентификатор сканирования
- ip: TEXT — IP-адрес
- port: INTEGER — порт
- status: TEXT — статус порта (open/closed)
- scan_time: DATETIME — время сканирования

## scan_history
- id: INTEGER PRIMARY KEY AUTOINCREMENT
- scan_id: TEXT — идентификатор сканирования
- change_time: DATETIME — время фиксации изменения
- change_type: TEXT — тип изменения ('opened' или 'closed')
- ip: TEXT — IP-адрес
- port: INTEGER — порт
- status: TEXT — статус порта

### Формат изменений
- Каждое изменение (открытие/закрытие порта) фиксируется отдельной записью в scan_history с типом изменения ('opened' или 'closed').
- Для каждого изменения сохраняются: scan_id, время, тип, ip, порт, статус.
