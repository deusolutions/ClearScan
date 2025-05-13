from datetime import datetime
from typing import List, Optional

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, JSON
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
    cidr = Column(String(50), nullable=False)
    description = Column(String(255))
    scan_interval = Column(Integer, default=3600)  # in seconds
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    created_by_id = Column(Integer, ForeignKey("users.id"))
    
    ports = relationship("Port", back_populates="network")
    scan_results = relationship("ScanResult", back_populates="network")
    created_by = relationship("User")

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
    network_id = Column(Integer, ForeignKey("networks.id"))
    scan_time = Column(DateTime, default=datetime.utcnow)
    results = Column(JSON)
    status = Column(String(20))  # success, failed, partial
    error_message = Column(String(255))

    network = relationship("Network", back_populates="scan_results")

class Configuration(Base):
    __tablename__ = "configurations"

    id = Column(Integer, primary_key=True)
    key = Column(String(50), unique=True, nullable=False)
    value = Column(JSON)
    description = Column(String(255))
    is_encrypted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    updated_by_id = Column(Integer, ForeignKey("users.id"))

    updated_by = relationship("User")

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

class NotificationRule(Base):
    __tablename__ = "notification_rules"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(255))
    event_type = Column(String(50), nullable=False)  # new_host, port_change, etc.
    conditions = Column(JSON)
    actions = Column(JSON)  # telegram, email, webhook, etc.
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    created_by_id = Column(Integer, ForeignKey("users.id"))

    created_by = relationship("User") 