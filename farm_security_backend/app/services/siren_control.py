# app/services/siren_control.py
import os
import requests
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# ESP32-CAM IP address (same as camera stream)
ESP32_CAM_IP = os.getenv("ESP32_CAM_IP", "10.18.81.133")  # Update to match your ESP32 IP
SIREN_STATE = False
SIREN_LOCK = False  # Prevent multiple simultaneous triggers

def trigger_siren(state: str) -> bool:
    """
    Triggers the siren ON or OFF by sending HTTP request to ESP32.
    ESP32 controls GPIO pin 2 (can be changed in Arduino code).
    """
    global SIREN_STATE, SIREN_LOCK
    
    if SIREN_LOCK:
        return False
    
    SIREN_LOCK = True
    
    try:
        # Send HTTP GET request to ESP32 siren endpoint
        url = f"http://{ESP32_CAM_IP}/siren?state={state.upper()}"
        
        try:
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                SIREN_STATE = (state.upper() == "ON")
                if state.upper() == "ON":
                    print(f"🔊 SIREN ACTIVATED via ESP32 (GPIO 2)")
                else:
                    print(f"🔇 SIREN DEACTIVATED via ESP32")
                return True
            else:
                print(f"⚠️  Siren control failed: HTTP {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"⚠️  Failed to control siren on ESP32: {e}")
            # Fallback: still update state for logging
            SIREN_STATE = (state.upper() == "ON")
            return False
    finally:
        SIREN_LOCK = False

def get_siren_state() -> bool:
    """Returns current siren state."""
    return SIREN_STATE

class SirenController:
    """Wrapper class for siren control."""
    
    def toggle_siren(self, state: str) -> bool:
        """Toggle siren ON or OFF."""
        return trigger_siren(state)
    
    def get_state(self) -> bool:
        """Get current siren state."""
        return get_siren_state()

# Global instance
siren_controller = SirenController()
