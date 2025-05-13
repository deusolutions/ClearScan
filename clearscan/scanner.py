"""
Network Scanner Module

This module handles network scanning using nmap and processes results.
"""

import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Optional
import json
import nmap
from sqlalchemy.orm import Session

from .models import Network, ScanResult, NetworkChange
from .comparator import ResultsComparator

logger = logging.getLogger(__name__)

class NetworkScanner:
    def __init__(self, session: Session, batch_size: int = 1000, timeout: int = 300):
        """
        Initialize network scanner.
        
        Args:
            session: Database session
            batch_size: Number of hosts to scan in each batch
            timeout: Scan timeout in seconds
        """
        self.session = session
        self.batch_size = batch_size
        self.timeout = timeout
        self.scanner = nmap.PortScanner()
        self.comparator = ResultsComparator(session)

    async def scan_all_networks(self) -> List[NetworkChange]:
        """
        Scan all configured networks.
        
        Returns:
            List of NetworkChange objects for detected changes
        """
        changes = []
        networks = self.session.query(Network).filter_by(is_active=True).all()
        
        for network in networks:
            try:
                logger.info(f"Сканирование сети {network.name} ({network.ip_range})")
                scan_result = await self._scan_network(network)
                
                if scan_result:
                    # Получаем предыдущий результат сканирования
                    prev_scan = self.session.query(ScanResult).filter_by(
                        network_id=network.id
                    ).order_by(ScanResult.timestamp.desc()).first()
                    
                    # Сравниваем результаты если есть предыдущее сканирование
                    if prev_scan:
                        change = self.comparator.compare_scans(prev_scan, scan_result)
                        if change:
                            changes.append(change)
                            self.session.add(change)
                    
                    self.session.add(scan_result)
                    self.session.commit()
                    
            except Exception as e:
                logger.error(f"Ошибка сканирования сети {network.name}: {e}")
                continue
                
        return changes

    async def _scan_network(self, network: Network) -> Optional[ScanResult]:
        """
        Scan a single network.
        
        Args:
            network: Network to scan
            
        Returns:
            ScanResult object if successful, None otherwise
        """
        try:
            # Запуск сканирования nmap
            arguments = f"-sS -sV -p- --min-rate 1000 -T4 --max-retries 2 --host-timeout {self.timeout}s"
            self.scanner.scan(hosts=network.ip_range, arguments=arguments)
            
            # Обработка результатов
            hosts = []
            host_details = {}
            
            for host in self.scanner.all_hosts():
                hosts.append(host)
                host_info = {
                    'status': self.scanner[host].state(),
                    'ports': [],
                    'services': {}
                }
                
                # Сбор информации о портах и сервисах
                for proto in self.scanner[host].all_protocols():
                    ports = sorted(self.scanner[host][proto].keys())
                    for port in ports:
                        port_info = self.scanner[host][proto][port]
                        host_info['ports'].append(port)
                        host_info['services'][str(port)] = {
                            'name': port_info['name'],
                            'product': port_info.get('product', ''),
                            'version': port_info.get('version', ''),
                            'state': port_info['state']
                        }
                
                host_details[host] = host_info
            
            # Создание записи результата
            scan_result = ScanResult(
                network_id=network.id,
                timestamp=datetime.utcnow(),
                hosts=json.dumps(hosts),
                host_details=json.dumps(host_details)
            )
            
            return scan_result
            
        except Exception as e:
            logger.error(f"Ошибка сканирования {network.ip_range}: {e}")
            return None

    async def scan_specific_hosts(self, hosts: List[str]) -> Dict:
        """
        Scan specific hosts.
        
        Args:
            hosts: List of host IP addresses to scan
            
        Returns:
            Dictionary with scan results
        """
        results = {}
        for host in hosts:
            try:
                self.scanner.scan(hosts=host, arguments="-sS -sV -p-")
                if self.scanner.all_hosts():
                    results[host] = {
                        'status': self.scanner[host].state(),
                        'ports': list(self.scanner[host]['tcp'].keys()) if 'tcp' in self.scanner[host] else []
                    }
            except Exception as e:
                logger.error(f"Ошибка сканирования хоста {host}: {e}")
                results[host] = {'error': str(e)}
                
        return results 