# Project AEGIS
**The Zero-Latency, Autonomous Cyber-Immune System for the Edge.**

AEGIS (Advanced Edge Guard & Intelligence System) is a hyper-local, zero-latency cybersecurity orchestration designed to democratize enterprise-grade, nation-state level protection. By shifting threat detection from reactive, high-latency cloud servers to autonomous, AI-driven local edge nodes powered by **AMD Ryzen AI**, AEGIS provides an impenetrable defense for edge devices, Industrial IoT, remote defense nodes, and environments with intermittent or zero cloud connectivity.

## 🛡️ The 5 Shields of AEGIS

AEGIS operates through a concurrent orchestration of five independent defense layers, launched via a single command engine:

1.  **AMD AI EDR Agent (`edr_agent.py`)**
    The core intelligence. Continuously processes raw system telemetry (CPU cycles, memory allocations, handles, I/O rates) through a locally trained ONNX Autoencoder Neural Network. It identifies Zero-Day behavioral anomalies by detecting Mean Squared Error (MSE) breaches and instantly terminating malicious processes.
2.  **Dynamic Network Edge Shield (`net_shield.py`)**
    Operating at the socket level, this shield detects volumetric DDoS patterns and dynamically injects adaptive Windows Defender rules while throttling SYN retransmissions during active network sieges.
3.  **Auto-Healing File System Honeypot (`honeypot.py`)**
    Deploys invisible, high-value decoy files across critical directories. Upon ransomware attempting encryption, AEGIS intercepts the OS interrupt, immediately isolates the process, and auto-heals corrupted files from a secure shadow cache.
4.  **Cognitive Memory Guard (`mind.py`)**
    A localized Natural Language Processing (NLP) filter over system volatile memory (like clipboards) that detects and redacts sensitive exfiltration attempts (e.g., API Keys, Passwords).
5.  **React Command Center (`delhibreathe-dashboard`)**
    A high-performance Vite/React Single-Page Application (SPA) streaming asynchronous WebSocket telemetry to render live Node Threat Maps and NPU consumption without creating system overhead.

## 🚀 The AMD Advantage

AEGIS is deeply optimized for the **AMD Ryzen AI Stack**.
*   **Zero Thermal Compromise:** By utilizing the **AMD XDNA NPU** via local ONNX Runtime Execution Providers, AEGIS offloads 100% of the behavioral AI inference matrix.
*   **Always-On Performance:** The primary CPU remains entirely unencumbered and dedicated to the user's workload, maintaining an "Always-On" security net that doesn't sap battery life or performance.
*   **Data Center GPU Training:** The Process Behavior Autoencoder model is trained rapidly by leveraging **AMD ROCm/CUDA** capabilities (`train_behavioral_model.py`) before deployment to the edge.

## ⚙️ Technologies Used

*   **Frontend:** React 19, Vite, Tailwind CSS, Recharts (NPU telemetry), React Router DOM.
*   **Backend Middleware:** Python (FastAPI, Uvicorn, WebSockets), SQLite3.
*   **Machine Learning Integration:** AMD Ryzen AI, ONNX Runtime, PyTorch (for model training).
*   **Low-Level OS Integration:** `psutil`, native Windows `netsh`/firewall integration.

## 🛠️ Installation & Execution

### Prerequisites
*   Python 3.10+
*   Node.js & npm (for the React Dashboard)
*   *(Optional but Recommended)*: AMD System with Ryzen AI NPU for hardware inference optimization.

### 1. Backend Setup

```bash
# Clone the repository
git clone <your-repository-url>
cd Project_Aegis

# Create a virtual environment
python -m venv venv
# Activate the environment (Windows)
.\venv\Scripts\activate

# Install dependencies (Assuming requirements.txt exists)
pip install fastapi uvicorn websockets psutil onnxruntime numpy torch
```

*Note: If `torch` or `onnxruntime` fail, you may need to install platform-specific versions targeting your AMD hardware.*

### 2. Frontend Setup

```bash
cd delhibreathe-dashboard
npm install
```

### 3. Launching AEGIS

AEGIS uses a master orchestrator script to bootstrap all 5 shields simultaneously.

```bash
# From the root project directory
python start_aegis.py
```
This will start the FastAPI backend server on port `8000`, the React dashboard on port `5173`, and instantiate the EDR, network, honeypot, and cognitive defenses in the background.

## 📡 Live Telemetry Dashboard
Once AEGIS is running, open your browser and navigate to:
**`http://localhost:5173`**

Login required for standard access. Note that the system leverages strict rate-limiting endpoints to defend against volumetric HTTP floods out of the box.

## 🤝 Contributing
Contributions, issues, and feature requests are welcome. Feel free to check [issues page].

## 📝 License
This project is licensed under the MIT License - see the `LICENSE` file for details.
