# app/services/siren_control.py
import os
import requests
from typing import Optional

# Mock siren control - can be replaced with GPIO/relay control or MQTT
SIREN_STATE = False
SIREN_LOCK = False  # Prevent multiple simultaneous triggers

def trigger_siren(state: str) -> bool:
    """
    Triggers the siren ON or OFF.
    For demo: returns True (mock success).
    For production: implement GPIO/relay control or MQTT publish.
    """
    global SIREN_STATE, SIREN_LOCK
    
    if SIREN_LOCK:
        return False
    
    SIREN_LOCK = True
    
    try:
        if state.upper() == "ON":
            SIREN_STATE = True
            print("🔊 SIREN ACTIVATED")
            # TODO: Add GPIO/relay control here
            # GPIO.output(SIREN_PIN, GPIO.HIGH)
            # OR publish MQTT message to ESP32
            return True
        elif state.upper() == "OFF":
            SIREN_STATE = False
            print("🔇 SIREN DEACTIVATED")
            # TODO: Add GPIO/relay control here
            # GPIO.output(SIREN_PIN, GPIO.LOW)
            return True
        else:
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
