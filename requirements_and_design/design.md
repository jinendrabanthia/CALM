# 📐 System Design & Architecture

## 🏛️ High-Level Overview

E.C.H.O. (Emergency Care Health Observer) utilizes an **Event-Driven Architecture** combined with **Edge AI**. Unlike cloud-based assistants (Alexa/Siri), E.C.H.O. processes all data locally on the device, ensuring privacy and operation without internet access.

The system follows a "Listen-Analyze-React" pipeline designed to minimize latency and computational load.

---

## 🧩 Architecture Diagram

```mermaid
graph TD
    A[Microphone Input] -->|Raw Audio Stream| B(Volume Gate)
    B -- Quiet < 0.15 --> C[Discard Data]
    B -- Loud > 0.15 --> D{CLAP Model Analysis}
    
    D -->|Safe Sound| E[Resume Monitoring]
    D -->|Distress Detected| F[Trigger Protocol]
    
    F --> G[Verbal Inquiry]
    G --> H[Speech-to-Text STT]
    H --> I[Local LLM Brain]
    I -->|Medical Guidance| J[Text-to-Speech TTS]
    J --> K[Speaker Output]
    
    style B fill:#f9f,stroke:#333,stroke-width:2px
    style D fill:#bbf,stroke:#333,stroke-width:2px
    style I fill:#bfb,stroke:#333,stroke-width:2px

🧱 Core Components
1. The Listener (Audio Ingestion)
Library: PyAudio

Spec: 48kHz Sample Rate, Float32 bit-depth.

Logic: The system maintains a rolling buffer of the last 5 seconds of audio. This ensures that when a sound triggers the system, we capture the start of the scream/crash, not just the aftermath.

2. The Gatekeeper (Trigger Logic)
To save battery and CPU, the heavy AI models do not run constantly.

Volume Threshold: A lightweight Numpy operation checks if the audio amplitude exceeds 0.15 (tunable).

Benefit: Reduces CPU usage by ~90% when the room is silent.

3. The Analyzer (CLAP Model)
Model: laion/clap-htsat-unfused

Function: Zero-Shot Audio Classification.

Why CLAP? Unlike standard classifiers trained on fixed categories (e.g., "dog", "car"), CLAP connects audio to text descriptions. This allows us to detect specific nuances like "Sound of a person gasping for air" without training a custom dataset.

4. The Brain (Local LLM)
Engine: Ollama running qwen2.5:3b.

Role: Contextual understanding. It doesn't just recite a script; it adapts.

Input: "I think I broke my leg."

Response: "Do not move. I am activating the emergency alert. Keep your leg still."

Privacy: Since it runs on localhost, no audio or text logs leave the machine.

5. The Interface (GUI)
Framework: Tkinter (Custom Dark Theme).

Threading: The UI runs on the MainThread, while the Listen/Analyze loop runs on a DaemonThread. This prevents the "Not Responding" freeze during heavy AI processing.

🔄 Data Flow Pipeline
Standby Phase:

System listens in 1024-frame chunks.

GUI shows "MONITORING".

CPU usage is < 5%.

Detection Phase:

Loud noise detected -> Audio chunk sent to CLAP.

CLAP returns probability scores for candidates (e.g., "Scream": 0.85, "Laughter": 0.02).

If Scream > CONFIDENCE_THRESHOLD, enter Distress Mode.

Interaction Phase:

System speaks: "Are you injured?"

Microphone opens for user response.

User Speech -> Google STT -> Text -> Ollama -> Response.

🛡️ Security & Privacy
Zero Cloud Dependency: All processing happens on 127.0.0.1.

Ephemeral Storage: Audio buffers are overwritten every 5 seconds. No recordings are saved to the hard drive unless specifically debugged.

Mic Kill Switch: Hardware-level software lock available in the UI ("Privacy Mode").