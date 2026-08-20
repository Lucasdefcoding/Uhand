# client.py (Runs on your laptop connected to hotspot)
import time
import requests

# Replace with the active link generated in Terminal 4 by cloudflared
API_URL = "https://xxxxxxxx.trycloudflare.com/gesture"

def send_gesture(gesture_name: str):
    headers = {"Content-Type": "application/json"}
    payload = {"gesture": gesture_name}

    try:
        response = requests.post(API_URL, json=payload, timeout=5)
        print(f"Sent Gesture: '{gesture_name}' | Status: {response.status_code} -> {response.json()}")

    except Exception as e:
        print(f"Failed to send signal for '{gesture_name}': {e}")

if __name__ == '__main__':
    # List of string gestures matching Terminal 3 commands
    gestures_to_test = [
        "peace",
        "palm_open",
        "palm_forward",
        "thumb_down",
        "thumb_up",
        "make_fist",
        "ok",
        "wave"
    ]
    
    for g in gestures_to_test:
        send_gesture(g)
        time.sleep(10)  # Wait 3 seconds between gestures to allow arm movement
