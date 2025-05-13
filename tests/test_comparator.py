"""Tests for the Results Comparator module."""

import json
from datetime import datetime
import pytest
from unittest.mock import Mock, patch
from clearscan.comparator import ResultsComparator
from clearscan.models import ScanResult, NetworkChange, ChangeNotification

@pytest.fixture
def db_session():
    """Create a mock database session."""
    return Mock()

@pytest.fixture
def comparator(db_session):
    """Create a ResultsComparator instance."""
    return ResultsComparator(db_session)

@pytest.fixture
def previous_scan():
    """Create a mock previous scan result."""
    return ScanResult(
        id=1,
        network_id=1,
        timestamp=datetime.utcnow(),
        hosts=json.dumps(['192.168.1.1', '192.168.1.2']),
        host_details=json.dumps({
            '192.168.1.1': {
                'ports': [80, 443],
                'services': {
                    '80': 'http',
                    '443': 'https'
                }
            },
            '192.168.1.2': {
                'ports': [22],
                'services': {
                    '22': 'ssh'
                }
            }
        })
    )

@pytest.fixture
def current_scan():
    """Create a mock current scan result."""
    return ScanResult(
        id=2,
        network_id=1,
        timestamp=datetime.utcnow(),
        hosts=json.dumps(['192.168.1.1', '192.168.1.3']),
        host_details=json.dumps({
            '192.168.1.1': {
                'ports': [80, 443, 8080],
                'services': {
                    '80': 'http',
                    '443': 'https-new',
                    '8080': 'http-alt'
                }
            },
            '192.168.1.3': {
                'ports': [22, 80],
                'services': {
                    '22': 'ssh',
                    '80': 'http'
                }
            }
        })
    )

def test_find_new_hosts(comparator, previous_scan, current_scan):
    """Test finding new hosts between scans."""
    new_hosts = comparator._find_new_hosts(previous_scan, current_scan)
    assert new_hosts == {'192.168.1.3'}

def test_find_removed_hosts(comparator, previous_scan, current_scan):
    """Test finding removed hosts between scans."""
    removed_hosts = comparator._find_removed_hosts(previous_scan, current_scan)
    assert removed_hosts == {'192.168.1.2'}

def test_find_changed_hosts(comparator, previous_scan, current_scan):
    """Test finding changed hosts between scans."""
    changed_hosts = comparator._find_changed_hosts(previous_scan, current_scan)
    assert '192.168.1.1' in changed_hosts
    assert 'new_ports' in changed_hosts['192.168.1.1']
    assert 8080 in changed_hosts['192.168.1.1']['new_ports']
    assert 'service_changes' in changed_hosts['192.168.1.1']
    assert '443' in changed_hosts['192.168.1.1']['service_changes']

def test_compare_host_details(comparator):
    """Test comparing details of a single host."""
    prev_details = {
        'ports': [80, 443],
        'services': {
            '80': 'http',
            '443': 'https'
        }
    }
    curr_details = {
        'ports': [80, 443, 8080],
        'services': {
            '80': 'http',
            '443': 'https-new',
            '8080': 'http-alt'
        }
    }
    
    changes = comparator._compare_host_details(prev_details, curr_details)
    assert changes['new_ports'] == [8080]
    assert '443' in changes['service_changes']
    assert changes['service_changes']['443']['old'] == 'https'
    assert changes['service_changes']['443']['new'] == 'https-new'

def test_calculate_severity(comparator):
    """Test severity calculation based on changes."""
    new_hosts = {'192.168.1.3'}
    removed_hosts = {'192.168.1.2'}
    changed_hosts = {
        '192.168.1.1': {
            'new_ports': [8080],
            'service_changes': {
                '443': {
                    'old': 'https',
                    'new': 'https-new'
                }
            }
        }
    }
    
    severity = comparator._calculate_severity(new_hosts, removed_hosts, changed_hosts)
    assert severity == 'low'  # 3 total changes (1 new, 1 removed, 1 changed)

def test_compare_scans(comparator, previous_scan, current_scan):
    """Test full scan comparison functionality."""
    changes = comparator.compare_scans(previous_scan, current_scan)
    
    assert isinstance(changes, NetworkChange)
    assert changes.network_id == current_scan.network_id
    assert changes.scan_id == current_scan.id
    assert changes.previous_scan_id == previous_scan.id
    
    new_hosts = json.loads(changes.new_hosts)
    removed_hosts = json.loads(changes.removed_hosts)
    changed_hosts = json.loads(changes.changed_hosts)
    
    assert '192.168.1.3' in new_hosts
    assert '192.168.1.2' in removed_hosts
    assert '192.168.1.1' in changed_hosts

def test_create_change_notification(comparator):
    """Test creation of change notifications."""
    change = NetworkChange(
        id=1,
        network_id=1,
        scan_id=2,
        previous_scan_id=1,
        timestamp=datetime.utcnow(),
        severity='medium',
        new_hosts=json.dumps(['192.168.1.3']),
        removed_hosts=json.dumps(['192.168.1.2']),
        changed_hosts=json.dumps({
            '192.168.1.1': {
                'new_ports': [8080],
                'service_changes': {
                    '443': {
                        'old': 'https',
                        'new': 'https-new'
                    }
                }
            }
        })
    )
    
    notification = comparator.create_change_notification(change)
    
    assert isinstance(notification, ChangeNotification)
    assert notification.change_id == change.id
    assert notification.severity == change.severity
    assert 'New hosts detected' in notification.message
    assert '192.168.1.3' in notification.message
    assert '192.168.1.2' in notification.message
    assert '192.168.1.1' in notification.message
    assert 'https → https-new' in notification.message 