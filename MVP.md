# ClearScan MVP Goals

## Core Purpose
ClearScan MVP is focused on providing essential network monitoring capabilities with minimal complexity. The goal is to create a reliable, easy-to-use tool for basic network surveillance and change detection.

## MVP Features

### 1. Network Scanning
- Basic TCP port scanning of defined networks
- Support for common ports (22-25, 80, 443, 3306, 5432)
- Simple scheduling with configurable intervals
- Basic host discovery and service detection

### 2. Change Detection
- Track new and removed hosts
- Basic service change detection
- Simple change severity classification (high/medium)

### 3. Notifications
- Telegram bot integration for alerts
- Basic command set (/start, /help, /status, /networks)
- Real-time notifications for network changes

### 4. Web Interface
- Simple Flask-based dashboard
- Basic network configuration
- View scan results and changes
- Minimal authentication

### 5. Data Storage
- SQLite database for storing:
  - Network definitions
  - Scan results
  - Detected changes

## Out of MVP Scope
The following features are intentionally excluded from MVP:
- Complex role-based access control
- Advanced security features
- Email notifications
- API documentation
- Complex configuration management
- Backup/restore functionality
- Performance tuning options
- Advanced scanning options

## Technical Requirements
- Python 3.8+
- nmap
- Basic system requirements (1GB RAM, 1 CPU core)
- SQLite database
- Telegram bot token

## Success Criteria
The MVP will be considered successful when it can:
1. Reliably scan configured networks
2. Detect and report network changes
3. Send notifications via Telegram
4. Provide basic web interface for configuration
5. Store and retrieve scan results

## Future Considerations
After MVP validation, we can consider adding:
- Advanced security features
- More notification channels
- API access
- Complex scheduling
- Performance optimizations
- Extended scanning capabilities 