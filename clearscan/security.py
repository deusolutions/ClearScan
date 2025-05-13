import logging
from datetime import datetime, timedelta
from typing import Optional, Tuple

from sqlalchemy.orm import Session
from werkzeug.security import check_password_hash, generate_password_hash

from .models import User, Configuration

logger = logging.getLogger(__name__)

class SecurityManager:
    def __init__(self, session: Session):
        self.session = session
        self._load_config()

    def _load_config(self) -> None:
        """Load security configuration from database."""
        configs = self.session.query(Configuration).filter(
            Configuration.key.in_([
                'security.failed_login_delay',
                'security.max_failed_attempts',
                'security.lockout_duration'
            ])
        ).all()
        
        self.config = {
            'failed_login_delay': 5,  # seconds
            'max_failed_attempts': 5,
            'lockout_duration': 1800,  # 30 minutes
        }
        
        for conf in configs:
            if conf.key == 'security.failed_login_delay':
                self.config['failed_login_delay'] = conf.value
            elif conf.key == 'security.max_failed_attempts':
                self.config['max_failed_attempts'] = conf.value
            elif conf.key == 'security.lockout_duration':
                self.config['lockout_duration'] = conf.value

    def authenticate(self, username: str, password: str) -> Tuple[bool, Optional[User], str]:
        """
        Authenticate a user.
        
        Args:
            username: Username to authenticate
            password: Password to verify
            
        Returns:
            Tuple of (success, user, message)
        """
        user = self.session.query(User).filter_by(username=username).first()
        
        if not user:
            logger.warning(f"Authentication failed: user {username} not found")
            return False, None, "Invalid username or password"
            
        if not user.is_active:
            logger.warning(f"Authentication failed: user {username} is inactive")
            return False, None, "Account is inactive"
            
        # Check if account is locked
        if self._is_account_locked(user):
            lockout_ends = user.last_login + timedelta(seconds=self.config['lockout_duration'])
            return False, None, f"Account is locked until {lockout_ends}"
            
        if check_password_hash(user.password_hash, password):
            # Successful login
            user.last_login = datetime.utcnow()
            self.session.commit()
            return True, user, "Authentication successful"
        else:
            # Failed login
            self._handle_failed_login(user)
            return False, None, "Invalid username or password"

    def _is_account_locked(self, user: User) -> bool:
        """Check if account is locked due to too many failed attempts."""
        if not user.last_login:
            return False
            
        lockout_time = user.last_login + timedelta(seconds=self.config['lockout_duration'])
        return datetime.utcnow() < lockout_time

    def _handle_failed_login(self, user: User) -> None:
        """Handle failed login attempt."""
        # TODO: Implement failed login counter in database
        user.last_login = datetime.utcnow()
        self.session.commit()

    def change_password(self, user: User, current_password: str, new_password: str) -> Tuple[bool, str]:
        """
        Change user's password.
        
        Args:
            user: User instance
            current_password: Current password for verification
            new_password: New password to set
            
        Returns:
            Tuple of (success, message)
        """
        if not check_password_hash(user.password_hash, current_password):
            return False, "Current password is incorrect"
            
        user.password_hash = generate_password_hash(new_password)
        user.last_login = datetime.utcnow()
        self.session.commit()
        
        return True, "Password changed successfully"

    def create_user(
        self,
        username: str,
        password: str,
        email: Optional[str] = None,
        is_admin: bool = False
    ) -> Tuple[bool, Optional[User], str]:
        """
        Create a new user.
        
        Args:
            username: Username for new user
            password: Password for new user
            email: Optional email address
            is_admin: Whether user should have admin privileges
            
        Returns:
            Tuple of (success, user, message)
        """
        existing = self.session.query(User).filter_by(username=username).first()
        if existing:
            return False, None, "Username already exists"
            
        if email:
            existing = self.session.query(User).filter_by(email=email).first()
            if existing:
                return False, None, "Email already exists"
        
        try:
            user = User(
                username=username,
                password_hash=generate_password_hash(password),
                email=email,
                is_active=True,
                is_admin=is_admin,
                created_at=datetime.utcnow()
            )
            self.session.add(user)
            self.session.commit()
            
            return True, user, "User created successfully"
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            self.session.rollback()
            return False, None, f"Error creating user: {str(e)}"

    def deactivate_user(self, user: User) -> Tuple[bool, str]:
        """
        Deactivate a user account.
        
        Args:
            user: User to deactivate
            
        Returns:
            Tuple of (success, message)
        """
        try:
            user.is_active = False
            self.session.commit()
            return True, "User deactivated successfully"
        except Exception as e:
            logger.error(f"Error deactivating user: {str(e)}")
            self.session.rollback()
            return False, f"Error deactivating user: {str(e)}" 