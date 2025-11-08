# app/models/event.py

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Pydantic schema for FastAPI (request/response bodies, validation)
class DetectionEvent(BaseModel):
    id: Optional[int] = None  # DB primary key, optional for creation
    timestamp: datetime
    device_id: str
    detection_type: str  # e.g., "elephant", "human", "monkey"
    video_filename: Optional[str]
    siren_activated: bool
    notified: bool
    notification_type: Optional[str]  # e.g., "push", "sms", "email"

# SQLAlchemy ORM model for database table
from sqlalchemy import Column, String, Integer, Boolean, DateTime
from app.database import Base  # Use common project-wide Base!

class DetectionEventDB(Base):
    __tablename__ = 'detection_events'
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, nullable=False)
    device_id = Column(String, nullable=False)
    detection_type = Column(String, nullable=False)
    video_filename = Column(String)
    siren_activated = Column(Boolean, default=False)
    notified = Column(Boolean, default=False)
    notification_type = Column(String)
