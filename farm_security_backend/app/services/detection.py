# app/services/detection.py
import os
import time
from threading import Timer, Lock
from ultralytics import YOLO
import cv2
import numpy as np
from datetime import datetime
from app.services.siren_control import trigger_siren
from app.services.push_notification import send_onesignal_notification
from app.database import SessionLocal
from app.models.event import DetectionEventDB

# --- Global System State ---
SYSTEM_ACTIVE = True
SYSTEM_LOCK = Lock()
MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'models', 'best.pt')
TIME_OFF = int(os.getenv('SYSTEM_OFF_DURATION_MINUTES', 30)) * 60

# Load YOLOv8 Model (It's safe to load globally)
model = None
try:
    if os.path.exists(MODEL_PATH):
        model = YOLO(MODEL_PATH)
        print(f"✅ YOLOv8 Model Loaded from {MODEL_PATH}")
    else:
        print(f"⚠️  WARNING: Model file not found at {MODEL_PATH}. Detection will be disabled.")
except Exception as e:
    print(f"❌ CRITICAL: Failed to load YOLOv8 model: {e}")

def auto_reactivate_system():
    """5. Auto-reactivation after 30 min."""
    global SYSTEM_ACTIVE
    with SYSTEM_LOCK:
        SYSTEM_ACTIVE = True
    print("\n\n*** SYSTEM AUTO-REACTIVATED ***\n\n")

def set_system_state(is_active: bool):
    """5. Endpoint to turn security system ON/OFF."""
    global SYSTEM_ACTIVE
    with SYSTEM_LOCK:
        SYSTEM_ACTIVE = is_active
    
    if not is_active:
        print(f"*** SYSTEM DEACTIVATED for {TIME_OFF // 60} minutes ***")
        # Start the auto-reactivation timer
        Timer(TIME_OFF, auto_reactivate_system).start()
    else:
        print("*** SYSTEM ACTIVATED ***")
    
    return SYSTEM_ACTIVE

def get_system_state():
    """Get current system state."""
    with SYSTEM_LOCK:
        return SYSTEM_ACTIVE

def run_detection(frame: np.ndarray) -> list:
    """
    Run YOLOv8 detection on a frame.
    Returns list of detections with 'label' and 'confidence' keys.
    """
    if model is None:
        return []
    
    try:
        results = model(frame, verbose=False)
        detections = []
        
        if results and len(results) > 0 and results[0].boxes is not None and len(results[0].boxes) > 0:
            for box in results[0].boxes:
                class_id = int(box.cls.item())
                confidence = float(box.conf.item())
                label = model.names[class_id]
                
                # Only return detections with confidence > 0.7 (increased threshold to reduce false positives)
                # Filter out common false positives - adjust class names based on your model
                if confidence > 0.7:
                    # Filter: only allow specific threat classes (human, elephant, etc.)
                    # Exclude background/irrelevant classes if your model has them
                    allowed_classes = ['human', 'person', 'elephant', 'monkey', 'animal']  # Add your actual class names
                    label_lower = label.lower()
                    if any(allowed in label_lower for allowed in allowed_classes):
                        detections.append({
                            'label': label,
                            'confidence': confidence,
                            'class_id': class_id
                        })
                    else:
                        print(f"⚠️  Filtered out detection: {label} (confidence: {confidence:.2f}) - not in allowed classes")
        
        return detections
    except Exception as e:
        print(f"Detection error: {e}")
        return []

def log_detection_event(detection_type: str, siren_activated: bool, notified: bool, video_filename: str = None, confidence: float = None):
    """Log a detection event to the database."""
    try:
        db = SessionLocal()
        try:
            event = DetectionEventDB(
                timestamp=datetime.now(),
                device_id="ESP32-CAM-01",
                detection_type=detection_type,
                video_filename=video_filename,
                siren_activated=siren_activated,
                notified=notified,
                confidence=confidence
            )
            db.add(event)
            db.commit()
            db.refresh(event)
            print(f"✅ Event logged: {detection_type} at {event.timestamp}")
            return event.id
        finally:
            db.close()
    except Exception as e:
        print(f"❌ Error logging event: {e}")
        return None

# For backward compatibility, provide a detector object with run_detection as an instance method
class Detector:
    def run_detection(self, frame: np.ndarray) -> list:
        """Wrapper method that calls the module-level run_detection function."""
        return run_detection(frame)

detector = Detector()