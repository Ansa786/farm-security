import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env at project root
load_dotenv()

ONESIGNAL_APP_ID = os.getenv("ONESIGNAL_APP_ID")        # Must be set in your .env file
ONESIGNAL_API_KEY = os.getenv("ONESIGNAL_API_KEY")      # Must be set in your .env file

def send_push_notification(player_id: str, title: str, message: str):
    """
    Sends a push notification to the given player_id using OneSignal.
    """
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
    response = requests.post(url, headers=headers, json=payload)
    print("Status:", response.status_code)
    print("Response:", response.json())
    return response.status_code, response.json()
