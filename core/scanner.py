import nmap
import datetime
from typing import List, Dict, Any

class Scanner:
    def __init__(self, subnets: List[str], ports: List[int]):
        self.subnets = subnets
        self.ports = ports
        self.nm = nmap.PortScanner()

    def scan(self) -> List[Dict[str, Any]]:
        """
        Выполняет сканирование указанных подсетей и портов.
        Возвращает список результатов сканирования.
        """
        results = []
        timestamp = datetime.datetime.now()

        for subnet in self.subnets:
            # Формируем строку портов для nmap
            ports_str = ','.join(map(str, self.ports))
            
            # Выполняем сканирование
            self.nm.scan(hosts=subnet, arguments=f'-p {ports_str}')

            # Обрабатываем результаты
            for host in self.nm.all_hosts():
                if 'tcp' in self.nm[host]:
                    for port in self.ports:
                        if str(port) in self.nm[host]['tcp']:
                            status = self.nm[host]['tcp'][str(port)]['state']
                            results.append({
                                'timestamp': timestamp,
                                'ip': host,
                                'port': port,
                                'status': status
                            })

        return results 