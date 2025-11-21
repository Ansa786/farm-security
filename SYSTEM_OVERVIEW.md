# Farm Security System - Overview

## System Architecture

### Hardware
- **ESP32-CAM AI Thinker** - Camera module for live video feed
- **Siren** - Connected to ESP32 for intrusion alerts

### AI Detection
- **YOLO Model** (`best.pt`) - Trained to detect:
  - Elephants
  - Cows
  - People/Humans

### Backend (FastAPI + Python)
- Real-time video processing from ESP32-CAM
- YOLO-based object detection
- Automatic siren control
- Push notifications via OneSignal
- SQLite database for event logging
- REST API for frontend communication

### Frontend (React + Vite)
- Live camera feed viewing
- Detection alerts/logs with timestamps
- Manual system ON/OFF control
- Manual siren control
- Real-time status monitoring

## How It Works

1. **ESP32-CAM** continuously streams video to the backend
2. **Backend** processes frames every 3rd frame for efficiency
3. **YOLO Model** detects intrusions (elephant/cow/people)
4. **On Detection:**
   - ✅ Siren automatically turns ON
   - ✅ Push notification sent to user
   - ✅ Event logged to database with:
     - Timestamp
     - Detection type
     - Confidence score
     - Device ID
     - Siren status
     - Notification status
   - ✅ Siren auto-turns OFF after 60 seconds
5. **User** can view all detection logs in the web app

## Detection Cooldown
- 30-second cooldown between same detection types
- Prevents notification spam
- Still logs all detections

## Database Schema
```
detection_events table:
- id (primary key)
- timestamp (datetime)
- detection_type (string)
- device_id (string)
- siren_activated (boolean)
- notified (boolean)
- confidence (float)
- data (JSON)
```

## API Endpoints

### Camera
- `GET /camera/status` - Camera connection status
- `GET /camera/live_feed` - MJPEG live stream

### System
- `POST /system` - Toggle system ON/OFF
- `GET /api/system/status` - Get system status
- `POST /api/system/siren/toggle` - Manual siren control

### Events/Alerts
- `GET /alerts` - Get all detection logs
- `GET /api/events/` - List all events
- `POST /api/events/` - Create event
- `GET /api/events/{id}` - Get specific event
- `PATCH /api/events/{id}` - Update event
- `DELETE /api/events/{id}` - Delete event

## Configuration

### Backend Environment Variables
```
ESP32_CAM_STREAM_URLS - Camera stream URL(s)
ESP32_CAM_SNAPSHOT_URL - Camera snapshot URL
DETECTION_CONFIDENCE_THRESHOLD - Min confidence (default: 0.7)
DETECTION_ALLOWED_CLASSES - Allowed detection classes
SYSTEM_OFF_DURATION_MINUTES - Auto-reactivation time (default: 30)
ONESIGNAL_APP_ID - OneSignal app ID
ONESIGNAL_REST_API_KEY - OneSignal API key
```

### Frontend Settings
- API Base URL (configurable in app)
- Stream URL (configurable in app)
- Mock mode for testing

## Features

✅ Real-time intrusion detection
✅ Automatic siren activation
✅ Push notifications
✅ Event logging with timestamps
✅ Live camera feed
✅ Manual system control
✅ Manual siren control
✅ Detection confidence scores
✅ Cooldown to prevent spam
✅ Auto-reactivation after system OFF
✅ Multi-device support

## No Video Recording
The system logs timestamps and metadata only - no video files are saved to conserve storage space.
