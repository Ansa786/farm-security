import cv2
import numpy as np
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import time
import threading
import os
import requests
from dotenv import load_dotenv

# Load .env file to ensure environment variables are available
load_dotenv()

from app.services.detection import detector, get_system_state, log_detection_event
from app.services.siren_control import siren_controller
from app.services.push_notification import send_onesignal_notification

router = APIRouter(prefix="/camera", tags=["camera"])

# NOTE: Update this URL to match the actual IP of your ESP32-CAM
# Prefer env override. Typical ESP32 stream path is http://<ip>:81/stream
# If stream doesn't work, try http://<ip>/stream or check ESP32 serial output for actual port
ESP32_CAM_STREAM_URLS = [u.strip() for u in os.getenv("ESP32_CAM_STREAM_URLS", "http://10.18.81.133:81/stream").split(",") if u.strip()]
ESP32_CAM_SNAPSHOT_URL = os.getenv("ESP32_CAM_SNAPSHOT_URL", "http://10.18.81.133/capture")

print(f"🎥 Camera URLs loaded: {ESP32_CAM_STREAM_URLS}")
print(f"📸 Snapshot URL: {ESP32_CAM_SNAPSHOT_URL}")
FRAME_SKIP = 3  # Run detection every 3 frames (to save CPU/GPU resources)

# Global video capture (will be initialized in processing loop)
cap = None
cap_lock = threading.Lock()
latest_frame = None
frame_lock = threading.Lock()
camera_connected = False
camera_connection_lock = threading.Lock()

# Detection cooldown to prevent spam notifications
last_detection_time = 0
DETECTION_COOLDOWN = 10  # seconds between detections (any type)
last_detection_type = None
cooldown_lock = threading.Lock()

def get_camera_connection_status():
    """Get current camera connection status."""
    with camera_connection_lock:
        return camera_connected

def set_camera_connection_status(status: bool):
    """Set camera connection status."""
    global camera_connected
    with camera_connection_lock:
        camera_connected = status

