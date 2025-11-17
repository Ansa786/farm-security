import cv2
import numpy as np
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import time
import threading
import os
import requests
from app.services.detection import detector, get_system_state, log_detection_event
from app.services.siren_control import siren_controller
from app.services.video_handler import video_handler
from app.services.push_notification import send_onesignal_notification

router = APIRouter(prefix="/camera", tags=["camera"])

# NOTE: Update this URL to match the actual IP of your ESP32-CAM
# Prefer env override. Typical ESP32 stream path is http://<ip>:81/stream
# If stream doesn't work, try http://<ip>/stream or check ESP32 serial output for actual port
ESP32_CAM_STREAM_URL = os.getenv("ESP32_CAM_STREAM_URL", "http://192.168.43.77:81/stream")
ESP32_CAM_SNAPSHOT_URL = os.getenv("ESP32_CAM_SNAPSHOT_URL", "http://192.168.43.77/capture")
FRAME_SKIP = 3  # Run detection every 3 frames (to save CPU/GPU resources)

# Global video capture (will be initialized in processing loop)
cap = None
cap_lock = threading.Lock()
latest_frame = None
frame_lock = threading.Lock()

# Detection cooldown to prevent spam notifications
last_detection_time = 0
DETECTION_COOLDOWN = 30  # seconds between detections of the same type
last_detection_type = None
cooldown_lock = threading.Lock()

def get_camera_capture():
    """Get or create video capture object."""
    global cap
    with cap_lock:
        if cap is None or not cap.isOpened():
            # Try opening with FFMPEG backend and tune timeouts/buffer to avoid long blocking reads
            try:
                cap = cv2.VideoCapture(ESP32_CAM_STREAM_URL, cv2.CAP_FFMPEG)
            except Exception:
                cap = cv2.VideoCapture(ESP32_CAM_STREAM_URL)

            # Try to reduce buffering and set open/read timeouts if supported by OpenCV build
            try:
                cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            except Exception:
                pass
            # Some OpenCV versions expose timeouts (milliseconds). Ignore if unsupported.
            try:
                cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 5000)
            except Exception:
                pass
            try:
                cap.set(cv2.CAP_PROP_READ_TIMEOUT_MSEC, 5000)
            except Exception:
                pass

            if not cap.isOpened():
                print(f"⚠️  WARNING: Failed to connect to camera stream at {ESP32_CAM_STREAM_URL}")
                return None
            else:
                print(f"🔌 Connected to camera stream at {ESP32_CAM_STREAM_URL} (buffer=1, timeouts=5s if supported)")
        return cap

def try_read_snapshot() -> np.ndarray | None:
    """
    Fallback: fetch a single JPEG snapshot from ESP32 and decode it.
    This works when MJPEG streaming is not enabled but /capture exists.
    """
    try:
        resp = requests.get(ESP32_CAM_SNAPSHOT_URL, timeout=3)
        if resp.status_code == 200 and resp.content:
            nparr = np.frombuffer(resp.content, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            return img
        else:
            return None
    except Exception:
        return None

def video_processing_loop():
    """The main background loop for running detection and triggering actions."""
    global latest_frame, cap, last_detection_time, last_detection_type
    
    frame_count = 0
    print(f"🎥 Video processing loop starting... (Stream URL: {ESP32_CAM_STREAM_URL} | Snapshot URL: {ESP32_CAM_SNAPSHOT_URL})")
    
    while True:
        # Check system state
        if not get_system_state():
            time.sleep(1)
            continue
        
        # Get camera capture
        camera = get_camera_capture()
        frame = None
        ret = False
        if camera is not None:
            ret, frame = camera.read()
        # Fallback to snapshot endpoint if streaming failed
        if not ret or frame is None:
            snapshot = try_read_snapshot()
            if snapshot is not None:
                frame = snapshot
                ret = True
        
        if not ret:
            print("⚠️  Stream not available, attempting reconnect in 2s...")
            with cap_lock:
                if cap:
                    cap.release()
                cap = None
            time.sleep(2)
            continue

        # Store latest frame for live feed
        with frame_lock:
            latest_frame = frame.copy()

        # 1. Add frame to handler buffer (for pre-event footage)
        video_handler.add_frame(frame)
        
        # 2. Run detection every N frames
        frame_count += 1
        if frame_count % FRAME_SKIP == 0:
            # --- CORE DETECTION CALL ---
            # Run YOLO detection on the frame
            try:
                detections = detector.run_detection(frame)
            except Exception as e:
                print(f"⚠️  Detection error: {e}")
                detections = []
            
            if detections and len(detections) > 0:
                detection_type = detections[0]['label']
                confidence = detections[0].get('confidence', 0.0)
                current_time = time.time()
                
                # Check cooldown - prevent spam notifications for same detection type
                with cooldown_lock:
                    should_alert = (last_detection_type != detection_type or 
                                  current_time - last_detection_time >= DETECTION_COOLDOWN)
                
                if not should_alert:
                    # Still in cooldown, skip notification but log detection
                    print(f"👁️  Detection: {detection_type} (confidence: {confidence:.2f}) - Cooldown active")
                else:
                    # New detection or cooldown expired - trigger alert
                    print(f"🚨 ALERT! Threat Detected: {detection_type} (confidence: {confidence:.2f}) at {time.strftime('%Y-%m-%d %H:%M:%S')}")
                    
                    # Update cooldown tracking
                    with cooldown_lock:
                        last_detection_time = current_time
                        last_detection_type = detection_type
                    
                    # A. Start recording (will only start if not already recording)
                    video_handler.start_recording(detection_type)
                    
                    # B. Trigger Siren (AI-triggered)
                    siren_success = siren_controller.toggle_siren("ON")
                    
                    # C. Send Notification
                    notification_success = send_onesignal_notification(
                        title="🚨 Intrusion Alert!",
                        message="ALERT INTRUSION HAS BEEN DETECTED, requesting for immediate user action"
                    )
                    
                    # D. Log event to database
                    video_filename = None  # Will be set by video_handler if recording succeeds
                    log_detection_event(
                        detection_type=detection_type,
                        siren_activated=siren_success,
                        notified=notification_success,
                        video_filename=video_filename,
                        confidence=confidence
                    )
                    
                    # Auto-turn off siren after 60 seconds
                    def auto_siren_off():
                        time.sleep(60)
                        siren_controller.toggle_siren("OFF")
                    
                    threading.Thread(target=auto_siren_off, daemon=True).start()
            
            frame_count = 0
        
        time.sleep(0.033)  # ~30 FPS processing rate
    
    print("Video processing loop stopped.")

def generate_frames():
    """Generator function for streaming video frames."""
    while True:
        with frame_lock:
            if latest_frame is None:
                time.sleep(0.1)
                continue
            frame = latest_frame.copy()
        
        # Encode frame as JPEG
        ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        if not ret:
            continue
        
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        
        time.sleep(0.033)  # ~30 FPS

@router.get("/status")
async def get_stream_status():
    """Checks if the video stream is currently open."""
    camera = get_camera_capture()
    is_open = camera is not None and camera.isOpened()
    return {
        "status": "streaming" if is_open else "disconnected",
        "url": ESP32_CAM_STREAM_URL,
        "system_active": get_system_state()
    }

@router.get("/live_feed")
async def live_feed():
    """Live feed endpoint for streaming camera video."""
    headers = {
        # Prevent buffering/caching so MJPEG renders continuously
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no",
        "Access-Control-Allow-Origin": "*",
    }
    return StreamingResponse(
        generate_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame",
        headers=headers
    )