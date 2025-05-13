"""
Database initialization script for ClearScan
"""

import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from werkzeug.security import generate_password_hash

from clearscan.models import Base, User, Network

def init_db():
    """Initialize the database with basic structure and admin user."""
    # Create database engine
    engine = create_engine('sqlite:///clearscan.db')
    
    # Create all tables
    Base.metadata.create_all(engine)
    
    # Create session
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Check if admin user exists
    admin = session.query(User).filter_by(username='admin').first()
    if not admin:
        # Get admin password from environment or use default (not recommended for production)
        admin_password = os.environ.get('CLEARSCAN_ADMIN_PASSWORD', 'admin')
        
        # Create admin user
        admin = User(
            username='admin',
            password_hash=generate_password_hash(admin_password),
            is_admin=True
        )
        session.add(admin)
        print("Created admin user")
    
    # Add example network if none exists
    if not session.query(Network).first():
        example_network = Network(
            name='Example Network',
            ip_range='192.168.1.0/24',
            description='Example network for testing',
            scan_interval=3600  # 1 hour
        )
        session.add(example_network)
        print("Added example network")
    
    # Commit changes
    try:
        session.commit()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Error initializing database: {e}")
        session.rollback()
        sys.exit(1)
    finally:
        session.close()

if __name__ == '__main__':
    print("Initializing ClearScan database...")
    init_db() 