"""
Results Comparator Module

This module provides functionality for comparing network scan results and detecting changes.
It analyzes differences between scans and generates detailed reports of changes.
"""

from typing import Dict, List, Set, Tuple, Optional
from datetime import datetime
import json
from sqlalchemy.orm import Session
from .models import ScanResult, NetworkChange, ChangeNotification
from .security import get_severity_level
import logging

logger = logging.getLogger(__name__)

class ResultsComparator:
    def __init__(self, db_session: Session, batch_size: int = 1000):
        """
        Initialize the comparator with a database session.
        
        Args:
            db_session: SQLAlchemy database session
            batch_size: Number of hosts to process in each batch for large networks
        """
        self.db_session = db_session
        self.batch_size = batch_size

    def compare_scans(self, previous_scan: ScanResult, current_scan: ScanResult) -> NetworkChange:
        """
        Compare two scan results and identify changes.
        
        Args:
            previous_scan: Previous scan result
            current_scan: Current scan result
            
        Returns:
            NetworkChange object containing the detected changes
        """
        try:
            # Compare host states
            new_hosts = self._find_new_hosts(previous_scan, current_scan)
            removed_hosts = self._find_removed_hosts(previous_scan, current_scan)
            changed_hosts = self._find_changed_hosts(previous_scan, current_scan)
            
            # Create NetworkChange object
            changes = NetworkChange(
                network_id=current_scan.network_id,
                scan_id=current_scan.id,
                previous_scan_id=previous_scan.id,
                timestamp=datetime.utcnow(),
                new_hosts=json.dumps(list(new_hosts)),
                removed_hosts=json.dumps(list(removed_hosts)),
                changed_hosts=json.dumps(changed_hosts)
            )
            
            # Set severity based on changes
            changes.severity = self._calculate_severity(new_hosts, removed_hosts, changed_hosts)
            
            return changes
        except Exception as e:
            logger.error(f"Ошибка сравнения результатов сканирования: {e}")
            return None

    def _find_new_hosts(self, previous: ScanResult, current: ScanResult) -> Set[str]:
        """Find hosts that appear in current scan but not in previous."""
        prev_hosts = set(json.loads(previous.hosts))
        curr_hosts = set(json.loads(current.hosts))
        return curr_hosts - prev_hosts

    def _find_removed_hosts(self, previous: ScanResult, current: ScanResult) -> Set[str]:
        """Find hosts that appear in previous scan but not in current."""
        prev_hosts = set(json.loads(previous.hosts))
        curr_hosts = set(json.loads(current.hosts))
        return prev_hosts - curr_hosts

    def _find_changed_hosts(self, previous: ScanResult, current: ScanResult) -> Dict[str, Dict]:
        """Find hosts that exist in both scans but have changes."""
        changes = {}
        prev_details = json.loads(previous.host_details)
        curr_details = json.loads(current.host_details)
        
        # Get hosts that exist in both scans
        common_hosts = set(prev_details.keys()) & set(curr_details.keys())
        
        # Process hosts in batches
        for i in range(0, len(common_hosts), self.batch_size):
            batch_hosts = list(common_hosts)[i:i + self.batch_size]
            for host in batch_hosts:
                host_changes = self._compare_host_details(
                    prev_details[host],
                    curr_details[host]
                )
                if host_changes:
                    changes[host] = host_changes
                
        return changes

    def _compare_host_details(self, prev_details: Dict, curr_details: Dict) -> Optional[Dict]:
        """Compare details of a single host."""
        changes = {}
        
        # Compare ports
        prev_ports = set(prev_details.get('ports', []))
        curr_ports = set(curr_details.get('ports', []))
        
        new_ports = curr_ports - prev_ports
        if new_ports:
            changes['new_ports'] = sorted(list(new_ports))
        
        # Compare services
        prev_services = prev_details.get('services', {})
        curr_services = curr_details.get('services', {})
        service_changes = {}
        
        for port in set(prev_services.keys()) | set(curr_services.keys()):
            if port not in prev_services:
                service_changes[port] = {
                    'added': curr_services[port]
                }
            elif port not in curr_services:
                service_changes[port] = {
                    'removed': prev_services[port]
                }
            elif prev_services[port] != curr_services[port]:
                service_changes[port] = {
                    'old': prev_services[port],
                    'new': curr_services[port]
                }
        
        if service_changes:
            changes['service_changes'] = service_changes
        
        return changes if changes else None

    def _calculate_severity(self, new_hosts: Set[str], removed_hosts: Set[str], 
                          changed_hosts: Dict) -> str:
        """Calculate severity level of changes."""
        total_changes = len(new_hosts) + len(removed_hosts)
        
        # Count significant changes
        critical_changes = 0
        for host_changes in changed_hosts.values():
            if 'new_ports' in host_changes:
                total_changes += len(host_changes['new_ports'])
                # New ports on existing hosts are considered critical
                critical_changes += len(host_changes['new_ports'])
        
        return get_severity_level(total_changes, critical_changes)

    def create_change_notification(self, change: NetworkChange) -> ChangeNotification:
        """Create a notification for detected changes."""
        notification = ChangeNotification(
            change_id=change.id,
            severity=change.severity,
            timestamp=datetime.utcnow(),
            message=self._generate_change_message(change)
        )
        return notification

    def _generate_change_message(self, change: NetworkChange) -> str:
        """Generate a human-readable message describing the changes."""
        new_hosts = json.loads(change.new_hosts)
        removed_hosts = json.loads(change.removed_hosts)
        changed_hosts = json.loads(change.changed_hosts)
        
        messages = []
        
        # Add summary counts
        total_changes = len(new_hosts) + len(removed_hosts) + len(changed_hosts)
        messages.append(f"Total changes detected: {total_changes}")
        
        if new_hosts:
            messages.append(f"New hosts detected ({len(new_hosts)}): {', '.join(sorted(new_hosts))}")
        if removed_hosts:
            messages.append(f"Hosts no longer responding ({len(removed_hosts)}): {', '.join(sorted(removed_hosts))}")
        
        if changed_hosts:
            messages.append(f"\nDetailed changes for {len(changed_hosts)} hosts:")
            for host in sorted(changed_hosts.keys()):
                details = changed_hosts[host]
                host_changes = []
                
                if 'new_ports' in details:
                    host_changes.append(f"new ports: {', '.join(map(str, sorted(details['new_ports'])))}")
                
                if 'service_changes' in details:
                    for port, change_info in sorted(details['service_changes'].items()):
                        if isinstance(change_info, dict) and 'old' in change_info:
                            host_changes.append(
                                f"service on port {port}: {change_info['old']} → {change_info['new']}"
                            )
                        else:
                            host_changes.append(f"new service on port {port}: {change_info}")
                
                if host_changes:
                    messages.append(f"\n{host}:\n- " + "\n- ".join(host_changes))
        
        return "\n".join(messages) 