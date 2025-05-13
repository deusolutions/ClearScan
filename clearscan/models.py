from datetime import datetime
from typing import List, Optional

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(255), unique=True)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)

class Network(Base):
    __tablename__ = "networks"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    ip_range = Column(String(100), nullable=False)
    scan_interval = Column(Integer, default=3600)  # in seconds
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    scans = relationship("ScanResult", back_populates="network")
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
    __tablename__ = "scan_results"

    id = Column(Integer, primary_key=True)
    network_id = Column(Integer, ForeignKey("networks.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    hosts = Column(Text, nullable=False)  # JSON string of host IPs
    host_details = Column(Text, nullable=False)  # JSON string of detailed host info
    scan_duration = Column(Integer)  # in seconds
    
    network = relationship("Network", back_populates="scans")
    changes_as_previous = relationship("NetworkChange", 
                                     foreign_keys="NetworkChange.previous_scan_id",
                                     back_populates="previous_scan")
    changes_as_current = relationship("NetworkChange", 
                                    foreign_keys="NetworkChange.scan_id",
                                    back_populates="current_scan")

class NetworkChange(Base):
    __tablename__ = "network_changes"
    
    id = Column(Integer, primary_key=True)
    network_id = Column(Integer, ForeignKey("networks.id"), nullable=False)
    scan_id = Column(Integer, ForeignKey("scan_results.id"), nullable=False)
    previous_scan_id = Column(Integer, ForeignKey("scan_results.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    severity = Column(String(20), nullable=False)  # high, medium, low, info
    new_hosts = Column(Text)  # JSON string of new hosts
    removed_hosts = Column(Text)  # JSON string of removed hosts
    changed_hosts = Column(Text)  # JSON string of changed hosts and their details
    
    network = relationship("Network", back_populates="changes")
    current_scan = relationship("ScanResult", 
                              foreign_keys=[scan_id],
                              back_populates="changes_as_current")
    previous_scan = relationship("ScanResult", 
                               foreign_keys=[previous_scan_id],
                               back_populates="changes_as_previous")
    notifications = relationship("ChangeNotification", back_populates="change")

class ChangeNotification(Base):
    __tablename__ = "change_notifications"
    
    id = Column(Integer, primary_key=True)
    change_id = Column(Integer, ForeignKey("network_changes.id"), nullable=False)
    severity = Column(String(20), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    message = Column(Text, nullable=False)
    sent = Column(DateTime)  # When the notification was sent
    delivery_status = Column(String(50))  # success, failed, pending
    
    change = relationship("NetworkChange", back_populates="notifications")

class Configuration(Base):
    __tablename__ = "configurations"

    id = Column(Integer, primary_key=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(Text, nullable=False)
    description = Column(Text)
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