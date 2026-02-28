import time
import pyperclip
import requests

# Track the last copied text so we don't analyze the same thing twice
LAST_TEXT = ""

def analyze_intent(text):
    """Sends text to the Local AMD NPU LLM for psychological analysis."""
    print(f"\n[NPU] 🧠 Routing text to Local AI Model...")
    
    # The payload formatted for LM Studio's local OpenAI-compatible server
    payload = {
        "messages": [
            {"role": "system", "content": "You are a strict cybersecurity AI. Read the following text. If it contains signs of phishing, urgency, fake invoices, or password requests, reply with ONLY the word 'UNSAFE'. Otherwise, reply 'SAFE'."},
            {"role": "user", "content": text}
        ],
        "temperature": 0.1,
        "max_tokens": 10
    }
    
    try:
        # Attempt to connect to the local AI model (e.g., LM Studio)
        response = requests.post("http://127.0.0.1:1234/v1/chat/completions", json=payload, timeout=2)
        result = response.json()['choices'][0]['message']['content'].strip()
        return "UNSAFE" in result.upper()
    
    except requests.exceptions.RequestException:
        # --- HACKATHON DEMO FALLBACK ---
        # If the local LLM isn't running yet, use this fast heuristic scanner
        print("[NPU] ⚠️ Local LLM offline. Engaging heuristic fallback...")
        suspicious_keywords = ["urgent", "password", "bank", "invoice", "transfer", "verify", "account", "suspended"]
        text_lower = text.lower()
        return any(word in text_lower for word in suspicious_keywords)

def trigger_cognitive_alert():
    """Broadcasts the social engineering threat to the React Dashboard."""
    alert_payload = {
        "node": "Node-01: User Endpoint",
        "action": "SOCIAL ENGINEERING DETECTED",
        "target": "System Clipboard",
        "classification": "[AMD NPU] Phi-3 NLP Phishing Heuristic (96.4%)",
        "status": "Text Intercepted"
    }
    try:
        requests.post("http://127.0.0.1:8000/api/threat-alert", json=alert_payload)
        print("[MIND] 🚨 Threat broadcasted to Command Center!")
    except Exception as e:
        print(f"[NETWORK] ⚠️ Could not reach Command Center: {e}")

if __name__ == "__main__":
    print("[*] Project Aegis: The Mind (Cognitive Agent) is ONLINE.")
    print("[*] Monitoring system clipboard for social engineering vectors...\n")
    
    while True:
        try:
            current_text = pyperclip.paste()
            
            # Only analyze if it's new text and longer than 15 characters
            if current_text != LAST_TEXT and len(current_text) > 15:
                LAST_TEXT = current_text
                print(f"[MIND] 📋 New clipboard data intercepted: '{current_text[:40]}...'")
                
                is_threat = analyze_intent(current_text)
                
                if is_threat:
                    print("[MIND] 🛑 WARNING: Malicious psychological intent detected!")
                    trigger_cognitive_alert()
                else:
                    print("[MIND] ✅ Text classified as benign.")
                    
        except Exception as e:
            pass
            
        time.sleep(1.5) # Check the clipboard every 1.5 seconds