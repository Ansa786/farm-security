from fastapi import APIRouter
from app.services.siren_control import siren_controller

router = APIRouter(prefix="/siren", tags=["siren"])

@router.post("/set_state/{state}")
async def set_siren_state(state: str):
    """Manually controls the siren state via MQTT ('on' or 'off')."""
    if state.lower() not in ["on", "off"]:
        return {"status": "error", "message": "State must be 'on' or 'off'"}
    
    command = "ON" if state.lower() == "on" else "OFF"
    success = siren_controller.toggle_siren(command)
    
    if success:
        return {"status": "success", "siren_state": command, "message": f"Siren set to {command} via MQTT."}
    else:
        return {"status": "error", "siren_state": command, "message": "Failed to publish MQTT command. Check broker connection."}