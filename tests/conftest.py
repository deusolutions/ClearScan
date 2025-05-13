"""Common test fixtures and utilities."""

import os
import pytest
import asyncio
from datetime import datetime
from typing import Generator, AsyncGenerator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from clearscan.models import Base, User, Network
from clearscan.security import SecurityManager
from clearscan.telegram.bot import ClearScanBot

# Настройка тестовой базы данных
@pytest.fixture(scope="session")
def db_engine():
    """Create a test database engine."""
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    return engine

@pytest.fixture
def db_session(db_engine) -> Generator[Session, None, None]:
    """Create a new database session for a test."""
    Session = sessionmaker(bind=db_engine)
    session = Session()
    
    try:
        yield session
    finally:
        session.rollback()
        session.close()

# Фикстуры для тестовых данных
@pytest.fixture
def test_user(db_session) -> User:
    """Create a test user."""
    security = SecurityManager(db_session)
    user = security.create_user(
        username="test_user",
        password="test_password",
        is_admin=True
    )
    db_session.commit()
    return user

@pytest.fixture
def test_network(db_session) -> Network:
    """Create a test network."""
    network = Network(
        name="Test Network",
        ip_range="127.0.0.1/32",
        description="Test network for unit tests",
        is_active=True,
        scan_interval=3600
    )
    db_session.add(network)
    db_session.commit()
    return network

# Фикстуры для Telegram бота
@pytest.fixture
def telegram_bot(db_session) -> ClearScanBot:
    """Create a test Telegram bot instance."""
    return ClearScanBot(
        token="test_token",
        allowed_chat_ids=["123456789"],
        db_session=db_session
    )

# Утилиты для асинхронного тестирования
@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def async_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create an async database session for tests."""
    engine = create_async_engine('sqlite+aiosqlite:///:memory:')
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session

# Утилиты для работы с временем в тестах
@pytest.fixture
def freeze_time(monkeypatch):
    """Freeze time for tests."""
    frozen_time = datetime(2024, 1, 1, 12, 0, 0)
    
    def mock_datetime_now():
        return frozen_time
    
    monkeypatch.setattr(datetime, 'utcnow', mock_datetime_now)
    return frozen_time

# Настройка временных файлов и директорий
@pytest.fixture
def temp_config(tmp_path):
    """Create a temporary config file."""
    config_path = tmp_path / "config.yaml"
    config_path.write_text("""
telegram:
  token: test_token
  allowed_chat_ids:
    - "123456789"
database:
  url: sqlite:///:memory:
logging:
  level: DEBUG
  file: test.log
    """)
    return config_path

# Очистка после тестов
@pytest.fixture(autouse=True)
def cleanup():
    """Clean up after tests."""
    yield
    # Удаляем временные файлы
    if os.path.exists("test.log"):
        os.remove("test.log") 