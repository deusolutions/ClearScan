-- Таблица сканов
CREATE TABLE scans (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  timestamp DATETIME,
  ip TEXT,
  port INTEGER,
  status TEXT
);

-- Таблица изменений
CREATE TABLE changes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  timestamp DATETIME,
  ip TEXT,
  port INTEGER,
  old_status TEXT,
  new_status TEXT
);
