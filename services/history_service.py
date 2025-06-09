from datetime import datetime
from typing import Optional, List, Dict, Any
from db.database import Database

class HistoryService:
    def __init__(self, db: Database):
        self.db = db
        self.items_per_page = 10

    async def get_scans(
        self,
        cidr: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        page: int = 1,
        sort_desc: bool = True
    ) -> Dict[str, Any]:
        """
        Получение отфильтрованной и отсортированной истории сканирований
        """
        # Получаем общее количество записей
        total = await self.db.get_scans_count(cidr, date_from, date_to)
        
        # Вычисляем смещение для пагинации
        offset = (page - 1) * self.items_per_page
        
        # Получаем записи
        scans = await self.db.get_scans(
            cidr=cidr,
            date_from=date_from,
            date_to=date_to,
            limit=self.items_per_page,
            offset=offset,
            sort_desc=sort_desc
        )
        
        # Вычисляем общее количество страниц
        total_pages = (total + self.items_per_page - 1) // self.items_per_page
        
        return {
            "scans": scans,
            "total": total,
            "page": page,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        } 