from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pathlib import Path
import sys
import os

# Добавляем корневую директорию проекта в PYTHONPATH
sys.path.append(str(Path(__file__).parent.parent))

from db.database import Database
from config.config import Config

app = FastAPI(title="ClearScan")

# Монтируем статические файлы
app.mount("/static", StaticFiles(directory="web/static"), name="static")

# Настраиваем шаблоны
templates = Jinja2Templates(directory="web/templates")

# Инициализация базы данных
config = Config()
db = Database(config)

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Главная страница с последними сканированиями"""
    # Получаем последние 10 сканирований
    scans = await db.get_last_scans(10)
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "scans": scans}
    )

@app.get("/scans", response_class=HTMLResponse)
async def scans(request: Request):
    """Страница со всеми сканированиями"""
    scans = await db.get_all_scans()
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "scans": scans}
    )

@app.get("/scans/{scan_id}", response_class=HTMLResponse)
async def scan_details(request: Request, scan_id: int):
    """Детальная информация о сканировании"""
    scan = await db.get_scan_by_id(scan_id)
    if not scan:
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "error": "Сканирование не найдено"}
        )
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "scan": scan}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080) 