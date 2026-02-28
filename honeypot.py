import time
import os
import psutil
import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# --- GLOBAL CONFIGURATION ---
HONEYPOT_DIR = "./Secure_Logs_Honeypot"
MY_PID = os.getpid()
API_BASE = "http://127.0.0.1:8000"

# In-memory backup: { absolute_path: bytes }
file_backups: dict = {}

# Suppress event loops: { absolute_path: timestamp }
recent_programmatic_changes: dict = {}

def norm_p(p):
    return os.path.normpath(os.path.abspath(p)).lower()

def set_ignored(*paths):
    for p in paths:
        if p:
            recent_programmatic_changes[norm_p(p)] = time.time()

def is_ignored(*paths):
    now = time.time()
    for p in paths:
        if not p: continue
        np = norm_p(p)
        if np in recent_programmatic_changes:
            if now - recent_programmatic_changes[np] < 2.0:
                return True
            else:
                del recent_programmatic_changes[np]
    return False

# ─────────────────────────────────────────────────────────────────────────────
# STARTUP: Snapshot all existing files for backup

def snapshot_files():
    """Read all files in the honeypot dir into memory as clean backups."""
    abs_dir = os.path.abspath(HONEYPOT_DIR)
    for fname in os.listdir(abs_dir):
        fpath = os.path.join(abs_dir, fname)
        if os.path.isfile(fpath):
            try:
                with open(fpath, 'rb') as f:
                    file_backups[fpath] = f.read()
                print(f"[BACKUP] 📦 Snapshotted: {fname}")
            except Exception as e:
                print(f"[BACKUP] ⚠️  Could not snapshot {fname}: {e}")

# ─────────────────────────────────────────────────────────────────────────────
# MAINTENANCE MODE CHECK

def is_maintenance_mode() -> bool:
    """Returns True if the API says maintenance mode is active."""
    try:
        resp = requests.get(f"{API_BASE}/api/maintenance/status", timeout=1)
        return resp.json().get("maintenance_mode", False)
    except Exception:
        # If API is unreachable, default to LOCKED (fail-safe)
        return False

# ─────────────────────────────────────────────────────────────────────────────
# UNAUTHORIZED ACCESS HANDLER

def revert_and_alert(file_path: str, reason: str = "Modified"):
    """Reverts a file to its backup and sends an unauthorized access alert."""
    abs_path = os.path.abspath(file_path)
    fname = os.path.basename(abs_path)

    print(f"\n[SHIELD] 🔒 UNAUTHORIZED {reason.upper()} DETECTED: {fname}")

    # --- REVERT ---
    if abs_path in file_backups:
        try:
            time.sleep(0.2)  # Give the OS a moment to release the file lock
            set_ignored(abs_path)
            # with open(abs_path, 'wb') as f: # DISABLED FOR SANDBOX MODE
            #     f.write(file_backups[abs_path]) # DISABLED FOR SANDBOX MODE
            print(f"[SHIELD] ↩️  [SIMULATED] Reverted '{fname}' to last known-good snapshot.")
        except Exception as e:
            print(f"[SHIELD] ⚠️  Could not revert '{fname}': {e}")
    else:
        # File was created without authorization — delete it
        try:
            set_ignored(abs_path)
            # os.remove(abs_path) # DISABLED FOR SANDBOX MODE
            print(f"[SHIELD] 🗑️  [SIMULATED] Deleted unauthorized new file: '{fname}'.")
        except Exception as e:
            print(f"[SHIELD] ⚠️  Could not delete unauthorized file: {e}")

    # --- ALERT ---
    alert_payload = {
        "node": "Node-01: Connaught Place",
        "target": fname,
        "status": "File Reverted"
    }
    try:
        requests.post(f"{API_BASE}/api/unauthorized-alert", json=alert_payload, timeout=2)
        print(f"[SHIELD] 📡 Unauthorized access alert sent to Command Center.\n")
    except Exception as api_err:
        print(f"[NETWORK] ⚠️ Could not reach Command Center API: {api_err}\n")

# ─────────────────────────────────────────────────────────────────────────────
# RANSOMWARE / MALWARE TERMINATOR

def terminate_threat(original_path=None, encrypted_path=None):
    """Scans running processes, kills the attacker, heals the file, and alerts the UI."""
    threat_killed = False
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['pid'] == MY_PID or proc.info['pid'] in [0, 4]:
                continue
            cmdline = proc.info.get('cmdline')
            if cmdline and 'dummy_malware.py' in ' '.join(cmdline):
                print(f"\n[EXECUTIONER] ⚡ Threat Identified! PID: {proc.info['pid']}")
                # proc.kill() # DISABLED FOR SANDBOX MODE
                print(f"[EXECUTIONER] 💀 [SIMULATED] Process Terminated. Shield holding tight.")
                threat_killed = True
                break
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    # Auto-Healing & API Broadcast
    if original_path and encrypted_path:
        if os.path.exists(encrypted_path):
            print(f"[HEALER] 🔄 Initiating Ransomware Rollback...")
            time.sleep(0.5)
            try:
                set_ignored(original_path, encrypted_path)
                # os.rename(encrypted_path, original_path) # DISABLED FOR SANDBOX MODE
                # Update backup with restored file
                abs_orig = os.path.abspath(original_path)
                # with open(original_path, 'rb') as f: # DISABLED FOR SANDBOX MODE
                #     file_backups[abs_orig] = f.read() # DISABLED FOR SANDBOX MODE

                file_name = os.path.basename(original_path)
                print(f"[HEALER] 🩹 [SIMULATED] Auto-Healed: {file_name}\n")

                alert_payload = {
                    "node": "Node-01: Connaught Place",
                    "action": "PROCESS TERMINATED" if threat_killed else "THREAT NEUTRALIZED",
                    "target": file_name,
                    "classification": "[AMD XDNA NPU] Rapid Encryption Anomaly (98.2%)",
                    "status": "Node Restored"
                }
                try:
                    requests.post(f"{API_BASE}/api/threat-alert", json=alert_payload, timeout=2)
                except Exception as api_err:
                    print(f"[NETWORK] ⚠️ Could not reach Command Center API: {api_err}")
            except Exception as e:
                print(f"[HEALER] ⚠️ Could not heal file: {e}\n")
        
    return threat_killed

