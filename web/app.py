from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pathlib import Path
import sys
import os
from datetime import datetime
from typing import Optional

# Добавляем корневую директорию проекта в PYTHONPATH
sys.path.append(str(Path(__file__).parent.parent))

from db.database import Database
from config.config import Config
from services.history_service import HistoryService

app = FastAPI(title="ClearScan")

# Монтируем статические файлы
app.mount("/static", StaticFiles(directory="web/static"), name="static")

# Настраиваем шаблоны
templates = Jinja2Templates(directory="web/templates")

# Инициализация базы данных и сервисов
config = Config()
db = Database(config)
history_service = HistoryService(db)

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Главная страница с последними сканированиями"""
    # Получаем последние 10 сканирований
    scans = await db.get_last_scans(10)
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "scans": scans}
    )

@app.get("/history", response_class=HTMLResponse)
async def history(
    request: Request,
    cidr: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    page: int = 1,
    sort: str = "desc"
):
    """Страница истории сканирований"""
    # Преобразуем строковые даты в datetime
    date_from_dt = datetime.fromisoformat(date_from) if date_from else None
    date_to_dt = datetime.fromisoformat(date_to) if date_to else None
    
    # Получаем данные с учетом фильтров и пагинации
    result = await history_service.get_scans(
        cidr=cidr,
        date_from=date_from_dt,
        date_to=date_to_dt,
        page=page,
        sort_desc=(sort != "asc")
    )
    
    return templates.TemplateResponse(
        "history.html",
        {
            "request": request,
            "scans": result["scans"],
            "page": result["page"],
            "total_pages": result["total_pages"],
            "has_next": result["has_next"],
            "has_prev": result["has_prev"]
        }
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