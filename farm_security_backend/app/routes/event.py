from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional

from app.database import SessionLocal
from app.models.event import DetectionEvent, DetectionEventDB

router = APIRouter()

# Dependency - get a database session per request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Compatibility endpoint for frontend
@router.get("/alerts")
async def get_alerts_compat(db: Session = Depends(get_db), limit: int = 100):
    """Compatibility endpoint: /alerts (frontend expects this)"""
    events = db.query(DetectionEventDB).order_by(DetectionEventDB.timestamp.desc()).limit(limit).all()
    # Convert to frontend format
    alerts = []
    for e in events:
        alerts.append({
            "id": e.id,
            "timestamp": e.timestamp.isoformat() if e.timestamp else None,
            "type": e.detection_type,
            "device": e.device_id,
            "siren": e.siren_activated,
            "notified": e.notified,
            "video": e.video_filename
        })
    return alerts

# Helper to convert DB model to Pydantic model
def db_to_pydantic(db_event: DetectionEventDB) -> DetectionEvent:
    """Convert SQLAlchemy model to Pydantic model."""
    return DetectionEvent(
        id=db_event.id,
        timestamp=db_event.timestamp,
        device_id=db_event.device_id,
        detection_type=db_event.detection_type,
        video_filename=db_event.video_filename,
        siren_activated=db_event.siren_activated,
        notified=db_event.notified,
        notification_type=db_event.notification_type
    )

# CREATE event
@router.post("/events/", response_model=DetectionEvent)
def create_detection_event(event: DetectionEvent, db: Session = Depends(get_db)):
    db_event = DetectionEventDB(
        timestamp=event.timestamp if event.timestamp else datetime.now(),
        device_id=event.device_id,
        detection_type=event.detection_type,
        video_filename=event.video_filename,
        siren_activated=event.siren_activated,
        notified=event.notified,
        notification_type=event.notification_type
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_to_pydantic(db_event)

# READ: List all events, or limit
@router.get("/events/", response_model=list[DetectionEvent])
def list_detection_events(db: Session = Depends(get_db), limit: int = 100):
    events = db.query(DetectionEventDB).order_by(DetectionEventDB.timestamp.desc()).limit(limit).all()
    return [db_to_pydantic(e) for e in events]

# READ: Get single event by ID
@router.get("/events/{event_id}", response_model=DetectionEvent)
def get_detection_event(event_id: int, db: Session = Depends(get_db)):
    event = db.query(DetectionEventDB).filter(DetectionEventDB.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Detection event not found")
    return db_to_pydantic(event)

# UPDATE: Patch event (example: mark as reviewed)
@router.patch("/events/{event_id}", response_model=DetectionEvent)
def update_detection_event(event_id: int, event_patch: DetectionEvent, db: Session = Depends(get_db)):
    event = db.query(DetectionEventDB).filter(DetectionEventDB.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    # Only update provided fields
    patch_dict = event_patch.model_dump(exclude_unset=True)
    for field, value in patch_dict.items():
        if field != 'id':  # Don't update ID
            setattr(event, field, value)
    db.commit()
    db.refresh(event)
    return db_to_pydantic(event)

# DELETE: Remove detection event
@router.delete("/events/{event_id}", response_model=dict)
def delete_detection_event(event_id: int, db: Session = Depends(get_db)):
    event = db.query(DetectionEventDB).filter(DetectionEventDB.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    db.delete(event)
    db.commit()
    return {"status": "deleted", "id": event_id}
