from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import threading
from app.database import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start camera processing thread (import camera lazily to avoid early annotation issues)
    from app.routes import camera as camera_route  # lazy import
    processing_thread = threading.Thread(target=camera_route.video_processing_loop, daemon=True)
    processing_thread.start()
    print("Camera processing thread started")
    yield
    # Shutdown: cleanup if needed
    print("Shutting down...")

app = FastAPI(
    title="Farm Security Backend",
    description="AI-powered farm security backend API",
    version="0.1.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers (import lazily to avoid import-time annotation evaluation errors)
from app.database import SessionLocal
from app.models.event import DetectionEventDB

from app.routes import event as event_route, camera as camera_route2, siren as siren_route, system as system_route

app.include_router(event_route.router, prefix="/api", tags=["Events"])
app.include_router(camera_route2.router, tags=["Camera"])
app.include_router(siren_route.router, tags=["Siren"])
app.include_router(system_route.router, tags=["System"])

# Compatibility routes for frontend (needs to be at root level)
from app.services.detection import set_system_state
from pydantic import BaseModel

class SystemEnabledRequest(BaseModel):
    enabled: bool

@app.post("/system")
async def toggle_system_compat(request: SystemEnabledRequest):
    """Compatibility endpoint: /system (frontend expects this with { enabled: bool })"""
    final_state = set_system_state(request.enabled)
    return {
        "success": True,
        "enabled": final_state
    }

@app.get("/alerts")
async def get_alerts_compat(limit: int = 100):
    """Compatibility endpoint: /alerts (frontend expects this)"""
    db = SessionLocal()
    try:
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
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Farm Security Backend is running!"}

# Allow `python -m app` to start the server directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.__main__:app", host="0.0.0.0", port=8000, reload=True)
