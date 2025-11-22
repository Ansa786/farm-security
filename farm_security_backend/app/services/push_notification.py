import os
import requests
from dotenv import load_dotenv
from typing import Optional, Sequence, Dict, Any

# Load environment variables from .env at project root
load_dotenv()

ONESIGNAL_API_URL = "https://api.onesignal.com/notifications"
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
    print(f"\n📱 Attempting to send notification...")
    print(f"   Title: {title}")
    print(f"   Message: {message}")
    
    # If OneSignal not configured, skip and return False (or True if you prefer silent success)
    if not ONESIGNAL_APP_ID or not ONESIGNAL_API_KEY:
        print("⚠️  OneSignal not configured (ONESIGNAL_APP_ID/ONESIGNAL_API_KEY missing). Notification skipped.")
        return False

    print(f"   App ID: {ONESIGNAL_APP_ID}")
    print(f"   API Key: {ONESIGNAL_API_KEY[:20]}...")

    # OneSignal v2 API - use the REST API Key with proper format
    # For os_v2_app_* keys, don't use "Basic" or "Bearer", just the key directly
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": ONESIGNAL_API_KEY  # Use key directly without prefix
    }
    print(f"   Using OneSignal v2 API")

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
        print(f"   Sending to specific players: {player_ids}")
        payload["include_player_ids"] = player_ids
    else:
        # If no player ids, send to all subscribers (use with caution)
        print(f"   Sending to all subscribed users")
        payload["included_segments"] = ["Subscribed Users"]

    if data:
        payload["data"] = data
    if url:
        payload["url"] = url

    try:
        print(f"   Sending request to OneSignal...")
        resp = requests.post(ONESIGNAL_API_URL, json=payload, headers=headers, timeout=timeout)
        print(f"   Response status: {resp.status_code}")
        print(f"   Response body: {resp.text}")
        
        if 200 <= resp.status_code < 300:
            print(f"✅ OneSignal notification sent successfully!")
            return True
        else:
            print(f"❌ OneSignal error: status={resp.status_code}")
            return False
    except requests.RequestException as e:
        print(f"❌ OneSignal request failed: {e}")
        return False
