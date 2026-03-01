import sqlite3
import psutil
import asyncio
import random
import hashlib
import secrets
import subprocess
import sys
from datetime import datetime
from fastapi import FastAPI, WebSocket, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Dict, Tuple
from fastapi.responses import JSONResponse
import time

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────────────────────────────────────
# ADMIN AUTH CONFIG
# Password: aegis2025  →  SHA-256 hash
ADMIN_PASSWORD_HASH = hashlib.sha256(b"aegis2025").hexdigest()

# In-memory active session tokens (token -> True)
active_tokens: set = set()

# ─────────────────────────────────────────────────────────────────────────────
# MAINTENANCE MODE STATE
maintenance_mode: bool = False

# ─────────────────────────────────────────────────────────────────────────────
# RATE LIMITING & DDOS DEFENSE
# ─────────────────────────────────────────────────────────────────────────────

RATE_LIMIT_WINDOW = 60  # seconds
MAX_REQS_PER_IP = 100   # Max requests per IP within the window
MAX_GLOBAL_REQS = 500   # Max global requests across all IPs within the window

# In-memory tracking
# ip_tracker: { ip_address: (timestamp_of_first_req_in_window, request_count) }
ip_tracker: Dict[str, Tuple[float, int]] = {}
global_req_tracker: Tuple[float, int] = (time.time(), 0)

rate_limit_alerted_ips: set = set()
global_alerted: bool = False

async def save_and_broadcast_alert(data: dict):
    conn = sqlite3.connect("aegis_logs.db")
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO alerts (node, action, target, classification, status, timestamp, analysis)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (data['node'], data['action'], data['target'], data['classification'], data['status'], data['timestamp'], data['analysis']))
        conn.commit()
        data['id'] = cursor.lastrowid
    except Exception as e:
        print(f"[DB ERROR] Failed to save alert: {e}")
    conn.close()
    await broadcast_to_dashboards(data)

async def check_rate_limit(request: Request) -> bool:
    """Checks if the request should be allowed based on IP and Global limits."""
    global global_req_tracker, global_alerted
    
    now = time.time()
    client_ip = request.client.host if request.client else "unknown"
    
    # 1. Global Throttling Check
    global_start_time, global_count = global_req_tracker
    if now - global_start_time > RATE_LIMIT_WINDOW:
        # Reset global window
        global_req_tracker = (now, 1)
        global_alerted = False
    else:
        if global_count >= MAX_GLOBAL_REQS:
            # High Alert: Global limit reached. 
            if not request.url.path.startswith("/api/admin/"):
                if not global_alerted:
                    global_alerted = True
                    alert_data = {
                        "node": "Node-01: Connaught Place",
                        "action": "API GLOBAL THROTTLE",
                        "target": "All Unauth Endpoints",
                        "classification": "[API SHIELD] Volumetric HTTP Flood (99%)",
                        "status": "503 Triggered",
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "analysis": f"DETECTED: Massive surge in HTTP requests exceeding structural capacity.\nANALYSIS: Global request rate breached {MAX_GLOBAL_REQS} req/{RATE_LIMIT_WINDOW}s window.\nRESPONSE: API placed in High Alert Mode. All unauthenticated traffic dropped to preserve backend stability."
                    }
                    asyncio.create_task(save_and_broadcast_alert(alert_data))
                    show_onscreen_alert(alert_data["classification"], f"Target: All Unauth Endpoints\nStatus: 503 Triggered")
                
                print(f"[SHIELD] 🔴 Global DDoS Threshold Breached! Dropping request from {client_ip}.")
                raise HTTPException(status_code=503, detail="Service Unavailable: High Alert Mode. System under heavy load.")
        global_req_tracker = (global_start_time, global_count + 1)

    # 2. Per-IP Rate Limiting
    if client_ip in ip_tracker:
        ip_start_time, ip_count = ip_tracker[client_ip]
        if now - ip_start_time > RATE_LIMIT_WINDOW:
            # Reset IP window
            ip_tracker[client_ip] = (now, 1)
            if client_ip in rate_limit_alerted_ips:
                rate_limit_alerted_ips.remove(client_ip)
        else:
            if ip_count >= MAX_REQS_PER_IP:
                if client_ip not in rate_limit_alerted_ips:
                    rate_limit_alerted_ips.add(client_ip)
                    alert_data = {
                        "node": "Node-01: Connaught Place",
                        "action": "API RATE LIMIT",
                        "target": f"IP: {client_ip}",
                        "classification": "[API SHIELD] Single-Source HTTP Flood (95%)",
                        "status": "Traffic Dropped",
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "analysis": f"DETECTED: Unusually high frequency of requests from {client_ip}.\nANALYSIS: Client exceeded {MAX_REQS_PER_IP} req/{RATE_LIMIT_WINDOW}s window.\nRESPONSE: HTTP 429 Too Many Requests enforcement active. IP traffic throttled."
                    }
                    asyncio.create_task(save_and_broadcast_alert(alert_data))
                    show_onscreen_alert(alert_data["classification"], f"Target: IP: {client_ip}\nStatus: Traffic Dropped")
                    
                print(f"[SHIELD] 🔴 IP Rate Limit Exceeded by {client_ip}.")
                raise HTTPException(status_code=429, detail="Too Many Requests from this IP.")
            ip_tracker[client_ip] = (ip_start_time, ip_count + 1)
    else:
        ip_tracker[client_ip] = (now, 1)
        
    return True

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    # Skip rate limiting for WebSockets as they keep a persistent connection
    if request.url.path.startswith("/ws/"):
        return await call_next(request)
        
    try:
        await check_rate_limit(request)
    except HTTPException as exc:
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
        
    response = await call_next(request)
    return response