def get_camera_capture():
    """Get or create video capture object. Tries multiple URLs and backends."""
    global cap
    with cap_lock:
        if cap is None or not cap.isOpened():
            # Try each URL in the list with different backends
            for url in ESP32_CAM_STREAM_URLS:
                # Try different OpenCV backends in order of preference
                backends = [
                    (cv2.CAP_ANY, "CAP_ANY"),
                    (cv2.CAP_FFMPEG, "CAP_FFMPEG"),
                    (cv2.CAP_DSHOW, "CAP_DSHOW"),
                ]
                
                for backend, backend_name in backends:
                    try:
                        print(f"🔌 Attempting connection to {url} with {backend_name}...")
                        cap = cv2.VideoCapture(url, backend)
                        
                        if not cap.isOpened():
                            print(f"   ❌ {backend_name} failed to open")
                            continue
                        
                        # Configure capture settings
                        try:
                            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                            cap.set(cv2.CAP_PROP_FPS, 30)
                        except Exception:
                            pass
                        
                        # Set timeouts if supported
                        try:
                            cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 10000)
                            cap.set(cv2.CAP_PROP_READ_TIMEOUT_MSEC, 3000)
                        except Exception:
                            pass

                        # Verify by reading a test frame
                        print(f"   📸 Testing frame read...")
                        ret, test_frame = cap.read()
                        if ret and test_frame is not None:
                            print(f"   ✅ SUCCESS! Connected with {backend_name}")
                            set_camera_connection_status(True)
                            return cap
                        else:
                            print(f"   ❌ {backend_name} opened but cannot read frames")
                            cap.release()
                            cap = None
                            
                    except Exception as e:
                        print(f"   ❌ {backend_name} exception: {e}")
                        if cap:
                            try:
                                cap.release()
                            except:
                                pass
                            cap = None
                        continue
            
            # All attempts failed
            print(f"⚠️  WARNING: Failed to connect to camera stream at any URL: {ESP32_CAM_STREAM_URLS}")
            print(f"💡 TIP: Stream works in browser but not OpenCV. Try:")
            print(f"   1. Check if ESP32 allows multiple connections")
            print(f"   2. Close browser tab accessing the stream")
            print(f"   3. Restart ESP32-CAM")
            set_camera_connection_status(False)
            return None
        else:
            # Verify the existing connection is still working
            try:
                # Check if we can still read frames
                if cap.isOpened():
                    # Don't actually read here, just check if opened
                    set_camera_connection_status(True)
                    return cap
            except Exception:
                # Connection lost, release and return None
                try:
                    cap.release()
                except:
                    pass
                cap = None
                set_camera_connection_status(False)
                return None
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
    consecutive_failures = 0
    max_consecutive_failures = 3  # Reconnect after 3 consecutive failed reads
    print(f"🎥 Video processing loop starting... (Stream URL: {ESP32_CAM_STREAM_URLS} | Snapshot URL: {ESP32_CAM_SNAPSHOT_URL})")
    
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
            consecutive_failures += 1
            print(f"⚠️  Stream read failed ({consecutive_failures}/{max_consecutive_failures})")
            set_camera_connection_status(False)
            
            # Force reconnection after 3 consecutive failures
            if consecutive_failures >= max_consecutive_failures:
                print("🔄 3 consecutive failures detected - forcing camera reconnection...")
                with cap_lock:
                    if cap:
                        try:
                            cap.release()
                        except:
                            pass
                    cap = None
                consecutive_failures = 0
                time.sleep(1)  # Brief pause before reconnecting
            else:
                time.sleep(0.5)  # Short delay between retries
            continue
        
        # Reset failure counter on successful read
        consecutive_failures = 0

        # Store latest frame for live feed
        with frame_lock:
            latest_frame = frame.copy()
        
        # Update connection status to True since we successfully read a frame
        set_camera_connection_status(True)

        # Run detection every N frames
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
                    
                    # A. Trigger Siren (AI-triggered)
                    siren_success = siren_controller.toggle_siren("ON")
                    
                    # B. Send Notification
                    notification_success = send_onesignal_notification(
                        title="🚨 Intrusion Alert!",
                        message=f"ALERT! {detection_type.upper()} DETECTED in your farm. Immediate action required!"
                    )
                    
                    # C. Log event to database (timestamp only, no video)
                    log_detection_event(
                        detection_type=detection_type,
                        siren_activated=siren_success,
                        notified=notification_success,
                        video_filename=None,
                        confidence=confidence
                    )
                    
                    # Auto-turn off siren after 60 seconds
                    def auto_siren_off():
                        time.sleep(60)
                        siren_controller.toggle_siren("OFF")
                    
                    threading.Thread(target=auto_siren_off, daemon=True).start()
            
            frame_count = 0
        
        time.sleep(0.016)  # ~60 FPS processing rate for smoother feed
    
    print("Video processing loop stopped.")

def generate_frames():
    """Generator function for streaming video frames."""
    while True:
        with frame_lock:
            if latest_frame is None:
                time.sleep(0.01)
                continue
            frame = latest_frame.copy()
        
        # Encode frame as JPEG with lower quality for faster streaming
        ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
        if not ret:
            continue
        
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        
        time.sleep(0.016)  # ~60 FPS for smoother streaming

@router.get("/status")
async def get_stream_status():
    """Checks if the video stream is currently open."""
    with cap_lock:
        cap_open = cap is not None and cap.isOpened()
    connection_status = get_camera_connection_status()
    final_status = "streaming" if (cap_open or connection_status) else "disconnected"
    return {
        "status": final_status,
        "url": ESP32_CAM_STREAM_URLS[0] if ESP32_CAM_STREAM_URLS else "",
        "system_active": get_system_state(),
        "connected": connection_status
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