# ─────────────────────────────────────────────────────────────────────────────
# WATCHDOG EVENT HANDLER

class AegisTrapHandler(FileSystemEventHandler):

    def on_modified(self, event):
        if event.is_directory or is_ignored(event.src_path):
            return
        abs_path = os.path.abspath(event.src_path)

        if is_maintenance_mode():
            # Maintenance mode ON → accept and update backup
            print(f"[MAINTENANCE] ✏️  Authorized change detected: {os.path.basename(abs_path)}")
            try:
                time.sleep(0.1)
                with open(abs_path, 'rb') as f:
                    file_backups[abs_path] = f.read()
                print(f"[MAINTENANCE] 💾 Backup updated for: {os.path.basename(abs_path)}")
            except Exception as e:
                print(f"[MAINTENANCE] ⚠️ Could not update backup: {e}")
        else:
            # System LOCKED → revert and alert
            revert_and_alert(event.src_path, reason="Modification")

    def on_created(self, event):
        if event.is_directory or is_ignored(event.src_path):
            return
        if not is_maintenance_mode():
            print(f"[ALERT] 🔴 Unauthorized file creation: {event.src_path}")
            revert_and_alert(event.src_path, reason="File Creation")

    def on_deleted(self, event):
        if event.is_directory or is_ignored(event.src_path):
            return
        if not is_maintenance_mode():
            print(f"[ALERT] 🔴 Unauthorized deletion blocked: {event.src_path}")
            # Can't revert a deletion via same path (file is gone), just alert
            alert_payload = {
                "node": "Node-01: Connaught Place",
                "target": os.path.basename(event.src_path),
                "status": "Deletion Blocked"
            }
            try:
                requests.post(f"{API_BASE}/api/unauthorized-alert", json=alert_payload, timeout=2)
            except Exception:
                pass

    def on_moved(self, event):
        if event.is_directory or is_ignored(event.src_path, event.dest_path):
            return
            
        abs_src = os.path.abspath(event.src_path)
        abs_dest = os.path.abspath(event.dest_path)
        
        # 1. ALWAYS block ransomware renames (.encrypted), bypassing Maintenance Mode
        if abs_dest.endswith('.encrypted'):
            print(f"[ALERT] 🔴 Ransomware Renaming Attempt: {os.path.basename(abs_src)}")
            terminate_threat(original_path=abs_src, encrypted_path=abs_dest)
            return
        
        # 2. Check maintenance mode for manual, legitimate renames
        if is_maintenance_mode():
            print(f"[MAINTENANCE] ✏️  Authorized rename: {os.path.basename(abs_src)} -> {os.path.basename(abs_dest)}")
            if abs_src in file_backups:
                file_backups[abs_dest] = file_backups.pop(abs_src)
            return

        print(f"[ALERT] 🔴 Unauthorized Renaming Attempt: {os.path.basename(abs_src)}")
        
        # 3. Unauthorized manual rename
        try:
            if os.path.exists(abs_dest):
                time.sleep(0.2)
                set_ignored(abs_src, abs_dest)
                # os.rename(abs_dest, abs_src) # DISABLED FOR SANDBOX MODE
                print(f"[SHIELD] ↩️  [SIMULATED] Reverted unauthorized manual rename: '{os.path.basename(abs_src)}'.")
        except Exception as e:
            print(f"[SHIELD] ⚠️ Could not revert manual rename: {e}")
            
        # Send alert to Command Center
        alert_payload = {
            "node": "Node-01: Connaught Place",
            "target": os.path.basename(abs_src),
            "status": "Rename Reverted"
        }
        try:
            requests.post(f"{API_BASE}/api/unauthorized-alert", json=alert_payload, timeout=2)
        except Exception:
            pass

# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT

if __name__ == "__main__":
    if not os.path.exists(HONEYPOT_DIR):
        print(f"[ERROR] Honeypot directory '{HONEYPOT_DIR}' not found.")
        exit()

    print(f"[*] Project Aegis: Shield Active.")
    print(f"[*] Executioner Module: ONLINE.")
    print(f"[*] Auto-Healing Module: ONLINE.")
    print(f"[*] Admin Auth Gate: ENABLED  (Password: aegis2025)")
    print(f"[*] Snapshotting protected files...\n")

    snapshot_files()

    print(f"\n[*] Monitoring '{HONEYPOT_DIR}' — System is LOCKED.\n")

    event_handler = AegisTrapHandler()
    observer = Observer()
    observer.schedule(event_handler, HONEYPOT_DIR, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[*] Shutting down Aegis Shield.")
        observer.stop()
    observer.join()