# ─────────────────────────────────────────────────────────────────────────────
# WEBSOCKET CLIENTS
connected_dashboards: List[WebSocket] = []

# ─────────────────────────────────────────────────────────────────────────────
# DATABASE
def init_db():
    conn = sqlite3.connect("aegis_logs.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            node TEXT,
            action TEXT,
            target TEXT,
            classification TEXT,
            status TEXT,
            timestamp TEXT,
            analysis TEXT
        )
    ''')
    try:
        cursor.execute("ALTER TABLE alerts ADD COLUMN analysis TEXT")
    except sqlite3.OperationalError:
        pass  # Column already exists
    conn.commit()
    conn.close()

init_db()

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS

def show_onscreen_alert(title: str, message: str):
    try:
        # Avoid blocking API server, use Popen
        python_exe = sys.executable
        script_path = "show_alert.py"
        print(f"[*] Dispatching on-screen alert: {python_exe} {script_path} --title '{title}' --message '{message}'")
        # CREATE_NO_WINDOW = 0x08000000 (prevents cmd prompt flashes on Windows)
        subprocess.Popen([python_exe, script_path, "--title", title, "--message", message], creationflags=0x08000000)
    except Exception as e:
        print(f"[ERROR] Failed to show onscreen alert: {e}", file=sys.stderr)

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_token(token: str) -> bool:
    return token in active_tokens

security = HTTPBearer(auto_error=False)

async def require_auth(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not credentials or not verify_token(credentials.credentials):
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid or missing token")
    return credentials.credentials

def generate_forensic_report(action, target, node):
    """Generates a Generative-AI style incident report."""
    if "UNAUTHORIZED" in action:
        return f"DETECTED: Unsanctioned write operation on protected file '{target}'.\nANALYSIS: File modification attempted while system was in LOCKED state. No maintenance window was active.\nRESPONSE: File automatically reverted to last known-good snapshot. Incident logged for audit trail."
    elif "Renaming" in action or "Encryption" in action:
        return f"DETECTED: High-entropy write operations on sensitive file '{target}'. \nANALYSIS: Process exhibited 'WannaCry' signature (rapid file renaming). \nRESPONSE: Immediate process isolation and termination executed on {node}. Auto-healing heuristics engaged to revert filesystem changes."
    elif "SOCIAL" in action:
        return f"DETECTED: Suspicious clipboard content matching phishing heuristics. \nANALYSIS: Natural Language Processing (NLP) identified urgency keywords and financial coercion patterns. \nRESPONSE: User warned via active UI intervention. Clipboard write-access flagged for monitoring."
    elif "MALWARE" in action or "EDR" in action:
        return f"DETECTED: Malicious payload execution signature detected in active memory.\nANALYSIS: Behavior matched known shellcode/reverse-shell or highly obfuscated command line strings characteristic of advanced persistent threats.\nRESPONSE: Automated process termination via EDR heuristics. System remains secure."
    else:
        return f"DETECTED: Anomalous behavior on {node}. \nANALYSIS: Pattern deviates from standard baseline by 94%. \nRESPONSE: Event logged for manual review."

async def broadcast_to_dashboards(data: dict):
    """Send a JSON payload to all connected dashboard WebSocket clients."""
    dead_sockets = []
    for ws in connected_dashboards:
        try:
            await ws.send_json(data)
        except Exception:
            dead_sockets.append(ws)
    for ws in dead_sockets:
        connected_dashboards.remove(ws)

# ─────────────────────────────────────────────────────────────────────────────
# AUTH ENDPOINTS

@app.post("/api/admin/login")
async def admin_login(request: Request):
    body = await request.json()
    password = body.get("password", "")
    if hash_password(password) == ADMIN_PASSWORD_HASH:
        token = secrets.token_hex(32)
        active_tokens.add(token)
        return {"success": True, "token": token}
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/api/admin/logout")
async def admin_logout(token: str = Depends(require_auth)):
    active_tokens.discard(token)
    # If logging out, disable maintenance mode
    global maintenance_mode
    maintenance_mode = False
    await broadcast_to_dashboards({"type": "system_state", "maintenance_mode": False, "authenticated": False})
    return {"success": True}

@app.get("/api/admin/verify")
async def verify_session(token: str = Depends(require_auth)):
    return {"valid": True}

# ─────────────────────────────────────────────────────────────────────────────
# MAINTENANCE MODE & SYSTEM STATUS ENDPOINTS
# ─────────────────────────────────────────────────────────────────────────────

edge_shield_last_ping: float = 0
edge_shield_enabled: bool = True  # Admin toggle
edr_last_ping: float = 0

@app.post("/api/edge/ping")
async def edge_ping():
    global edge_shield_last_ping
    edge_shield_last_ping = time.time()
    return {"status": "ok"}

@app.post("/api/edr/ping")
async def edr_ping():
    global edr_last_ping
    edr_last_ping = time.time()
    return {"status": "ok"}

@app.post("/api/edge/toggle")
async def toggle_edge_shield(request: Request, token: str = Depends(require_auth)):
    global edge_shield_enabled
    body = await request.json()
    enabled = body.get("enabled", True)
    edge_shield_enabled = enabled
    # Broadcast state change to dashboards
    await broadcast_to_dashboards({"type": "system_state", "maintenance_mode": maintenance_mode, "edge_shield_enabled": enabled})
    return {"success": True, "edge_shield_enabled": edge_shield_enabled}

@app.get("/api/system/status")
async def get_system_status():
    global edge_shield_last_ping, maintenance_mode, edge_shield_enabled, edr_last_ping
    edge_shield_active = (time.time() - edge_shield_last_ping) < 10
    edr_active = (time.time() - edr_last_ping) < 10
    return {
        "status": "ok",
        "maintenance_mode": maintenance_mode,
        "edge_shield_active": edge_shield_active,
        "edge_shield_enabled": edge_shield_enabled,
        "edr_active": edr_active
    }

@app.get("/api/maintenance/status")
async def get_maintenance_status():
    return {"maintenance_mode": maintenance_mode}

@app.post("/api/maintenance/toggle")
async def toggle_maintenance(request: Request, token: str = Depends(require_auth)):
    global maintenance_mode
    body = await request.json()
    maintenance_mode = body.get("enabled", False)
    # Broadcast state change to all dashboards
    await broadcast_to_dashboards({
        "type": "system_state",
        "maintenance_mode": maintenance_mode,
        "authenticated": True
    })
    return {"success": True, "maintenance_mode": maintenance_mode}

# ─────────────────────────────────────────────────────────────────────────────
# WEBSOCKET ENDPOINTS

@app.websocket("/ws/dashboard")
async def dashboard_stream(websocket: WebSocket):
    await websocket.accept()
    connected_dashboards.append(websocket)
    # Send current system state immediately on connect
    try:
        await websocket.send_json({
            "type": "system_state",
            "maintenance_mode": maintenance_mode,
            "authenticated": False  # Client manages auth state locally
        })
    except Exception:
        pass
    try:
        while True:
            await websocket.receive_text()
    except Exception:
        if websocket in connected_dashboards:
            connected_dashboards.remove(websocket)

@app.websocket("/ws/telemetry")
async def telemetry_stream(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            cpu = psutil.cpu_percent(interval=None)
            ram = psutil.virtual_memory().percent
            npu = cpu * 1.5 + random.randint(5, 15) if cpu > 20 else random.randint(0, 5)
            if npu > 100: npu = 100
            await websocket.send_json({"cpu": cpu, "ram": ram, "npu": int(npu)})
            await asyncio.sleep(0.5)
    except Exception:
        pass

# ─────────────────────────────────────────────────────────────────────────────
# ALERT ENDPOINTS

@app.get("/api/alerts-history")
async def get_history():
    conn = sqlite3.connect("aegis_logs.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM alerts ORDER BY id DESC LIMIT 50")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.post("/api/threat-alert")
async def trigger_alert(request: Request):
    data = await request.json()
    data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data['analysis'] = generate_forensic_report(data['action'], data['target'], data['node'])

    show_onscreen_alert(data.get('classification', 'Threat Alert'), data.get('action', 'Unknown Action'))

    conn = sqlite3.connect("aegis_logs.db")
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO alerts (node, action, target, classification, status, timestamp, analysis)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (data['node'], data['action'], data['target'], data['classification'], data['status'], data['timestamp'], data['analysis']))
        conn.commit()
        data['id'] = cursor.lastrowid
    except Exception as e:
        print(f"[DB ERROR] Failed to save threat alert: {e}")
    conn.close()

    await broadcast_to_dashboards(data)
    return {"status": "Alert processed"}

@app.post("/api/unauthorized-alert")
async def unauthorized_alert(request: Request):
    """Called by honeypot when someone edits a file without maintenance mode."""
    data = await request.json()
    data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data['action'] = "UNAUTHORIZED ACCESS"
    data['classification'] = "[AEGIS SHIELD] Unauthorized File Modification (100%)"
    data['status'] = "File Reverted"
    data['analysis'] = generate_forensic_report("UNAUTHORIZED", data.get('target', 'Unknown'), data.get('node', 'Node-01'))

    title = data.get('classification', 'Unauthorized Access')
    message = f"Target: {data.get('target', 'Unknown')}\nStatus: {data['status']}"
    show_onscreen_alert(title, message)

    conn = sqlite3.connect("aegis_logs.db")
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO alerts (node, action, target, classification, status, timestamp, analysis)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (data['node'], data['action'], data['target'], data['classification'], data['status'], data['timestamp'], data['analysis']))
        conn.commit()
        data['id'] = cursor.lastrowid
    except Exception as e:
        print(f"[DB ERROR] Failed to save unauthorized alert: {e}")
    conn.close()

    await broadcast_to_dashboards(data)
    return {"status": "Unauthorized access logged"}