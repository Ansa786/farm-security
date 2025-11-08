# app/models/video.py
from pydantic import BaseModel

class VideoMeta(BaseModel):
    filename: str
    event_id: int
    recorded_at: datetime
    duration_sec: int
