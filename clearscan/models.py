"""
Core database models for ClearScan
Contains only essential models for basic network scanning functionality
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    """Basic user model for authentication."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)

class Network(Base):
    """Network to be scanned."""
    __tablename__ = "networks"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    ip_range = Column(String(50), nullable=False)  # Example: "192.168.1.0/24"
    description = Column(String(255))
    is_active = Column(Boolean, default=True)
    scan_interval = Column(Integer, default=3600)  # Scan interval in seconds
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    scan_results = relationship("ScanResult", back_populates="network", cascade="all, delete-orphan")
    telegram_chats = relationship("TelegramChat", back_populates="network", cascade="all, delete-orphan")

class ScanResult(Base):
    """Network scan results."""
    __tablename__ = "scan_results"

    id = Column(Integer, primary_key=True)
    network_id = Column(Integer, ForeignKey("networks.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    hosts = Column(Text, nullable=False)  # JSON list of hosts
    host_details = Column(Text, nullable=False)  # JSON with host details
    status = Column(String(20), default='completed')  # completed, failed
    error_message = Column(String(255))
    scan_duration = Column(Float)  # Scan duration in seconds
    
    network = relationship("Network", back_populates="scan_results")
    changes = relationship("NetworkChange", back_populates="scan_result")

class NetworkChange(Base):
    """Network changes detected between scans."""
    __tablename__ = "network_changes"
    
    id = Column(Integer, primary_key=True)
    network_id = Column(Integer, ForeignKey("networks.id"), nullable=False)
    scan_id = Column(Integer, ForeignKey("scan_results.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    severity = Column(String(20), nullable=False)  # critical, high, medium, low, info
    changes_detected = Column(Text, nullable=False)  # JSON with detected changes
    message = Column(Text)  # Human-readable change description
    notified = Column(Boolean, default=False)  # Whether Telegram notification was sent
    
    network = relationship("Network")
    scan_result = relationship("ScanResult", back_populates="changes")

class TelegramChat(Base):
    """Telegram chat settings for notifications."""
    __tablename__ = "telegram_chats"
    
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, nullable=False)
    network_id = Column(Integer, ForeignKey("networks.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_notification = Column(DateTime)
    
    network = relationship("Network", back_populates="telegram_chats") 