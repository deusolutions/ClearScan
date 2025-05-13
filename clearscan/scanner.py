"""
Simple network scanner using nmap
"""

import logging
import json
import time
from datetime import datetime
import nmap
from sqlalchemy.orm import Session

from .models import Network, ScanResult, NetworkChange

logger = logging.getLogger(__name__)

class NetworkScanner:
    def __init__(self, session: Session):
        """Initialize scanner with database session."""
        self.session = session
        self.scanner = nmap.PortScanner()
    
    def scan_network(self, network: Network) -> ScanResult:
        """
        Scan a single network.
        
        Args:
            network: Network to scan
            
        Returns:
            ScanResult object
        """
        logger.info(f"Scanning network {network.name} ({network.ip_range})")
        start_time = time.time()
        
        try:
            # Run basic TCP scan
            self.scanner.scan(
                hosts=network.ip_range,
                arguments='-sS -p 22-25,80,443,3306,5432 --min-rate 1000'
            )
            
            # Process results
            hosts = []
            host_details = {}
            
            for host in self.scanner.all_hosts():
                hosts.append(host)
                host_info = {
                    'status': self.scanner[host].state(),
                    'ports': [],
                    'services': {}
                }
                
                # Get port information
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
            
            # Create scan result
            scan_result = ScanResult(
                network_id=network.id,
                timestamp=datetime.utcnow(),
                hosts=json.dumps(hosts),
                host_details=json.dumps(host_details),
                status='completed',
                scan_duration=time.time() - start_time
            )
            
            return scan_result
            
        except Exception as e:
            logger.error(f"Error scanning network {network.ip_range}: {e}")
            return ScanResult(
                network_id=network.id,
                timestamp=datetime.utcnow(),
                hosts=json.dumps([]),
                host_details=json.dumps({}),
                status='failed',
                error_message=str(e),
                scan_duration=time.time() - start_time
            )
    
    def compare_results(self, prev_scan: ScanResult, curr_scan: ScanResult) -> NetworkChange:
        """Compare two scan results and create change record."""
        if prev_scan.status != 'completed' or curr_scan.status != 'completed':
            return None
            
        prev_hosts = set(json.loads(prev_scan.hosts))
        curr_hosts = set(json.loads(curr_scan.hosts))
        
        new_hosts = curr_hosts - prev_hosts
        removed_hosts = prev_hosts - curr_hosts
        
        if not new_hosts and not removed_hosts:
            return None
            
        changes = {
            'new_hosts': list(new_hosts),
            'removed_hosts': list(removed_hosts)
        }
        
        return NetworkChange(
            network_id=curr_scan.network_id,
            scan_id=curr_scan.id,
            severity='high' if new_hosts else 'medium',
            changes_detected=json.dumps(changes),
            message=self._format_change_message(changes)
        )
    
    def _format_change_message(self, changes: dict) -> str:
        """Format change message for notifications."""
        msg_parts = []
        
        if changes['new_hosts']:
            msg_parts.append(f"New hosts: {', '.join(changes['new_hosts'])}")
        
        if changes['removed_hosts']:
            msg_parts.append(f"Removed hosts: {', '.join(changes['removed_hosts'])}")
        
        return ' | '.join(msg_parts)
    
    def run(self):
        """Main scanning loop."""
        while True:
            try:
                # Get active networks
                networks = self.session.query(Network).filter_by(is_active=True).all()
                
                for network in networks:
                    # Check if it's time to scan
                    last_scan = self.session.query(ScanResult)\
                        .filter_by(network_id=network.id)\
                        .order_by(ScanResult.timestamp.desc())\
                        .first()
                    
                    if last_scan:
                        elapsed = (datetime.utcnow() - last_scan.timestamp).total_seconds()
                        if elapsed < network.scan_interval:
                            continue
                    
                    # Run scan
                    scan_result = self.scan_network(network)
                    self.session.add(scan_result)
                    
                    # Compare with previous scan
                    if last_scan and scan_result.status == 'completed':
                        changes = self.compare_results(last_scan, scan_result)
                        if changes:
                            self.session.add(changes)
                    
                    self.session.commit()
                    
            except Exception as e:
                logger.error(f"Error in scanner loop: {e}")
            
            # Sleep for a minute before next iteration
            time.sleep(60) 