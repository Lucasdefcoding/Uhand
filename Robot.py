import socket

HOST = '0.0.0.0' # Listen for TCP socket from Central Server
PORT = 5000

def start_robot():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen()
        print(f"Robot listener ready on port {PORT}...")

        while True:
            conn, addr = server.accept()
            with conn:
                data = conn.recv(1024)
                if data:
                    try:
                        # Convert received byte message back to integer 0-5
                        signal_num = int(data.decode('utf-8').strip())
                        
                        # Return acknowledgment back to Central Server
                        conn.sendall(f"DONE:{signal_num}".encode('utf-8'))
                    except ValueError:
                        print("Received non-numeric data!")

if __name__ == '__main__':
    start_robot()