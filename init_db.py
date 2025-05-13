import os
import sys
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from werkzeug.security import generate_password_hash

from clearscan.models import Base, User, Configuration

def init_db():
    # Get admin password from environment
    admin_password = os.environ.get('CLEARSCAN_ADMIN_PASSWORD')
    if not admin_password:
        print("Error: CLEARSCAN_ADMIN_PASSWORD environment variable is not set")
        sys.exit(1)

    # Create database directory if it doesn't exist
    db_dir = "/var/lib/clearscan"
    os.makedirs(db_dir, exist_ok=True)

    # Initialize database
    db_path = os.path.join(db_dir, "clearscan.db")
    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(engine)

    # Create session
    Session = sessionmaker(bind=engine)
    session = Session()

    # Check if admin user exists
    admin = session.query(User).filter_by(username="admin").first()
    if not admin:
        # Create admin user
        admin = User(
            username="admin",
            password_hash=generate_password_hash(admin_password),
            email="admin@localhost",
            is_active=True,
            is_admin=True,
            created_at=datetime.utcnow()
        )
        session.add(admin)

    # Initialize default configurations
    default_configs = {
        "telegram.enabled": {"value": False, "description": "Enable Telegram notifications"},
        "telegram.bot_token": {"value": "", "description": "Telegram Bot Token", "is_encrypted": True},
        "telegram.chat_id": {"value": "", "description": "Telegram Chat ID"},
        "web.port": {"value": 80, "description": "Web interface port"},
        "web.session_timeout": {"value": 3600, "description": "Session timeout in seconds"},
        "scanner.default_interval": {"value": 3600, "description": "Default scan interval in seconds"},
        "scanner.timeout": {"value": 300, "description": "Scanner timeout in seconds"},
        "scanner.max_retries": {"value": 3, "description": "Maximum number of scan retries"},
        "logging.level": {"value": "INFO", "description": "Logging level"},
        "logging.file": {"value": "/var/log/clearscan.log", "description": "Log file path"},
        "security.failed_login_delay": {"value": 5, "description": "Delay after failed login in seconds"},
        "security.max_failed_attempts": {"value": 5, "description": "Maximum failed login attempts before lockout"},
        "security.lockout_duration": {"value": 1800, "description": "Account lockout duration in seconds"},
    }

    for key, config in default_configs.items():
        existing = session.query(Configuration).filter_by(key=key).first()
        if not existing:
            conf = Configuration(
                key=key,
                value=config["value"],
                description=config["description"],
                is_encrypted=config.get("is_encrypted", False),
                created_at=datetime.utcnow(),
                updated_by_id=admin.id
            )
            session.add(conf)

    try:
        session.commit()
        print("Database initialized successfully!")
        print("You can now log in to the web interface with:")
        print("Username: admin")
        print("Password: [the one you set in CLEARSCAN_ADMIN_PASSWORD]")
    except Exception as e:
        print(f"Error initializing database: {e}")
        session.rollback()
        sys.exit(1)
    finally:
        session.close()

if __name__ == "__main__":
    init_db() 