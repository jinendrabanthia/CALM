# 🛠️ System Requirements & Dependencies

To run **E.C.H.O.** locally, your system must meet the following specifications to handle audio processing and the Local LLM (Large Language Model) simultaneously.

---

## 💻 Hardware Requirements

| Component | Minimum | Recommended |
| :--- | :--- | :--- |
| **RAM** | 8 GB | 16 GB+ |
| **CPU** | Quad-Core (Intel i5/Ryzen 5) | Hexa-Core or better |
| **GPU** | Integrated Graphics | NVIDIA RTX 3060+ (For faster response) |
| **Disk Space** | 5 GB Free | 10 GB Free (For AI Models) |
| **Peripherals** | Built-in Microphone | High-quality USB Microphone |

> **Note on Performance:** The application is designed to run on CPU if no GPU is detected, but response times for the Conversational AI (Qwen 2.5) will be slower (5-10 seconds latency vs. nearly instant on GPU).

---

## 💿 Software Prerequisites

### 1. Python
- **Version:** Python 3.10 or 3.11 (Recommended for PyAudio compatibility)
- [Download Python](https://www.python.org/downloads/)
- pip install -r requirements.txt

### 2. Ollama (Crucial)
E.C.H.O. relies on **Ollama** to run the conversational AI offline. You **must** install this separately; it cannot be installed via pip.
1. Download Ollama from [ollama.com](https://ollama.com).
2. Install it.
3. Open your terminal/command prompt and run:
   ```bash
   ollama pull qwen2.5:3b