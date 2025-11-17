import os
import requests
from dotenv import load_dotenv
from typing import Optional, Sequence, Dict, Any

# Load environment variables from .env at project root
load_dotenv()

ONESIGNAL_API_URL = "https://onesignal.com/api/v1/notifications"
ONESIGNAL_APP_ID = os.getenv("ONESIGNAL_APP_ID", "b6f2e79a-afa6-4b06-81db-86a6ed2053ba")  # Default from index.html
ONESIGNAL_API_KEY = os.getenv("ONESIGNAL_API_KEY", "")  # Must be set in your .env file
# Optional: comma-separated player ids or single id in env for testing
ONESIGNAL_PLAYER_IDS = os.getenv("ONESIGNAL_PLAYER_IDS")

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

def send_onesignal_notification(
    title: str,
    message: str,
    include_player_ids: Optional[Sequence[str]] = None,
    data: Optional[Dict[str, Any]] = None,
    url: Optional[str] = None,
    timeout: int = 5
) -> bool:
    """
    Send a push notification via OneSignal.
    Returns True on success, False on failure.
    """
    # If OneSignal not configured, skip and return False (or True if you prefer silent success)
    if not ONESIGNAL_APP_ID or not ONESIGNAL_API_KEY:
        print("⚠️  OneSignal not configured (ONESIGNAL_APP_ID/ONESIGNAL_API_KEY missing). Notification skipped.")
        return False

    # OneSignal REST API Key format: "Basic <REST_API_KEY>"
    # The REST API Key from OneSignal dashboard should be used directly
    # Note: Make sure ONESIGNAL_API_KEY in .env is your REST API Key (not App ID)
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": f"Basic {ONESIGNAL_API_KEY}"
    }

    # build include_player_ids from env if caller didn't provide
    player_ids = None
    if include_player_ids:
        player_ids = list(include_player_ids)
    elif ONESIGNAL_PLAYER_IDS:
        # support comma-separated list in env
        player_ids = [p.strip() for p in ONESIGNAL_PLAYER_IDS.split(",") if p.strip()]

    payload = {
        "app_id": ONESIGNAL_APP_ID,
        "headings": {"en": title},
        "contents": {"en": message},
    }
    if player_ids:
        payload["include_player_ids"] = player_ids
    else:
        # If no player ids, send to all subscribers (use with caution)
        payload["included_segments"] = ["Subscribed Users"]

    if data:
        payload["data"] = data
    if url:
        payload["url"] = url

    try:
        resp = requests.post(ONESIGNAL_API_URL, json=payload, headers=headers, timeout=timeout)
        if 200 <= resp.status_code < 300:
            print(f"✅ OneSignal notification sent: {title}")
            return True
        else:
            print(f"❌ OneSignal error: status={resp.status_code} body={resp.text}")
            return False
    except requests.RequestException as e:
        print(f"❌ OneSignal request failed: {e}")
        return False
