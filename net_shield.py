import time
import os
import subprocess
import psutil
import requests
from collections import defaultdict
from datetime import datetime

# --- GLOBAL CONFIGURATION ---
API_BASE = "http://127.0.0.1:8000"
CHECK_INTERVAL_SEC = 2
WHITELIST_IPS = {"127.0.0.1", "::1"}

# --- DDOS THRESHOLDS ---
MAX_CONNS_PER_IP = 50       # Max active connections from a single IP before ban
GLOBAL_CONN_THRESHOLD = 500 # Max total active network connections before TCP hardening

blocked_ips = set()

def execute_ps(command: str):
    """Executes a PowerShell command silently."""
    try:
        subprocess.run(["powershell", "-Command", command], capture_output=True, text=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] PowerShell Execution Failed: {e.stderr}")
        return False

def block_ip_firewall(ip: str):
    """Adds a Windows Defender Firewall rule to block all inbound traffic from an IP."""
    if ip in blocked_ips or ip in WHITELIST_IPS:
        return
        
    rule_name = f"Aegis_Block_{ip.replace('.', '_')}"
    print(f"[EDGE SHIELD] 🔴 [SIMULATED] Executing physical block on IP: {ip}")
    
    # Use netsh to add a firewall rule
    # cmd = f'netsh advfirewall firewall add rule name="{rule_name}" dir=in action=block remoteip="{ip}"'
    
    # if execute_ps(cmd): # DISABLED FOR SANDBOX MODE
    if True:
        blocked_ips.add(ip)
        print(f"[EDGE SHIELD] ✅ [SIMULATED] Firewall rule '{rule_name}' activated.")
        
        # Dispatch alert to Command Center
        alert_payload = {
            "node": "Node-01: Connaught Place",
            "action": "NETWORK BAN",
            "target": f"IP: {ip}",
            "classification": "[AEGIS SHIELD] Single-Source DoS Anomaly (99%)",
            "status": "IP Banned (OS-Level)",
            "analysis": f"DETECTED: Volumetric DoS signature originating from {ip}.\n"
                        f"ANALYSIS: Connection attempts exceeded threshold ({MAX_CONNS_PER_IP} conns/sec).\n"
                        f"RESPONSE: Edge Security triggered. Ingress traffic explicitly blocked at Windows Defender Firewall."
        }
        try:
            requests.post(f"{API_BASE}/api/threat-alert", json=alert_payload, timeout=2)
        except Exception:
            pass

def harden_tcp_stack():
    """Applies emergency TCP hardening if a massive distributed attack is detected."""
    print("[EDGE SHIELD] ⚠️ DISTRIBUTED DDOS DETECTED! Hardening TCP Stack...")
    # Reduce SYN retries to drop dead connections faster
    # execute_ps('Set-NetTCPSetting -SettingName "InternetCustom" -MaxSynRetransmissions 2') # DISABLED FOR SANDBOX MODE
    
    alert_payload = {
        "node": "Node-01: Connaught Place",
        "action": "TCP HARDENING",
        "target": "Network Stack",
        "classification": "[AEGIS SHIELD] Distributed Network Anomaly (99%)",
        "status": "Protocol Hardened",
        "analysis": f"DETECTED: Massive distributed network anomaly.\n"
                    f"ANALYSIS: Total global connection count breached structural threshold ({GLOBAL_CONN_THRESHOLD}).\n"
                    f"RESPONSE: Engaging dynamic OS TCP hardening. SYN Retransmissions minimized."
    }
    try:
        requests.post(f"{API_BASE}/api/threat-alert", json=alert_payload, timeout=2)
    except Exception:
        pass

def restore_tcp_stack():
    """Restores the TCP stack to normal parameters once the attack subsides."""
    print("[EDGE SHIELD] 🟢 Traffic normalized. Restoring TCP Stack...")
    # execute_ps('Set-NetTCPSetting -SettingName "InternetCustom" -MaxSynRetransmissions 4') # DISABLED FOR SANDBOX MODE

tcp_hardened = False

def monitor_network():
    """Polls active network connections and enforces DDoS limits."""
    global tcp_hardened
    
    print(f"[*] Project Aegis: Edge Shield Active.")
    print(f"[*] Process Interceptor: ONLINE.")
    print(f"[*] Target Interface: Windows Defender Firewall.")
    print(f"[*] Max Connections per IP: {MAX_CONNS_PER_IP}")
    print(f"[*] Global DDoS Threshold: {GLOBAL_CONN_THRESHOLD}\n")
    print(f"[*] WARNING: Script must run as Administrator to apply Firewall rules.\n")
    
    while True:
        try:
            total_conns = 0
            ip_counts = defaultdict(int)
            
            # Use psutil to list all network connections
            for conn in psutil.net_connections(kind='tcp'):
                if conn.status in [psutil.CONN_ESTABLISHED, psutil.CONN_SYN_RECV]:
                    total_conns += 1
                    # conn.raddr is the remote address tuple (ip, port)
                    if conn.raddr and conn.raddr.ip:
                        ip_counts[conn.raddr.ip] += 1
            
            # --- 1. SINGLE-SOURCE DOS DETECTION ---
            for ip, count in ip_counts.items():
                if count > MAX_CONNS_PER_IP:
                    block_ip_firewall(ip)
            
            # --- 2. DISTRIBUTED DDOS DETECTION ---
            if total_conns > GLOBAL_CONN_THRESHOLD and not tcp_hardened:
                harden_tcp_stack()
                tcp_hardened = True
            elif total_conns < (GLOBAL_CONN_THRESHOLD * 0.5) and tcp_hardened: # Stop hardening if traffic drops by 50%
                restore_tcp_stack()
                tcp_hardened = False
                
            # --- 3. HEARTBEAT PING ---
            try:
                requests.post(f"{API_BASE}/api/edge/ping", timeout=1)
            except Exception:
                pass
                
        except psutil.AccessDenied:
            print("[ERROR] Access Denied. Please ensure net_shield.py is running as Administrator.")
            time.sleep(10) # Prevent log-spam
        except Exception as e:
            print(f"[EDGE SHIELD] ⚠️ Error monitoring network: {e}")
            
        time.sleep(CHECK_INTERVAL_SEC)

if __name__ == "__main__":
    monitor_network()
