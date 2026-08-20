# client.py (Runs on your laptop connected to hotspot)
import socket
import time
import requests

#HOST = 'YOUR_SERVER_FIXED_IP'  # Replace with your server's public/fixed IP
#PORT = 8080                    # Port matching your Flask server

BASE_URL= "https://xxxxxxxx.trycloudflare.com/gesture"

def send_gesture(gesture_num: int):

    url = f"{BASE_URL}/{gesture_num}"

    try:
        response = requests.post(url, timeout=5)
        print(f"Status: {response.status_code} | Response: {response.json()}")

    except Exception as e:
        print(f"Failed to send signal: {e}")

if __name__ == '__main__':
    # List of integer signals (0 through 5)
    gestures_to_test = [0, 1, 2, 3, 4, 5]
    
    for g in gestures_to_test:
        send_gesture(g)
        time.sleep(3)  # Wait 3 seconds between commands