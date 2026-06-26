from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from .db import Base

class Camera(Base):
    __tablename__ = "cameras"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    source = Column(String, nullable=False) # e.g. "0" for webcam or RTSP URL or path to video
    is_active = Column(Boolean, default=True)
    threshold = Column(Float, default=70.0, nullable=True)
    zone_min_x = Column(Float, default=0.0, nullable=True)
    zone_min_y = Column(Float, default=0.0, nullable=True)
    zone_max_x = Column(Float, default=1.0, nullable=True)
    zone_max_y = Column(Float, default=1.0, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    events = relationship("Event", back_populates="camera", cascade="all, delete-orphan")

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    camera_id = Column(Integer, ForeignKey("cameras.id", ondelete="CASCADE"), nullable=False)
    score = Column(Float, nullable=False)
    image_path = Column(String, nullable=True)
    description = Column(String, nullable=True)

    camera = relationship("Camera", back_populates="events")
    alerts = relationship("Alert", back_populates="event", cascade="all, delete-orphan")

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    message = Column(String, nullable=False)

    event = relationship("Event", back_populates="alerts")
