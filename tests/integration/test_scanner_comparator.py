"""Integration tests for scanner and comparator modules."""

import os
import json
import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from clearscan.models import Base, Network, ScanResult, NetworkChange
from clearscan.scanner import NetworkScanner
from clearscan.comparator import ResultsComparator

@pytest.fixture(scope="module")
def db_engine():
    """Create a test database."""
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    return engine

@pytest.fixture
def db_session(db_engine):
    """Create a new database session for a test."""
    Session = sessionmaker(bind=db_engine)
    session = Session()
    yield session
    session.rollback()
    session.close()

@pytest.fixture
def network(db_session):
    """Create a test network."""
    network = Network(
        name='Test Network',
        ip_range='127.0.0.1/32',  # Just localhost for testing
        scan_interval=3600
    )
    db_session.add(network)
    db_session.commit()
    return network

@pytest.fixture
def scanner(db_session):
    """Create a NetworkScanner instance."""
    return NetworkScanner(db_session)

@pytest.fixture
def comparator(db_session):
    """Create a ResultsComparator instance."""
    return ResultsComparator(db_session)

def create_scan_result(db_session, network_id, hosts, host_details, timestamp=None):
    """Helper function to create a scan result."""
    if timestamp is None:
        timestamp = datetime.utcnow()
    
    result = ScanResult(
        network_id=network_id,
        timestamp=timestamp,
        hosts=json.dumps(hosts),
        host_details=json.dumps(host_details),
        scan_duration=1
    )
    db_session.add(result)
    db_session.commit()
    return result

def test_scan_and_compare_no_changes(db_session, network, scanner, comparator):
    """Test scanning and comparing with no network changes."""
    # Create initial scan
    hosts = ['127.0.0.1']
    host_details = {
        '127.0.0.1': {
            'ports': [80],
            'services': {'80': 'http'}
        }
    }
    prev_scan = create_scan_result(
        db_session, 
        network.id,
        hosts,
        host_details,
        datetime.utcnow() - timedelta(hours=1)
    )
    
    # Create current scan with same data
    curr_scan = create_scan_result(
        db_session,
        network.id,
        hosts,
        host_details
    )
    
    # Compare scans
    changes = comparator.compare_scans(prev_scan, curr_scan)
    
    # Verify no changes detected
    assert not json.loads(changes.new_hosts)
    assert not json.loads(changes.removed_hosts)
    assert not json.loads(changes.changed_hosts)
    assert changes.severity == 'info'

def test_scan_and_compare_with_changes(db_session, network, scanner, comparator):
    """Test scanning and comparing with network changes."""
    # Create initial scan
    prev_hosts = ['127.0.0.1']
    prev_details = {
        '127.0.0.1': {
            'ports': [80],
            'services': {'80': 'http'}
        }
    }
    prev_scan = create_scan_result(
        db_session,
        network.id,
        prev_hosts,
        prev_details,
        datetime.utcnow() - timedelta(hours=1)
    )
    
    # Create current scan with changes
    curr_hosts = ['127.0.0.1', '127.0.0.2']
    curr_details = {
        '127.0.0.1': {
            'ports': [80, 443],
            'services': {
                '80': 'http',
                '443': 'https'
            }
        },
        '127.0.0.2': {
            'ports': [22],
            'services': {'22': 'ssh'}
        }
    }
    curr_scan = create_scan_result(
        db_session,
        network.id,
        curr_hosts,
        curr_details
    )
    
    # Compare scans
    changes = comparator.compare_scans(prev_scan, curr_scan)
    
    # Verify changes
    assert json.loads(changes.new_hosts) == ['127.0.0.2']
    assert not json.loads(changes.removed_hosts)
    
    changed_hosts = json.loads(changes.changed_hosts)
    assert '127.0.0.1' in changed_hosts
    assert 443 in changed_hosts['127.0.0.1']['new_ports']
    assert 'https' in changed_hosts['127.0.0.1']['service_changes']['443']['added']

