"""Database initialization script for ClearScan."""

import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from clearscan.models import Base, User, Network, Configuration
from clearscan.security import hash_password

def init_database():
    """Initialize the database with required tables and initial data."""
    # Create database engine
    engine = create_engine('sqlite:///clearscan.db')
    
    # Create all tables
    Base.metadata.create_all(engine)
    
    # Create session
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Check if admin user exists
        admin = session.query(User).filter_by(username='admin').first()
        if not admin:
            # Create admin user
            admin_password = os.environ.get('CLEARSCAN_ADMIN_PASSWORD')
            if not admin_password:
                print("Error: CLEARSCAN_ADMIN_PASSWORD environment variable not set")
                sys.exit(1)
            
            admin = User(
                username='admin',
                password_hash=hash_password(admin_password),
                email='admin@localhost',
                role='admin'
            )
            session.add(admin)
        
        # Add default configuration if not exists
        default_configs = {
            'scan_threads': '10',
            'notification_enabled': 'true',
            'telegram_enabled': 'false',
            'email_enabled': 'false',
            'log_level': 'INFO',
            'retention_days': '30'
        }
        
        for key, value in default_configs.items():
            config = session.query(Configuration).filter_by(key=key).first()
            if not config:
                config = Configuration(
                    key=key,
                    value=value,
                    description=f'Default {key} configuration',
                    created_by=1,
                    updated_by=1
                )
                session.add(config)
        
        # Add example network if not exists
        network = session.query(Network).first()
        if not network:
            network = Network(
                name='Local Network',
                ip_range='192.168.1.0/24',
                scan_interval=3600  # 1 hour
            )
            session.add(network)
        
        session.commit()
        print("Database initialized successfully")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        session.rollback()
        sys.exit(1)
        
    finally:
        session.close()

if __name__ == '__main__':
    init_database() 