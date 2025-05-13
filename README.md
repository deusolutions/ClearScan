# ClearScan

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

ClearScan is an open-source network monitoring solution designed for automated scanning of white-listed IP ranges, with real-time Telegram notifications and a web dashboard.

## Features

- 🔍 Automated network scanning of user-defined IP ranges
- 🔄 Hourly monitoring of changes in network state
- 📱 Real-time notifications via Telegram bot
- �� Web dashboard with configuration management
- 📊 SQLite database for storing scan results and settings
- 🔒 Security-focused design with role-based access control
- ⚙️ Dynamic configuration through web interface
- 📈 Configuration history and audit log
- 💾 Configuration backup and restore

## Requirements

- Ubuntu 22.04 (or compatible Linux distribution)
- Python 3.8+
- 2GB RAM
- 32GB HDD
- 2 CPU cores
- nmap
- UFW (Uncomplicated Firewall)

## Quick Start

```bash
# Clone the repository
git clone https://github.com/deusolutions/ClearScan.git
cd ClearScan

# Install dependencies
pip install -r requirements.txt

# Set initial admin password
export CLEARSCAN_ADMIN_PASSWORD=your_secure_password

# Initialize the application
python init_db.py

# Start the service
sudo systemctl start clearscan
```

## Web Configuration

Access the web interface at `http://your-server:80` and log in with:
- Username: `admin`
- Password: (the one you set in CLEARSCAN_ADMIN_PASSWORD)

### Available Settings

#### Network Configuration
- Add/remove networks to scan
- Configure scan intervals per network
- Set custom ports for scanning
- Configure scan timeout and retry settings

#### Notification Settings
- Telegram bot configuration
- Email notifications (optional)
- Custom notification rules and filters

#### Security Settings
- User management
- Role-based access control
- IP whitelist for web interface
- Authentication settings

#### System Settings
- Database maintenance
- Logging configuration
- Backup and restore
- Performance tuning

## Architecture

ClearScan consists of several key components:

1. Scanner: Network scanning using nmap
2. Comparator: Change detection in network state
3. Database: SQLite storage for results and configuration
4. Telegram Bot: Notifications and command interface
5. Web Dashboard: Flask-based interface with configuration management
6. Scheduler: Dynamic task scheduling based on configuration
7. Logger: System logging with configurable destinations

## API Documentation

The web interface is powered by a RESTful API that can also be used for automation:

```
GET    /api/v1/networks      # List configured networks
POST   /api/v1/networks      # Add new network
DELETE /api/v1/networks/:id  # Remove network
PUT    /api/v1/networks/:id  # Update network settings

GET    /api/v1/config        # Get current configuration
PUT    /api/v1/config        # Update configuration
POST   /api/v1/config/backup # Create configuration backup
POST   /api/v1/config/restore# Restore configuration
```

Full API documentation is available at `/api/docs` after installation.

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## Security

If you discover any security-related issues, please email security@yourdomain.com instead of using the issue tracker.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- 📝 [Issue Tracker](https://github.com/deusolutions/ClearScan/issues)
- 📖 [Documentation](https://github.com/deusolutions/ClearScan/wiki)
- 💬 [Discussions](https://github.com/deusolutions/ClearScan/discussions) 