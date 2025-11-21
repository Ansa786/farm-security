# app/routes/system.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.detection import set_system_state, get_system_state, SYSTEM_ACTIVE
from app.services.siren_control import siren_controller, get_siren_state

router = APIRouter(prefix="/api/system", tags=["System"])

class SystemStateRequest(BaseModel):
    state: str  # "ON" or "OFF"

class SirenStateRequest(BaseModel):
    action: str  # "ON" or "OFF"

@router.get("/status")
async def get_status():
    """Returns the current security system status."""
    # Import here to avoid circular imports
    from app.routes.camera import get_camera_connection_status
    
    system_active = get_system_state()
    camera_connected = get_camera_connection_status()
    
    # Build status message
    if system_active and camera_connected:
        status_msg = "System is active and camera is connected."
        status_display = "ON - Connected"
    elif system_active:
        status_msg = "System is active but camera is disconnected."
        status_display = "ON - Disconnected"
    else:
        status_msg = "System is paused."
        status_display = "OFF"
    
    return {
        "status": "ON" if system_active else "OFF",
        "status_display": status_display,
        "message": status_msg,
        "camera_connected": camera_connected,
        "siren_state": "ON" if get_siren_state() else "OFF"
    }

@router.post("/toggle")
async def toggle_system(request: SystemStateRequest):
    """5. Endpoint to manually turn the security system ON/OFF."""
    if request.state not in ['ON', 'OFF']:
        raise HTTPException(status_code=400, detail="State must be ON or OFF.")
    
    new_state_bool = request.state == 'ON'
    final_state = set_system_state(new_state_bool)
    return {
        "success": True,
        "new_state": "ON" if final_state else "OFF",
        "message": f"System turned {'ON' if final_state else 'OFF'}"
    }

class SystemEnabledRequest(BaseModel):
    enabled: bool

@router.post("/system")
async def toggle_system_compat(request: SystemEnabledRequest):
    """Compatibility endpoint: /system (frontend expects this with { enabled: bool })"""
    final_state = set_system_state(request.enabled)
    return {
        "success": True,
        "enabled": final_state
    }

@router.post("/siren/toggle")
async def toggle_siren_manual(request: SirenStateRequest):
    """3. Manual ON/OFF control for the siren."""
    if request.action not in ['ON', 'OFF']:
        raise HTTPException(status_code=400, detail="Action must be ON or OFF.")
    
    success = siren_controller.toggle_siren(request.action)
    return {
        "success": success,
        "siren_state": request.action.upper(),
        "message": f"Siren turned {request.action.upper()}"
    }

@router.get("/siren/status")
async def get_siren_status():
    """Get current siren status."""
    return {
        "siren_state": "ON" if get_siren_state() else "OFF"
    }
