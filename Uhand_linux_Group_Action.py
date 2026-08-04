import serial
import time
import sys
import select
import tty
import termios

PORT = '/dev/ttyUSB1' 
BAUD = 9600

# Open Serial Connection
ser = serial.Serial(PORT, BAUD, timeout=1)
time.sleep(2)  # Wait for Arduino Nano reset


OPEN_POS = 2000
CLOSE_POS = 1000
MOVE_TIME = 300  

# Track state for Servos 1-6 (True = Open, False = Closed)
finger_states = {1: True, 2: True, 3: True, 4: True, 5: True, 6: True}

def run_action_group(group_id, times=1):
    """
    Triggers a pre-saved action group stored in the uHand's flash memory.
    
    :param group_id: The number/ID of the action group (0, 1, 2, ...)
    :param times: How many times to repeat the action group (1 = once, 0 = loop infinitely)
    """
    length = 5
    cmd = 0x06  # CMD_ACTION_GROUP_RUN

    # Split repeat count into Low and High bytes
    times_low = times & 0xFF
    times_high = (times >> 8) & 0xFF

    packet = bytearray([
        0x55, 0x55,    # Header
        length,        # Length (5)
        cmd,           # Command (0x06)
        group_id,      # Action Group Number
        times_low,     # Repeat Count Low Byte
        times_high     # Repeat Count High Byte
    ])

    ser.write(packet)
    print(f"Triggered Action Group {group_id} (Repeat count: {times})")



def move_single_finger(servo_id, position, duration_ms=300):
    length = 8
    cmd = 0x03
    servo_count = 1

    packet = bytearray([
        0x55, 0x55,                    # Header
        length,                        # Payload Length
        cmd,                           # 0x03 Command
        servo_count,                   # 1 Servo
        duration_ms & 0xFF,            # Duration Low Byte
        (duration_ms >> 8) & 0xFF,     # Duration High Byte
        servo_id,                      # Servo ID (1-6)
        position & 0xFF,               # Position PWM Low Byte
        (position >> 8) & 0xFF         # Position PWM High Byte
    ])

    ser.write(packet)

def toggle_finger(servo_id):
    current_state = finger_states[servo_id]
    target_pos = CLOSE_POS if current_state else OPEN_POS
    finger_states[servo_id] = not current_state

    state_text = "CLOSING" if current_state else "OPENING"
    print(f"\rFinger {servo_id} -> {state_text} (PWM: {target_pos})    ", end="")

    move_single_finger(servo_id, target_pos, MOVE_TIME)

#linux helper to catch keypresses
def get_key_non_blocking():
    if select.select([sys.stdin], [], [], 0)[0]:
        return sys.stdin.read(1)
    return None

# Main Instant Key-Listener Loop
if __name__ == "__main__":
    print("\n--- uHand Instant Keyboard Control ---")
    print("Tap '1' through '6' to instantly toggle fingers.")
    print("Press 'q' or ESC to exit.\n")
    print("Press 'g' for group action mode")
    print("Press 's' for single action mode")

    # Save original terminal settings
    old_settings = termios.tcgetattr(sys.stdin) 

    try:

        tty.setcbreak(sys.stdin.fileno())

        while True:

            key_char = get_key_non_blocking()

            if key_char:
                key_char = key_char.lower()

                if key_char == 'q' or key_char == '\x1b':  # 'q' or ESC key
                    print("\nExiting program.")
                    break

                if key_char == 'g':
                    print("\nGroup Action mode")

                    while key_char != 's':
                        key_char = get_key_non_blocking()
                        key_char = key_char.lower()

                        if key_char.isdigit():
                            num = int(key_char)
                            run_action_group(num)

                        if key_char == 'q' or key_char == '\x1b':  # 'q' or ESC key
                            print("\nExiting program.")
                            break

                if key_char == 's':
                    print("\nSingle Action mode")

                    while key_char != 'g':
                        key_char = get_key_non_blocking()
                        key_char = key_char.lower()

                        if key_char.isdigit():
                            num = int(key_char)
                            if 1 <= num <= 6:
                                toggle_finger(num)
                                
                        if key_char == 'q' or key_char == '\x1b':  # 'q' or ESC key
                            print("\nExiting program.")
                            break
        
            time.sleep(0.01) 

    finally:
        termios.tcsetattr(sys.stdin, termios.TCSANOW, old_settings)
        ser.close()