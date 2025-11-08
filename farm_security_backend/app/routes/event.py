from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

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
    return DetectionEvent.from_orm(db_event)

# READ: List all events, or limit
@router.get("/events/", response_model=list[DetectionEvent])
def list_detection_events(db: Session = Depends(get_db), limit: int = 20):
    events = db.query(DetectionEventDB).order_by(DetectionEventDB.timestamp.desc()).limit(limit).all()
    return [DetectionEvent.from_orm(e) for e in events]

# READ: Get single event by ID
@router.get("/events/{event_id}", response_model=DetectionEvent)
def get_detection_event(event_id: int, db: Session = Depends(get_db)):
    event = db.query(DetectionEventDB).filter(DetectionEventDB.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Detection event not found")
    return DetectionEvent.from_orm(event)

# UPDATE: Patch event (example: mark as reviewed)
@router.patch("/events/{event_id}", response_model=DetectionEvent)
def update_detection_event(event_id: int, event_patch: DetectionEvent, db: Session = Depends(get_db)):
    event = db.query(DetectionEventDB).filter(DetectionEventDB.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    # Only update provided fields
    for field, value in event_patch.dict(exclude_unset=True).items():
        setattr(event, field, value)
    db.commit()
    db.refresh(event)
    return DetectionEvent.from_orm(event)

# DELETE: Remove detection event
@router.delete("/events/{event_id}", response_model=dict)
def delete_detection_event(event_id: int, db: Session = Depends(get_db)):
    event = db.query(DetectionEventDB).filter(DetectionEventDB.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    db.delete(event)
    db.commit()
    return {"status": "deleted"}
