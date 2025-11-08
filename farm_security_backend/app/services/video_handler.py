import cv2
import numpy as np
import os
import datetime
import threading
import time

# Configuration
UPLOADS_DIR = "farm_security_backend/uploads"
CLIP_DURATION_SECONDS = 120 # 2 minutes
FPS = 15 # Target FPS for recording

os.makedirs(UPLOADS_DIR, exist_ok=True)

class VideoHandler:
    """Manages capturing and saving video clips."""
    
    def __init__(self):
        self._is_recording = False
        self._frame_buffer = [] # Buffer for storing pre-event and current frames
        self._lock = threading.Lock()
        
    def start_recording(self, detection_type: str):
        """Starts a new recording thread."""
        with self._lock:
            if self._is_recording:
                return False
            
            self._is_recording = True
            
            # Start the non-blocking recording thread
            threading.Thread(
                target=self._record_clip, 
                args=(detection_type,),
                daemon=True # Daemon thread so it closes when main app closes
            ).start()
            print(f"Started 2-minute recording for {detection_type} event.")
            return True

    def add_frame(self, frame: np.ndarray):
        """Adds a frame to the buffer/queue."""
        # Always maintain a small buffer (e.g., 5 seconds of pre-event footage)
        PRE_EVENT_BUFFER_SIZE = FPS * 5 
        
        with self._lock:
            self._frame_buffer.append(frame.copy())
            
            # Trim buffer if not recording
            if not self._is_recording and len(self._frame_buffer) > PRE_EVENT_BUFFER_SIZE:
                self._frame_buffer.pop(0)

    def _record_clip(self, detection_type: str):
        """Worker function for the recording thread."""
        
        if not self._frame_buffer:
            self._is_recording = False
            return
            
        # 1. Setup Writer
        height, width, _ = self._frame_buffer[0].shape
        filename = f"{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{detection_type}.avi"
        filepath = os.path.join(UPLOADS_DIR, filename)
        
        # XVID codec for AVI format
        fourcc = cv2.VideoWriter_fourcc(*'XVID') 
        writer = cv2.VideoWriter(filepath, fourcc, FPS, (width, height))
        
        start_time = time.time()
        
        # 2. Write Buffered Frames (Pre-event footage)
        with self._lock:
            frames_to_write = self._frame_buffer[:] # Copy all buffered frames
            self._frame_buffer.clear() # Clear for new live frames
            
        for frame in frames_to_write:
            writer.write(frame)

        # 3. Write Live Frames
        while (time.time() - start_time) < CLIP_DURATION_SECONDS:
            with self._lock:
                if self._frame_buffer:
                    frame = self._frame_buffer.pop(0) # Use frames added by add_frame
                else:
                    frame = None
            
            if frame is not None:
                writer.write(frame)
            else:
                time.sleep(1/FPS) # Wait for a new frame
                
        # 4. Finalize
        writer.release()
        with self._lock:
            self._is_recording = False
        print(f"Finished recording: {filepath}")

# Global instance
video_handler = VideoHandler()