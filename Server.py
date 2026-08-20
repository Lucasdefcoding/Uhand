# Fixed IP Server)
from flask import Flask, jsonify
import socket

app = Flask(__name__)

# Network config for the Robot's Computer (Local Network / Direct Connection)
ROBOT_IP = "robot_arm.local"  # local hostname/mDNS
ROBOT_PORT = 5000

def send_to_robot(gesture_number: int):
    #sends the gesture number to robot through socket
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(3.0) # 3-second connection timeout
            s.connect((ROBOT_IP, ROBOT_PORT))
            
            # Send the number as a string encoded to bytes
            msg = str(gesture_number)
            s.sendall(msg.encode('utf-8'))
            
            # Optional: Read response from robot
            response = s.recv(1024).decode('utf-8')
            return True, response
    except Exception as e:
        return False, str(e)

@app.route('/gesture/<int:code>', methods=['GET', 'POST'])
def handle_gesture(code):
    # Validate signal range (0 to 5)
    if code < 0 or code > 5:
        return jsonify({"status": "error", "message": "Signal must be between 0 and 5"}), 400

    print(f"Received HTTP signal for Gesture #{code}")

    # Forward signal to Robot via TCP Socket
    success, result = send_to_robot(code)

    if success:
        return jsonify({
            "status": "success", 
            "gesture_sent": code, 
            "robot_ack": result
        }), 200
    else:
        return jsonify({
            "status": "failed_to_reach_robot", 
            "error": result
        }), 500

if __name__ == '__main__':
    # '0.0.0.0' allows external incoming HTTP requests from phone/hotspot
    app.run(host='0.0.0.0', port=65301)