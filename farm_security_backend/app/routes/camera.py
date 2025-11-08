import cv2
import numpy as np
from fastapi import APIRouter
import time
from app.services.detection import detector # <-- Detection Service is imported here
from app.services.siren_control import siren_controller
from app.services.video_handler import video_handler

router = APIRouter(prefix="/camera", tags=["camera"])

# NOTE: Update this URL to match the actual IP of your ESP32-CAM
ESP32_CAM_STREAM_URL = "http://192.168.1.100:81/stream" 
FRAME_SKIP = 5 # Run detection every 5 frames (to save CPU/GPU resources)

cap = cv2.VideoCapture(ESP32_CAM_STREAM_URL)
if not cap.isOpened():
    print(f"WARNING: Initial connection to stream failed at {ESP32_CAM_STREAM_URL}.")

def video_processing_loop():
    """The main background loop for running detection and triggering actions."""
    
    # Re-initialize capture if it was closed
    if not cap.isOpened():
        cap.open(ESP32_CAM_STREAM_URL)
        if not cap.isOpened():
            print("ERROR: Failed to open stream in background task.")
            return

    frame_count = 0
    print("Video processing loop running...")
    while cap.isOpened():
        ret, frame = cap.read()
        
        if not ret:
            print("Stream ended, attempting reconnect...")
            cap.open(ESP32_CAM_STREAM_URL)
            time.sleep(1) 
            continue

        # 1. Add frame to handler buffer (for pre-event footage)
        video_handler.add_frame(frame)
        
        # 2. Run detection every N frames
        frame_count += 1
        if frame_count % FRAME_SKIP == 0:
            # --- CORE DETECTION CALL ---
            detections = detector.run_detection(frame) 
            # ---------------------------
            
            if detections:
                print(f"!!! ALERT !!! Threat Detected: {detections[0]['label']} at {time.time()}")
                
                # A. Start recording (will only start if not already recording)
                detection_type = detections[0]['label']
                video_handler.start_recording(detection_type)
                    
                # B. Trigger Siren (AI-triggered)
                siren_controller.toggle_siren("ON")
                
                # C. Send Notification (Placeholder for push_notification.py service call)
                # You would uncomment and implement this: push_notification_service.send_alert(detection_type)
                
            frame_count = 0
            
        time.sleep(0.01) # Small delay
    print("Video processing loop stopped.")


@router.get("/status")
async def get_stream_status():
    """Checks if the video stream is currently open."""
    return {"status": "streaming" if cap.isOpened() else "disconnected", "url": ESP32_CAM_STREAM_URL}