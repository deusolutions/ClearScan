#!/usr/bin/env python3
"""
ClearScan - Network Scanner with Telegram notifications
"""

import os
import sys
import yaml
import logging
from threading import Thread

from clearscan.web import app
from clearscan.scanner import NetworkScanner
from clearscan.bot import TelegramBot

def load_config():
    """Load configuration from config.yaml"""
    try:
        with open('config.yaml', 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        sys.exit(1)

def main():
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Load configuration
    config = load_config()
    
    # Initialize components
    scanner = NetworkScanner()
    bot = TelegramBot(config['telegram']['token'])
    
    # Start Telegram bot in background
    bot_thread = Thread(target=bot.run)
    bot_thread.daemon = True
    bot_thread.start()
    
    # Start scanner in background
    scanner_thread = Thread(target=scanner.run)
    scanner_thread.daemon = True
    scanner_thread.start()
    
    # Run web interface
    app.run(
        host=config['web']['host'],
        port=config['web']['port'],
        debug=config['app']['debug']
    )

if __name__ == '__main__':
    main() 