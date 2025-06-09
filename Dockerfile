FROM python:3.11-slim

# Установка nmap
RUN apt-get update && \
    apt-get install -y nmap && \
    rm -rf /var/lib/apt/lists/*

# Создание рабочей директории
WORKDIR /app

# Копирование файлов проекта
COPY . .

# Установка зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Запуск сканера
CMD ["python", "scan.py"] 