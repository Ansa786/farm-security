from fastapi import FastAPI
from app.routes import camera, siren
from app.routes import event

app.include_router(event.router)

app = FastAPI()
app.include_router(event.router)

app = FastAPI(
    title="Farm Security Backend",
    description="AI-powered farm security backend API",
    version="0.1.0"
)

app.include_router(camera.router, prefix="/camera", tags=["Camera"])
app.include_router(siren.router, prefix="/siren", tags=["Siren"])
@app.get("/")
def read_root():
    return {"message": "Farm Security Backend is running!"}

# app/main.py or a one-time script

from app.database import engine, Base
from app.models.event import DetectionEventDB  # import all your models!

Base.metadata.create_all(bind=engine)
