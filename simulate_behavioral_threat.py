import time
import os
import threading
import math

print("--- FAKE BEHAVIORAL THREAT STARTED ---")
print(f"PID: {os.getpid()}")
print("Generating massive thread count and anomalous memory allocation to trigger the AMD NPU autoencoder...")

def CPU_hog():
    # Attempt to burn CPU and allocating memory rapidly
    dummy_memory = []
    while True:
        try:
            for i in range(10000):
                math.sqrt(i * 10.5)
            dummy_memory.append('A' * 1024 * 100) # Fast allocation
        except MemoryError:
            dummy_memory.clear()

threads = []
print("Spinning up 250 dummy worker threads...")
for i in range(250):
    t = threading.Thread(target=CPU_hog, daemon=True)
    threads.append(t)
    t.start()
    if i % 50 == 0:
        print(f"[{i}/250] Threads alive...")

print("Threads established. Awaiting EDR Agent isolation...")
print("If the AMD Ryzen ML model calculates an MSE anomaly score greater than the threshold, this process will terminate abruptly.")

try:
    for i in range(60):
        print(f"Malware running erratically... ({i}/60)")
        time.sleep(1)
except KeyboardInterrupt:
    print("Manually stopped.")
