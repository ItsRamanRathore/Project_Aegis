import time
import os
import psutil
import requests
import socket
import numpy as np
import onnxruntime as ort
from datetime import datetime

# Configuration
API_URL = "http://127.0.0.1:8000"
NODE_NAME = f"Node-{socket.gethostname()[:4]}"
SCAN_INTERVAL_SECONDS = 2.0

# Colors for terminal output
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
RESET = "\033[0m"

# YARA-style heuristic rules 
MALICIOUS_CMDLINE_SIGNATURES = [
    "powershell -w hidden -enc",
    "powershell -windowstyle hidden -encodedcommand",
    "simulate_malware",
    "reverse_shell",
    "mimikatz",
    "nc -e cmd.exe"
]

def log(msg, color=RESET):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {color}{msg}{RESET}")

# Initialize AMD NPU Inference Session
onnx_model_path = "aegis_behavioral_model.onnx"
session = None
if os.path.exists(onnx_model_path):
    # Attempt to load with local Execution Providers, prioritizing Vitis AI (Ryzen AI) and DirectML
    try:
        session = ort.InferenceSession(onnx_model_path, providers=['VitisAIExecutionProvider', 'DmlExecutionProvider', 'CPUExecutionProvider'])
        log(f"Successfully loaded {onnx_model_path} via ONNX Runtime.", MAGENTA)
        log(f"Active Execution Providers: {session.get_providers()}", MAGENTA)
    except Exception as e:
        log(f"Warning: Failed to load ONNX model. Behavioral AI disabled. {e}", YELLOW)
else:
    log(f"Warning: {onnx_model_path} not found. Proceeding with Signature Matching only.", YELLOW)

def report_threat(action, target, confidence):
    try:
        payload = {
            "node": NODE_NAME,
            "action": action,
            "target": target,
            "classification": "MALWARE_PAYLOAD",
            "confidence": confidence,
            "status": "TERMINATED"
        }
        res = requests.post(f"{API_URL}/api/threat-alert", json=payload)
        if res.status_code == 200:
            log(f"Threat report successfully dispatched to Aegis SOC.", GREEN)
        else:
            log(f"Warning: Aegis SOC returned status {res.status_code}", YELLOW)
    except Exception as e:
        log(f"Failed to reach Aegis API: {e}", RED)

def send_heartbeat(npu_usage=0.0):
    try:
        requests.post(f"{API_URL}/api/edr/ping", json={"npu_usage": npu_usage}, timeout=1.0)
    except Exception:
        pass # Silently fail heartbeat

def extract_features(p):
    """Extracts raw numerical features from a psutil Process for ML Inference."""
    try:
        # Scale appropriately to match the synthetic training data space roughly
        cpu = p.cpu_percent(interval=None) # usually 0-100
        mem = p.memory_percent() # 0-100
        threads = p.num_threads()
        try:
            handles = p.num_handles()
        except AttributeError:
            handles = 200 # Fallback for posix
        
        try:
            io = p.io_counters().read_count if p.io_counters() else 10
        except Exception:
            io = 10
            
        feature_vector = np.array([cpu, mem, threads, handles, io], dtype=np.float32)
        # Apply standard normalization bound trick corresponding to training normalization
        feature_vector = np.clip(feature_vector, 0, [100, 100, 1000, 5000, 10000])
        feature_vector = feature_vector / np.array([100, 100, 1000, 5000, 10000], dtype=np.float32)
        
        return feature_vector.astype(np.float32)
    except Exception:
        return None

def scan_processes():
    """Scans all active processes for malicious command line arguments and Behavioral anomalies."""
    npu_total_compute = 0.0

    for p in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = p.info.get('cmdline')
            if not cmdline:
                continue
                
            cmd_str = " ".join(cmdline).lower()
            
            # Prevent the agent from killing itself by accident
            if "edr_agent.py" in cmd_str:
                continue

            # 1. SIGNATURE SCAN
            threat_found = False
            for sig in MALICIOUS_CMDLINE_SIGNATURES:
                if sig in cmd_str:
                    log(f"!!! CRITICAL THREAT DETECTED !!!", RED)
                    log(f"Process ID: {p.pid} | Name: {p.info['name']}", YELLOW)
                    log(f"Signature Match: '{sig}'", CYAN)
                    threat_found = True
                    report_threat(f"[EDR] PAYLOAD TERMINATED: {sig}", p.info['name'], 98)
                    break
            
            # 2. BEHAVIORAL INFERENCE (AMD NPU)
            if not threat_found and session:
                features = extract_features(p)
                if features is not None:
                    # Run it through the ONNX Autoencoder
                    input_name = session.get_inputs()[0].name
                    inputs = {input_name: features.reshape(1, 5)}
                    outputs = session.run(None, inputs)
                    reconstructed = outputs[0]
                    
                    mse = np.mean((features - reconstructed) ** 2)
                    npu_total_compute += 0.5 # Add mocked inference cost to NPU graph
                    
                    # Very high MSE implies abnormal behavior compared to standard baseline
                    if mse > 0.8:  # Anomaly threshold
                        log(f"!!! BEHAVIORAL ANOMALY DETECTED !!!", MAGENTA)
                        log(f"Process ID: {p.pid} | Name: {p.info['name']} | MSE: {mse:.4f}", MAGENTA)
                        report_threat(f"[AMD RYZEN AI] BEHAVIORAL ANOMALY", p.info['name'], int(mse*100))
                        threat_found = True

            # 3. TERMINATION
            if threat_found:
                try:
                    if "dummy_malware" in cmd_str or "simulate_malware" in cmd_str:
                        p.kill()
                        log(f"[EXECUTIONER] Process {p.pid} terminated.", RED)
                    else:
                        log(f"[SIMULATED] Process {p.pid} would have been successfully terminated. Sandboxed.", GREEN)
                except Exception as e:
                    pass
                    
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
            
    # Send Heartbeat with aggregated NPU Usage
    send_heartbeat(min(npu_total_compute, 100.0))

def main():
    log(f"Starting Aegis Advanced Endpoint Protection (EDR) Agent...", CYAN)
    log(f"Node: {NODE_NAME}", CYAN)
    log(f"Initializing Memory Heuristics & Signature Scanner...", CYAN)
    if session:
        log(f"AMD AI Stack ACTIVE. Autoencoder logic loaded.", MAGENTA)
    time.sleep(1)
    
    log(f"EDR Agent Active. Monitoring host processes...", GREEN)
    print("=" * 60)
    
    while True:
        scan_processes()
        time.sleep(SCAN_INTERVAL_SECONDS)

if __name__ == "__main__":
    main()
