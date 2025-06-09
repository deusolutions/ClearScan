from typing import List, Dict, Any
import datetime

class Diff:
    def __init__(self):
        self.timestamp = datetime.datetime.now()

    def compare(self, current_scan: List[Dict[str, Any]], 
               previous_scan: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Сравнивает результаты текущего и предыдущего сканирования.
        Возвращает список изменений.
        """
        changes = []
        
        # Создаем словари для быстрого поиска
        current_dict = {
            (scan['ip'], scan['port']): scan['status']
            for scan in current_scan
        }
        
        previous_dict = {
            (scan['ip'], scan['port']): scan['status']
            for scan in previous_scan
        }

        # Проверяем изменения в существующих хостах/портах
        for (ip, port), new_status in current_dict.items():
            if (ip, port) in previous_dict:
                old_status = previous_dict[(ip, port)]
                if old_status != new_status:
                    changes.append({
                        'timestamp': self.timestamp,
                        'ip': ip,
                        'port': port,
                        'old_status': old_status,
                        'new_status': new_status
                    })
            else:
                # Новый хост/порт
                changes.append({
                    'timestamp': self.timestamp,
                    'ip': ip,
                    'port': port,
                    'old_status': 'unknown',
                    'new_status': new_status
                })

        # Проверяем удаленные хосты/порты
        for (ip, port), old_status in previous_dict.items():
            if (ip, port) not in current_dict:
                changes.append({
                    'timestamp': self.timestamp,
                    'ip': ip,
                    'port': port,
                    'old_status': old_status,
                    'new_status': 'closed'
                })

        return changes 