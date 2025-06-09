import yaml
from typing import List, Dict, Any

class Config:
    def __init__(self, config_path: str = 'config.yaml'):
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Загрузка конфигурации из YAML файла"""
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Конфигурационный файл {self.config_path} не найден")
        except yaml.YAMLError as e:
            raise ValueError(f"Ошибка в формате YAML файла: {e}")

    @property
    def subnets(self) -> List[str]:
        """Получение списка подсетей для сканирования"""
        return self.config.get('subnets', [])

    @property
    def ports(self) -> List[int]:
        """Получение списка портов для сканирования"""
        return self.config.get('ports', [])

    @property
    def scan_interval_minutes(self) -> int:
        """Получение интервала сканирования в минутах"""
        return self.config.get('scan_interval_minutes', 60) 