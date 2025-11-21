# app/models/event.py

from datetime import datetime
from typing import Optional, Dict, Any

from pydantic import BaseModel, ConfigDict
from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    String,
    Boolean,
    Float,
    JSON,
)

from app.database import Base


class DetectionEventDB(Base):
    """
    SQLAlchemy model for detection events.
    Using the shared declarative Base ensures Base.metadata.create_all()
    in app/__main__.py creates the table on startup (required for SQLite).
    """

    __tablename__ = "detection_events"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    detection_type = Column(String(128), nullable=False)
    device_id = Column(String(128), nullable=True)
    siren_activated = Column(Boolean, default=False, nullable=False)
    notified = Column(Boolean, default=False, nullable=False)
    video_filename = Column(String(256), nullable=True)
    confidence = Column(Float, nullable=True)
    data = Column(JSON, nullable=True)

    def __repr__(self) -> str:  # pragma: no cover - simple debug helper
        return (
            f"<DetectionEventDB id={self.id} type={self.detection_type} "
            f"device={self.device_id} siren={self.siren_activated} ts={self.timestamp}>"
        )


class DetectionEvent(BaseModel):
    """
    Pydantic schema exposed via FastAPI (request/response bodies).
    """

    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    timestamp: Optional[datetime] = None
    detection_type: str
    device_id: Optional[str] = None
    siren_activated: bool = False
    notified: bool = False
    video_filename: Optional[str] = None
    confidence: Optional[float] = None
    data: Optional[Dict[str, Any]] = None
