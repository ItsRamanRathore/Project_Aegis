import socket
import time
import threading

TARGET_HOST = "127.0.0.1"
TARGET_PORT = 8000
NUM_CONNECTIONS = 60 # More than MAX_CONNS_PER_IP (which is 50)

sockets = []

def open_socket(i):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        s.connect((TARGET_HOST, TARGET_PORT))
        sockets.append(s)
        print(f"[{i}] Raw socket connected.")
        # Hold the connection open
        time.sleep(10)
    except Exception as e:
        print(f"[{i}] Socket failed: {e}")

print(f"[*] Simulating raw OS-level socket flood towards {TARGET_HOST}:{TARGET_PORT}...")
threads = []
for i in range(NUM_CONNECTIONS):
    t = threading.Thread(target=open_socket, args=(i,))
    threads.append(t)
    t.start()
    time.sleep(0.01) # Stagger slightly

for t in threads:
    t.join()
    
print("[*] Closing sockets...")
for s in sockets:
    try:
        s.close()
    except:
        pass
        
print("[*] Flood test complete. Check Aegis dashboard for NETWORK BAN alert.")
