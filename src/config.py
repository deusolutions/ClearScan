import yaml
import os

DATABASE_PATH = '/opt/clearscan/clearscan.db'  # unified DB path for Linux
SCAN_INTERVAL = 3600  # in seconds
NMAP_PATH = '/usr/bin/nmap'  # Adjust if nmap is installed in a different
# location

CONFIG_PATH = '/opt/clearscan/config.yaml'
if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, 'r') as f:
        config = yaml.safe_load(f)
    HTTP_AUTH_USERNAME = config.get('http_auth_username', 'admin')
    HTTP_AUTH_PASSWORD = config.get('http_auth_password', 'password')
    TELEGRAM_BOT_TOKEN = config.get('telegram_bot_token')
    if not TELEGRAM_BOT_TOKEN:
        raise ValueError("telegram_bot_token not found in config.yaml")
    ALLOWED_USERS = set(config.get('allowed_users', []))
    if not ALLOWED_USERS:
        raise ValueError("allowed_users not found in config.yaml")
else:
    HTTP_AUTH_USERNAME = 'admin'
    HTTP_AUTH_PASSWORD = 'password'
    raise ValueError(f"Config file not found at {CONFIG_PATH}")
