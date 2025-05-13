"""
Database models for ClearScan
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    """Модель пользователя."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(100), unique=True)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    failed_attempts = Column(Integer, default=0)
    is_locked = Column(Boolean, default=False)
    locked_until = Column(DateTime)

class Network(Base):
    """Модель сети для сканирования."""
    __tablename__ = "networks"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    ip_range = Column(String(50), nullable=False)
    description = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    scan_interval = Column(Integer, default=3600)  # интервал сканирования в секундах

    # Связи
    scan_results = relationship("ScanResult", back_populates="network")
    changes = relationship("NetworkChange", back_populates="network")
    telegram_chats = relationship("TelegramChat", back_populates="network")

class Port(Base):
    __tablename__ = "ports"

    id = Column(Integer, primary_key=True)
    network_id = Column(Integer, ForeignKey("networks.id"))
    port_number = Column(Integer, nullable=False)
    protocol = Column(String(10), default="tcp")
    description = Column(String(255))
    is_active = Column(Boolean, default=True)

    network = relationship("Network", back_populates="ports")

class ScanResult(Base):
    """Модель результатов сканирования."""
    __tablename__ = "scan_results"

    id = Column(Integer, primary_key=True)
    network_id = Column(Integer, ForeignKey("networks.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    hosts = Column(Text, nullable=False)  # JSON список хостов
    host_details = Column(Text, nullable=False)  # JSON с деталями хостов
    status = Column(String(20), default='completed')
    error_message = Column(String(255))
    
    network = relationship("Network", back_populates="scan_results")
    changes = relationship("NetworkChange", back_populates="scan_result")

class NetworkChange(Base):
    """Модель изменений в сети."""
    __tablename__ = "network_changes"
    
    id = Column(Integer, primary_key=True)
    network_id = Column(Integer, ForeignKey("networks.id"), nullable=False)
    scan_id = Column(Integer, ForeignKey("scan_results.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    severity = Column(String(20), nullable=False)  # critical, high, medium, low, info
    new_hosts = Column(Text)  # JSON список новых хостов
    removed_hosts = Column(Text)  # JSON список удаленных хостов
    changed_hosts = Column(Text)  # JSON с изменениями на хостах
    message = Column(Text)  # Человекочитаемое описание изменений
    
    network = relationship("Network", back_populates="changes")
    scan_result = relationship("ScanResult", back_populates="changes")
    notifications = relationship("ChangeNotification", back_populates="change")

class ChangeNotification(Base):
    """Модель уведомлений об изменениях."""
    __tablename__ = "change_notifications"
    
    id = Column(Integer, primary_key=True)
    change_id = Column(Integer, ForeignKey("network_changes.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    notification_type = Column(String(20), default='telegram')  # telegram, email, etc.
    status = Column(String(20), default='pending')  # pending, sent, failed
    error_message = Column(String(255))
    
    change = relationship("NetworkChange", back_populates="notifications")

class Configuration(Base):
    """Модель конфигурации."""
    __tablename__ = "configurations"

    id = Column(Integer, primary_key=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(String(255))
    description = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))
    updated_by = Column(Integer, ForeignKey("users.id"))

class ConfigurationHistory(Base):
    __tablename__ = "configuration_history"

    id = Column(Integer, primary_key=True)
    config_key = Column(String(50), nullable=False)
    old_value = Column(JSON)
    new_value = Column(JSON)
    changed_at = Column(DateTime, default=datetime.utcnow)
    changed_by_id = Column(Integer, ForeignKey("users.id"))
    change_reason = Column(String(255))

    changed_by = relationship("User")

class TelegramChat(Base):
    __tablename__ = "telegram_chats"
    
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, nullable=False)
    network_id = Column(Integer, ForeignKey("networks.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_notification = Column(DateTime)
    
    network = relationship("Network", back_populates="telegram_chats")
    
    class Config:
        orm_mode = True 