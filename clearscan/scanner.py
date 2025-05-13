import logging
from datetime import datetime
from typing import Dict, List, Optional

import nmap
from sqlalchemy.orm import Session

from .models import Network, Port, ScanResult, Configuration

logger = logging.getLogger(__name__)

class NetworkScanner:
    def __init__(self, session: Session):
        self.session = session
        self.nm = nmap.PortScanner()
        self._load_config()

    def _load_config(self) -> None:
        """Load scanner configuration from database."""
        configs = self.session.query(Configuration).filter(
            Configuration.key.in_([
                'scanner.timeout',
                'scanner.max_retries'
            ])
        ).all()
        
        self.config = {
            'timeout': 300,  # default timeout
            'max_retries': 3,  # default retries
        }
        
        for conf in configs:
            if conf.key == 'scanner.timeout':
                self.config['timeout'] = conf.value
            elif conf.key == 'scanner.max_retries':
                self.config['max_retries'] = conf.value

    def scan_network(self, network: Network) -> ScanResult:
        """
        Scan a network and its configured ports.
        
        Args:
            network: Network model instance to scan
            
        Returns:
            ScanResult instance with scan results
        """
        logger.info(f"Starting scan of network {network.cidr}")
        
        # Get active ports for this network
        active_ports = [p.port_number for p in network.ports if p.is_active]
        if not active_ports:
            logger.warning(f"No active ports configured for network {network.cidr}")
            return self._create_scan_result(network, {}, "failed", "No ports configured")

        try:
            # Convert ports list to nmap format
            ports_str = ",".join(map(str, active_ports))
            
            # Run the scan
            scan_result = self.nm.scan(
                hosts=network.cidr,
                ports=ports_str,
                arguments=f"-sS -n --max-retries {self.config['max_retries']} --host-timeout {self.config['timeout']}s"
            )

            # Process results
            results = self._process_scan_results(scan_result)
            
            # Create and return scan result
            return self._create_scan_result(network, results, "success")

        except Exception as e:
            logger.error(f"Error scanning network {network.cidr}: {str(e)}")
            return self._create_scan_result(network, {}, "failed", str(e))

    def _process_scan_results(self, scan_result: Dict) -> Dict:
        """Process nmap scan results into our format."""
        results = {}
        
        if not scan_result or 'scan' not in scan_result:
            return results

        for host, host_data in scan_result['scan'].items():
            if 'tcp' in host_data:
                results[host] = {
                    'status': host_data.get('status', {}).get('state', 'unknown'),
                    'hostname': host_data.get('hostnames', [{'name': ''}])[0]['name'],
                    'ports': {}
                }
                
                for port, port_data in host_data['tcp'].items():
                    results[host]['ports'][str(port)] = {
                        'state': port_data['state'],
                        'service': port_data['name'],
                        'version': port_data.get('version', ''),
                    }

        return results

    def _create_scan_result(
        self,
        network: Network,
        results: Dict,
        status: str,
        error_message: Optional[str] = None
    ) -> ScanResult:
        """Create and save a scan result."""
        scan_result = ScanResult(
            network_id=network.id,
            scan_time=datetime.utcnow(),
            results=results,
            status=status,
            error_message=error_message
        )
        
        self.session.add(scan_result)
        self.session.commit()
        
        return scan_result

    def scan_all_active_networks(self) -> List[ScanResult]:
        """Scan all active networks."""
        networks = self.session.query(Network).filter_by(is_active=True).all()
        results = []
        
        for network in networks:
            try:
                result = self.scan_network(network)
                results.append(result)
            except Exception as e:
                logger.error(f"Error scanning network {network.cidr}: {str(e)}")
                results.append(
                    self._create_scan_result(network, {}, "failed", str(e))
                )
        
        return results 