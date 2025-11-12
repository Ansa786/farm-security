import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env at project root
load_dotenv()

ONESIGNAL_APP_ID = os.getenv("ONESIGNAL_APP_ID", "b6f2e79a-afa6-4b06-81db-86a6ed2053ba")  # Default from index.html
ONESIGNAL_API_KEY = os.getenv("ONESIGNAL_API_KEY", "")  # Must be set in your .env file

def send_push_notification(player_id: str, title: str, message: str):
    """
    Sends a push notification to the given player_id using OneSignal.
    """
    if not ONESIGNAL_API_KEY:
        print("WARNING: ONESIGNAL_API_KEY not set. Notification not sent.")
        return False
    
    url = "https://onesignal.com/api/v1/notifications"
    headers = {
        "Authorization": f"Basic {ONESIGNAL_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "app_id": ONESIGNAL_APP_ID,
        "include_player_ids": [player_id],
        "headings": {"en": title},
        "contents": {"en": message}
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=5)
        print(f"OneSignal Status: {response.status_code}")
        if response.status_code == 200:
            return True
        else:
            print(f"OneSignal Error: {response.text}")
            return False
    except Exception as e:
        print(f"OneSignal Exception: {e}")
        return False

def send_onesignal_notification(title: str, message: str) -> bool:
    """
    Sends a push notification to all subscribed users (broadcast).
    This is the function called by detection service.
    """
    if not ONESIGNAL_API_KEY:
        print("WARNING: ONESIGNAL_API_KEY not set. Notification not sent.")
        return False
    
    url = "https://onesignal.com/api/v1/notifications"
    headers = {
        "Authorization": f"Basic {ONESIGNAL_API_KEY}",
        "Content-Type": "application/json"
    }
    # Send to all subscribed users (no player_ids = broadcast)
    payload = {
        "app_id": ONESIGNAL_APP_ID,
        "included_segments": ["All"],  # Send to all subscribed users
        "headings": {"en": title},
        "contents": {"en": message}
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=5)
        print(f"OneSignal Broadcast Status: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ Notification sent: {title} - {message}")
            return True
        else:
            print(f"OneSignal Error: {response.text}")
            return False
    except Exception as e:
        print(f"OneSignal Exception: {e}")
        return False
