import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch

from clearscan.models import Network, Port, ScanResult, Configuration
from clearscan.scanner import NetworkScanner

@pytest.fixture
def mock_session():
    session = MagicMock()
    
    # Mock configuration query
    configs = [
        MagicMock(key='scanner.timeout', value=300),
        MagicMock(key='scanner.max_retries', value=3)
    ]
    session.query.return_value.filter.return_value.all.return_value = configs
    
    return session

@pytest.fixture
def test_network():
    network = Network(
        id=1,
        cidr='192.168.1.0/24',
        description='Test network',
        scan_interval=3600,
        is_active=True,
        created_at=datetime.utcnow()
    )
    
    # Add test ports
    network.ports = [
        Port(port_number=80, protocol='tcp', is_active=True),
        Port(port_number=443, protocol='tcp', is_active=True),
        Port(port_number=22, protocol='tcp', is_active=False)
    ]
    
    return network

def test_scanner_initialization(mock_session):
    scanner = NetworkScanner(mock_session)
    assert scanner.config['timeout'] == 300
    assert scanner.config['max_retries'] == 3

@patch('nmap.PortScanner')
def test_scan_network_success(mock_nmap, mock_session, test_network):
    # Mock nmap scan results
    mock_scan_result = {
        'scan': {
            '192.168.1.1': {
                'status': {'state': 'up'},
                'hostnames': [{'name': 'router.local'}],
                'tcp': {
                    80: {
                        'state': 'open',
                        'name': 'http',
                        'version': 'nginx'
                    },
                    443: {
                        'state': 'open',
                        'name': 'https',
                        'version': ''
                    }
                }
            }
        }
    }
    
    mock_nmap_instance = MagicMock()
    mock_nmap_instance.scan.return_value = mock_scan_result
    mock_nmap.return_value = mock_nmap_instance
    
    scanner = NetworkScanner(mock_session)
    result = scanner.scan_network(test_network)
    
    assert result.status == 'success'
    assert result.network_id == test_network.id
    assert '192.168.1.1' in result.results
    assert result.results['192.168.1.1']['ports']['80']['state'] == 'open'
    assert result.results['192.168.1.1']['ports']['443']['state'] == 'open'

@patch('nmap.PortScanner')
def test_scan_network_no_ports(mock_nmap, mock_session):
    network = Network(
        id=2,
        cidr='192.168.2.0/24',
        description='Test network without ports',
        is_active=True,
        ports=[]
    )
    
    scanner = NetworkScanner(mock_session)
    result = scanner.scan_network(network)
    
    assert result.status == 'failed'
    assert result.error_message == 'No ports configured'
    assert not result.results

@patch('nmap.PortScanner')
def test_scan_network_error(mock_nmap, mock_session, test_network):
    mock_nmap_instance = MagicMock()
    mock_nmap_instance.scan.side_effect = Exception('Scan failed')
    mock_nmap.return_value = mock_nmap_instance
    
    scanner = NetworkScanner(mock_session)
    result = scanner.scan_network(test_network)
    
    assert result.status == 'failed'
    assert result.error_message == 'Scan failed'
    assert not result.results

def test_scan_all_active_networks(mock_session):
    networks = [
        Network(id=1, cidr='192.168.1.0/24', is_active=True),
        Network(id=2, cidr='192.168.2.0/24', is_active=True),
        Network(id=3, cidr='192.168.3.0/24', is_active=False)
    ]
    mock_session.query.return_value.filter_by.return_value.all.return_value = networks
    
    scanner = NetworkScanner(mock_session)
    with patch.object(scanner, 'scan_network') as mock_scan:
        mock_scan.return_value = MagicMock(status='success')
        results = scanner.scan_all_active_networks()
        
        assert len(results) == 2  # Only active networks
        mock_scan.assert_called()
        assert mock_scan.call_count == 2 