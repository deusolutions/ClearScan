import yaml
import os

DATABASE_PATH = '/opt/clearscan/clearscan.db'  # unified DB path for Linux
TELEGRAM_BOT_TOKEN = 'your_telegram_bot_token'
SCAN_INTERVAL = 3600  # in seconds
NMAP_PATH = '/usr/bin/nmap'  # Adjust if nmap is installed in a different
# location

CONFIG_PATH = '/opt/clearscan/config.yaml'
if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, 'r') as f:
        config = yaml.safe_load(f)
    HTTP_AUTH_USERNAME = config.get('http_auth_username', 'admin')
    HTTP_AUTH_PASSWORD = config.get('http_auth_password', 'password')
else:
    HTTP_AUTH_USERNAME = 'admin'
    HTTP_AUTH_PASSWORD = 'password'
