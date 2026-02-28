import subprocess
import sys
import time
import os
import ctypes

os.environ["PYTHONIOENCODING"] = "utf-8"

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def main():
    if not is_admin():
        print("[WARNING] Project Aegis Orchestrator is NOT running as Administrator.")
        print("Network Edge Shield and some EDR capabilities may be limited.")
        print("For full protection, please run from an elevated command prompt.\n")

    print("=" * 60)
    print("Project Aegis: Initializing Central Defense Orchestrator")
    print("=" * 60 + "\n")

    # Determine Python executable (prefer venv if it exists)
    venv_python = os.path.join(os.path.dirname(os.path.abspath(__file__)), "venv", "Scripts", "python.exe")
    python_exe = venv_python if os.path.exists(venv_python) else sys.executable
    print(f"[*] Using Python executable: {python_exe}\n")

    # Define the scripts to run
    scripts = [
        ("API & Command Center", "api.py", [python_exe, "-m", "uvicorn", "api:app", "--host", "127.0.0.1", "--port", "8000", "--reload"]),
        ("EDR Agent", "edr_agent.py", [python_exe, "edr_agent.py"]),
        ("Network Edge Shield", "net_shield.py", [python_exe, "net_shield.py"]),
        ("File System Honeypot", "honeypot.py", [python_exe, "honeypot.py"]),
        ("Cognitive Mind Agent", "mind.py", [python_exe, "mind.py"])
    ]

    processes = []
    
    try:
        # Start API first and wait a bit for it to be ready
        name, filename, cmd = scripts[0]
        if os.path.exists(filename):
            print(f"[*] Starting {name}...")
            p = subprocess.Popen(cmd)
            processes.append((name, p))
            time.sleep(3) # Give API time to bind to port
        else:
            print(f"[ERROR] Could not find {filename}")

        # Start the rest
        for name, filename, cmd in scripts[1:]:
            if os.path.exists(filename):
                print(f"[*] Starting {name}...")
                # We use CREATE_NEW_CONSOLE to avoid stdout overlap in the same terminal, 
                # or just run them and let output mix?
                # Actually, mixing output works for testing, but can be messy.
                # Let's keep them in the same console for this script, but they might interleave.
                p = subprocess.Popen(cmd)
                processes.append((name, p))
                time.sleep(1)
            else:
                print(f"[ERROR] Could not find {filename}")

        print("\n" + "=" * 60)
        print("All shields are active. Press Ctrl+C to stop all components.")
        print("=" * 60 + "\n")

        # Keep main thread alive
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n[!] Ctrl+C received. Initiating graceful shutdown...")
    finally:
        for name, p in processes:
            print(f"[*] Stopping {name} (PID: {p.pid})...")
            p.terminate()
            try:
                p.wait(timeout=3)
            except subprocess.TimeoutExpired:
                print(f"[!] Force killing {name}...")
                p.kill()
        
        print("[*] All Aegis systems offline.")

if __name__ == "__main__":
    main()
