import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock

from werkzeug.security import generate_password_hash

from clearscan.models import User, Configuration
from clearscan.security import SecurityManager

@pytest.fixture
def mock_session():
    session = MagicMock()
    
    # Mock configuration query
    configs = [
        MagicMock(key='security.failed_login_delay', value=5),
        MagicMock(key='security.max_failed_attempts', value=5),
        MagicMock(key='security.lockout_duration', value=1800)
    ]
    session.query.return_value.filter.return_value.all.return_value = configs
    
    return session

@pytest.fixture
def test_user():
    return User(
        id=1,
        username='testuser',
        password_hash=generate_password_hash('password123'),
        email='test@example.com',
        is_active=True,
        is_admin=False,
        created_at=datetime.utcnow()
    )

def test_security_manager_initialization(mock_session):
    manager = SecurityManager(mock_session)
    assert manager.config['failed_login_delay'] == 5
    assert manager.config['max_failed_attempts'] == 5
    assert manager.config['lockout_duration'] == 1800

def test_authenticate_success(mock_session, test_user):
    mock_session.query.return_value.filter_by.return_value.first.return_value = test_user
    
    manager = SecurityManager(mock_session)
    success, user, message = manager.authenticate('testuser', 'password123')
    
    assert success
    assert user == test_user
    assert message == "Authentication successful"
    assert mock_session.commit.called

def test_authenticate_wrong_password(mock_session, test_user):
    mock_session.query.return_value.filter_by.return_value.first.return_value = test_user
    
    manager = SecurityManager(mock_session)
    success, user, message = manager.authenticate('testuser', 'wrongpassword')
    
    assert not success
    assert user is None
    assert message == "Invalid username or password"
    assert mock_session.commit.called

def test_authenticate_user_not_found(mock_session):
    mock_session.query.return_value.filter_by.return_value.first.return_value = None
    
    manager = SecurityManager(mock_session)
    success, user, message = manager.authenticate('nonexistent', 'password123')
    
    assert not success
    assert user is None
    assert message == "Invalid username or password"

def test_authenticate_inactive_user(mock_session, test_user):
    test_user.is_active = False
    mock_session.query.return_value.filter_by.return_value.first.return_value = test_user
    
    manager = SecurityManager(mock_session)
    success, user, message = manager.authenticate('testuser', 'password123')
    
    assert not success
    assert user is None
    assert message == "Account is inactive"

def test_authenticate_locked_account(mock_session, test_user):
    test_user.last_login = datetime.utcnow()
    mock_session.query.return_value.filter_by.return_value.first.return_value = test_user
    
    manager = SecurityManager(mock_session)
    success, user, message = manager.authenticate('testuser', 'password123')
    
    assert not success
    assert user is None
    assert "Account is locked until" in message

def test_change_password_success(mock_session, test_user):
    manager = SecurityManager(mock_session)
    success, message = manager.change_password(test_user, 'password123', 'newpassword')
    
    assert success
    assert message == "Password changed successfully"
    assert mock_session.commit.called

def test_change_password_wrong_current(mock_session, test_user):
    manager = SecurityManager(mock_session)
    success, message = manager.change_password(test_user, 'wrongpassword', 'newpassword')
    
    assert not success
    assert message == "Current password is incorrect"

def test_create_user_success(mock_session):
    mock_session.query.return_value.filter_by.return_value.first.return_value = None
    
    manager = SecurityManager(mock_session)
    success, user, message = manager.create_user('newuser', 'password123')
    
    assert success
    assert user is not None
    assert message == "User created successfully"
    assert mock_session.add.called
    assert mock_session.commit.called

def test_create_user_existing_username(mock_session, test_user):
    mock_session.query.return_value.filter_by.return_value.first.return_value = test_user
    
    manager = SecurityManager(mock_session)
    success, user, message = manager.create_user('testuser', 'password123')
    
    assert not success
    assert user is None
    assert message == "Username already exists"

def test_deactivate_user_success(mock_session, test_user):
    manager = SecurityManager(mock_session)
    success, message = manager.deactivate_user(test_user)
    
    assert success
    assert message == "User deactivated successfully"
    assert not test_user.is_active
    assert mock_session.commit.called 