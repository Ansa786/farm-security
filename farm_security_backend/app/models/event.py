# app/models/event.py

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel
from app import db

# SQLAlchemy model used by the app (must provide fields used elsewhere)
class DetectionEventDB(db.Model):
    __tablename__ = "detection_events"

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    detection_type = db.Column(db.String(128), nullable=False)
    device_id = db.Column(db.String(128), nullable=True)
    siren_activated = db.Column(db.Boolean, default=False, nullable=False)
    notified = db.Column(db.Boolean, default=False, nullable=False)
    video_filename = db.Column(db.String(256), nullable=True)
    confidence = db.Column(db.Float, nullable=True)
    data = db.Column(db.JSON, nullable=True)

    def __repr__(self):
        return (
            f"<DetectionEventDB id={self.id} type={self.detection_type} "
            f"device={self.device_id} siren={self.siren_activated} ts={self.timestamp}>"
        )

# Pydantic schema exposed as DetectionEvent for FastAPI / other imports
class DetectionEvent(BaseModel):
    id: Optional[int] = None
    timestamp: Optional[datetime] = None
    detection_type: str
    device_id: Optional[str] = None
    siren_activated: bool = False
    notified: bool = False
    video_filename: Optional[str] = None
    confidence: Optional[float] = None
    data: Optional[Dict[str, Any]] = None

    class Config:
        orm_mode = True           # keep for Pydantic v1 compatibility
        from_attributes = True    # Pydantic v2 key to avoid warning
