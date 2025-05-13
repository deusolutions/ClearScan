"""Entry point for running the Telegram bot."""

import os
import sys
import logging
import yaml
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .bot import ClearScanBot
from ..models import Base

def main():
    """Main entry point for the Telegram bot."""
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    # Load configuration
    try:
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        logger.error("Configuration file 'config.yaml' not found")
        sys.exit(1)
    except yaml.YAMLError as e:
        logger.error(f"Error parsing configuration file: {e}")
        sys.exit(1)
        
    # Check for bot token
    bot_token = config['telegram'].get('token')
    if not bot_token:
        logger.error("Telegram bot token not found in configuration")
        sys.exit(1)
        
    # Set up database connection
    try:
        engine = create_engine(config['database']['url'])
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        sys.exit(1)
        
    # Create and start the bot
    try:
        bot = ClearScanBot(bot_token, session)
        logger.info("Starting Telegram bot...")
        bot.run()
    except Exception as e:
        logger.error(f"Failed to start Telegram bot: {e}")
        sys.exit(1)
    finally:
        session.close()

if __name__ == '__main__':
    main() 