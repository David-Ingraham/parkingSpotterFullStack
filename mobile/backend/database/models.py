from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Float, ForeignKey, CheckConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.sql import func
from .db import Base

class Camera(Base):
    __tablename__ = 'cameras'
    
    address = Column(String(255), primary_key=True)
    camera_id = Column(String(255), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    last_status = Column(String(50), nullable=True, default=None)
    parked_cars_confidence = Column(Float, nullable=True, default=None)
    open_parking_confidence = Column(Float, nullable=True, default=None)
    
    # Relationships
    watchers = relationship('Watcher', back_populates='camera', cascade='all, delete-orphan')
    status_history = relationship('CameraStatusHistory', back_populates='camera', cascade='all, delete-orphan')

class Watcher(Base):
    __tablename__ = 'watchers'
    
    id = Column(Integer, primary_key=True)
    camera_address = Column(String(255), ForeignKey('cameras.address'))
    client_id = Column(String(255), nullable=False)
    time_to_live = Column(Integer, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_connected = Column(Boolean, default=False)
    
    # Push notification support
    push_token = Column(String(500), nullable=True)
    platform = Column(String(20), nullable=True)  # 'ios' or 'android'
    
    created_at = Column(DateTime(timezone=True), default=func.now())
    
    # Relationships
    camera = relationship('Camera', back_populates='watchers')
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            'time_to_live >= 10 AND time_to_live <= 180 AND time_to_live % 5 = 0',
            name='check_time_to_live'
        ),
        # Prevent duplicate watches
        CheckConstraint(
            'camera_address IS NOT NULL AND client_id IS NOT NULL',
            name='check_required_fields'
        ),
    )

class CameraStatusHistory(Base):
    __tablename__ = 'camera_status_history'
    
    id = Column(Integer, primary_key=True)
    camera_address = Column(String(255), ForeignKey('cameras.address'))
    status = Column(String(50), nullable=False)
    recorded_at = Column(DateTime(timezone=True), default=func.now())
    
    # Relationships
    camera = relationship('Camera', back_populates='status_history')


# Database connection
def init_db(database_url):
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)

# Helper functions for common operations
def get_active_watchers(session):
    """Get all non-expired watchers"""
    return session.query(Watcher).filter(Watcher.expires_at > func.now()).all()

def get_camera_watchers(session, camera_address):
    """Get all active watchers for a specific camera"""
    return session.query(Watcher).filter(
        Watcher.camera_address == camera_address,
        Watcher.expires_at > func.now()
    ).all()

def cleanup_expired_watchers(session):
    """Remove expired watchers"""
    session.query(Watcher).filter(Watcher.expires_at <= func.now()).delete()
    session.commit()

def get_watched_cameras(session):
    """Get all cameras that have at least one active watcher"""
    cleanup_expired_watchers(session)
    return session.query(Camera).join(Watcher).filter(
        Watcher.expires_at > func.now()
    ).distinct().all() 