def test_scan_and_compare_large_network(db_session, network, scanner, comparator):
    """Test scanning and comparing with a large number of hosts."""
    # Create initial scan with 100 hosts
    prev_hosts = [f'192.168.1.{i}' for i in range(100)]
    prev_details = {
        host: {
            'ports': [80],
            'services': {'80': 'http'}
        }
        for host in prev_hosts
    }
    prev_scan = create_scan_result(
        db_session,
        network.id,
        prev_hosts,
        prev_details,
        datetime.utcnow() - timedelta(hours=1)
    )
    
    # Create current scan with 50 changes
    curr_hosts = [f'192.168.1.{i}' for i in range(50, 150)]  # 50 removed, 50 added
    curr_details = {
        host: {
            'ports': [80, 443] if i % 2 == 0 else [80],  # Add 443 to half the hosts
            'services': {
                '80': 'http',
                '443': 'https'
            } if i % 2 == 0 else {'80': 'http'}
        }
        for i, host in enumerate(curr_hosts)
    }
    curr_scan = create_scan_result(
        db_session,
        network.id,
        curr_hosts,
        curr_details
    )
    
    # Compare scans
    changes = comparator.compare_scans(prev_scan, curr_scan)
    
    # Verify changes
    new_hosts = json.loads(changes.new_hosts)
    removed_hosts = json.loads(changes.removed_hosts)
    changed_hosts = json.loads(changes.changed_hosts)
    
    assert len(new_hosts) == 50  # 50 new hosts
    assert len(removed_hosts) == 50  # 50 removed hosts
    assert changes.severity == 'high'  # Due to large number of changes

def test_concurrent_scans_and_compares(db_session, network, scanner, comparator):
    """Test handling multiple scans and comparisons concurrently."""
    from concurrent.futures import ThreadPoolExecutor
    import threading
    
    def scan_and_compare():
        """Perform scan and comparison in a thread."""
        thread_id = threading.get_ident()
        hosts = [f'192.168.1.{thread_id % 255}']
        details = {
            hosts[0]: {
                'ports': [80],
                'services': {'80': 'http'}
            }
        }
        
        # Create two scans and compare them
        prev_scan = create_scan_result(
            db_session,
            network.id,
            hosts,
            details,
            datetime.utcnow() - timedelta(seconds=1)
        )
        
        curr_scan = create_scan_result(
            db_session,
            network.id,
            hosts,
            details
        )
        
        return comparator.compare_scans(prev_scan, curr_scan)
    
    # Run 10 concurrent scans and comparisons
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(scan_and_compare) for _ in range(10)]
        results = [f.result() for f in futures]
    
    # Verify all comparisons completed successfully
    assert len(results) == 10
    assert all(isinstance(r, NetworkChange) for r in results)

def test_performance_optimization(db_session, network, scanner, comparator):
    """Test performance optimization for large networks."""
    import time
    
    # Create initial scan with 1000 hosts
    prev_hosts = [f'192.168.1.{i}' for i in range(1000)]
    prev_details = {
        host: {
            'ports': list(range(1, 101)),  # 100 ports per host
            'services': {str(port): f'service_{port}' for port in range(1, 101)}
        }
        for host in prev_hosts
    }
    prev_scan = create_scan_result(
        db_session,
        network.id,
        prev_hosts,
        prev_details,
        datetime.utcnow() - timedelta(hours=1)
    )
    
    # Create current scan with small changes
    curr_hosts = prev_hosts.copy()
    curr_details = prev_details.copy()
    # Modify 10 hosts
    for i in range(10):
        host = f'192.168.1.{i}'
        curr_details[host]['ports'].append(8080)
        curr_details[host]['services']['8080'] = 'http-alt'
    
    curr_scan = create_scan_result(
        db_session,
        network.id,
        curr_hosts,
        curr_details
    )
    
    # Measure comparison time
    start_time = time.time()
    changes = comparator.compare_scans(prev_scan, curr_scan)
    end_time = time.time()
    
    # Verify performance
    comparison_time = end_time - start_time
    assert comparison_time < 1.0  # Should complete in less than 1 second
    
    # Verify accuracy
    changed_hosts = json.loads(changes.changed_hosts)
    assert len(changed_hosts) == 10  # Only 10 hosts should be marked as changed
    assert all('8080' in details['service_changes'] 
              for details in changed_hosts.values()) 