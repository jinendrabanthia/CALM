import os
import time
import asyncio
import numpy as np
import pyaudio
import speech_recognition as sr
from pygame import mixer
import sys
import edge_tts
from transformers import pipeline
import warnings
import torch
import ollama
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox, Toplevel
from PIL import Image, ImageTk, ImageDraw 

# --- 0. CONFIGURATION & GLOBALS ---
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
warnings.filterwarnings("ignore")

# Voice & Model Settings
VOICE = "en-US-EricNeural"
LOCAL_MODEL = "qwen2.5:3b"

# Sensitivity
VOLUME_THRESHOLD = 0.03
CONFIDENCE_THRESHOLD = 0.50

# Labels
CANDIDATE_LABELS = [
    "Sound of a person screaming in pain", "Sound of a person crying in agony",
    "Sound of a person moaning in injury", "Sound of a person gasping for air",
    "Sound of loud people talking", "Sound of laughter", "Sound of clapping",
    "Sound of normal speech", "Sound of background noise", "Sound of silence"
]

DISTRESS_LABELS = [
    "Sound of a person screaming in pain", "Sound of a person crying in agony",
    "Sound of a person moaning in injury", "Sound of a person gasping for air"
]

RATE = 48000
CHUNK = 48000

# Initialize Audio
mixer.init()
r = sr.Recognizer()

# Load Model Global
classifier = None

# --- UPDATED: EMAIL CONFIG WITH MULTIPLE RECEIVERS ---
EMAIL_CONFIG = {
    "enabled": True,
    "sender": "hackathonteamecho@gmail.com",
    "password": "zyptkbuhkbrlsgts",
    "receivers": [
        "saishovan2@gmail.com",
        "simrandasisme@gmail.com",
        "bhumika.khandelwal2006@gmail.com",
        "rupeshmaharana5566@gmail.com",
        "marthahimesh2006@gmail.com"
    ],
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587
}

SOS_TIMEOUT = 65                    # seconds of silence → SOS
SEVERE_SCORE_THRESHOLD = 0.80       # Very high confidence
SEVERE_VOLUME = 0.85

SEVERE_LABELS = {
    "Sound of a person screaming in pain",
    "Sound of a person crying in agony",
    "Sound of a person moaning in injury",
    "Sound of a person gasping for air",
    "Sound of a person choking"
}

conversation_active = False
last_user_response_time = 0

# --- 1. HELPER FUNCTIONS ---
async def generate_voice(text):
    communicate = edge_tts.Communicate(text, VOICE)
    await communicate.save("echo_voice.mp3")

def speak(text, update_log_func):
    update_log_func(f"E.C.H.O.: {text}", "ai")
    try:
        asyncio.run(generate_voice(text))
        mixer.music.load("echo_voice.mp3")
        mixer.music.play()
        while mixer.music.get_busy():
            time.sleep(0.1)
        mixer.music.unload()
        if os.path.exists("echo_voice.mp3"):
            try: os.remove("echo_voice.mp3")
            except: pass
    except Exception as e:
        update_log_func(f"Voice Error: {e}", "error")

def listen_to_existing_stream(stream, update_log_func, seconds=5):
    update_log_func(f"[LISTENING] Speak clearly for {seconds}s...", "system")
    frames = []
    for _ in range(seconds):
        try:
            data = stream.read(CHUNK, exception_on_overflow=False)
            frames.append(data)
        except Exception:
            break
    
    raw_data = b''.join(frames)
    audio_float = np.frombuffer(raw_data, dtype=np.float32)
    audio_float = audio_float * 1.5
    audio_int16 = (audio_float * 32767).astype(np.int16)
    return sr.AudioData(audio_int16.tobytes(), RATE, 2)

# --- NEW: SOS Email Function (UPDATED FOR MULTIPLE RECEIVERS) ---
def send_sos_email(label, score, is_timeout=False):
    if not EMAIL_CONFIG["enabled"]:
        return False
    try:
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        import smtplib

        msg = MIMEMultipart()
        msg['From'] = EMAIL_CONFIG["sender"]
        msg['To'] = ", ".join(EMAIL_CONFIG["receivers"])  # Comma-separated for multiple
        urgency = "CRITICAL - NO RESPONSE" if is_timeout else "SEVERE DISTRESS"
        msg['Subject'] = f"🚨 E.C.H.O. SOS: {urgency}"

        body = f"""🆘 E.C.H.O. EMERGENCY ALERT 🆘

Type: {label}
Confidence: {score:.1%}
Time: {time.strftime('%d %b %Y, %I:%M:%S %p')}

{'→ User did NOT respond in {SOS_TIMEOUT} seconds!' if is_timeout else '→ High severity distress detected'}

Please check on the person immediately.
Location: {os.getenv('LOCATION', 'Unknown')}
"""
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(EMAIL_CONFIG["smtp_server"], EMAIL_CONFIG["smtp_port"])
        server.starttls()
        server.login(EMAIL_CONFIG["sender"], EMAIL_CONFIG["password"])
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        app.log(f"[SOS] Email failed: {e}", "alert")
        return False

# --- 2. THE UI CLASS ---
class EchoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("E.C.H.O. | Emergency Care Health Observer")
        self.root.geometry("800x600")
        self.root.configure(bg="#050510")

        # Application State
        self.running = False
        self.mic_enabled = True
        self.thread = None
        self.stop_event = threading.Event()
        
        # Log Management
        self.log_history = [] # Stores logs in memory
        self.log_window = None
        self.log_text_widget = None

        # --- GUI LAYOUT ---
        self.setup_background()
        self.setup_ui_elements()
        
        # Load Model in background
        self.log("Initializing Neural Pathways...", "system")
        threading.Thread(target=self.load_model, daemon=True).start()

    def setup_background(self):
        self.canvas = tk.Canvas(self.root, bg="#050510", highlightthickness=0)
        self.canvas.place(relwidth=1, relheight=1)
        
        try:
            if os.path.exists("background.png"):
                img = Image.open("background.png")
            elif os.path.exists("background.jpg"):
                img = Image.open("background.jpg")
            else:
                raise FileNotFoundError
            img = img.resize((800, 600), Image.Resampling.LANCZOS)
            self.bg_img = ImageTk.PhotoImage(img)
            self.canvas.create_image(0, 0, image=self.bg_img, anchor="nw")
            self.canvas.create_rectangle(0, 0, 800, 600, fill="#000000", stipple="gray50")
        except:
            self.draw_grid()

    def draw_grid(self):
        w, h = 800, 600
        step = 50
        for x in range(0, w, step):
            color = "#0f1f3f" if x % 100 != 0 else "#1a3a6a"
            self.canvas.create_line(x, 0, x, h, fill=color)
        for y in range(0, h, step):
            color = "#0f1f3f" if y % 100 != 0 else "#1a3a6a"
            self.canvas.create_line(0, y, w, y, fill=color)
        
        self.canvas.create_text(400, 100, text="E.C.H.O. SYSTEM", fill="#102030", font=("Arial", 60, "bold"))

    def setup_ui_elements(self):
        # Header
        header_frame = tk.Frame(self.root, bg="#000000", bd=2, relief="ridge")
        header_frame.pack(side="top", fill="x", padx=20, pady=20)
        tk.Label(header_frame, text="E.C.H.O. INTERFACE", fg="#00ffcc", bg="#000000", font=("Consolas", 18, "bold")).pack(pady=10)

        # --- NEW MAIN STATUS DISPLAY (Replaces the text box) ---
        self.status_frame = tk.Frame(self.root, bg="#000000", bd=0)
        self.status_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        self.lbl_big_status = tk.Label(self.status_frame, text="INITIALIZING...", 
                                       fg="#555555", bg="#000000", font=("Arial", 36, "bold"))
        self.lbl_big_status.pack()
        
        self.lbl_sub_status = tk.Label(self.status_frame, text="Please wait for neural loading", 
                                       fg="#888888", bg="#000000", font=("Consolas", 14))
        self.lbl_sub_status.pack(pady=10)

        # Controls Frame
        btn_frame = tk.Frame(self.root, bg="#050510")
        btn_frame.pack(side="bottom", fill="x", pady=30, padx=20)

        # Run/Stop Button
        self.btn_run = tk.Button(btn_frame, text="ACTIVATE SYSTEM", command=self.toggle_run, 
                                 bg="#004400", fg="white", font=("Arial", 12, "bold"), width=18, height=2)
        self.btn_run.pack(side="left", padx=10)

        # Mic Toggle
        self.btn_mic = tk.Button(btn_frame, text="MIC: ON", command=self.toggle_mic, 
                                 bg="#004444", fg="white", font=("Arial", 12, "bold"), width=12, height=2)
        self.btn_mic.pack(side="left", padx=10)

        # SHOW LOGS BUTTON
        self.btn_logs = tk.Button(btn_frame, text="SHOW LOGS", command=self.open_log_window, 
                                  bg="#333333", fg="white", font=("Arial", 10, "bold"), width=12, height=2)
        self.btn_logs.pack(side="right", padx=10)

    # --- LOGGING SYSTEM ---
    def open_log_window(self):
        if self.log_window is not None and self.log_window.winfo_exists():
            self.log_window.lift()
            return

        self.log_window = Toplevel(self.root)
        self.log_window.title("E.C.H.O. Analysis Logs")
        self.log_window.geometry("600x400")
        self.log_window.configure(bg="black")
        
        self.log_text_widget = scrolledtext.ScrolledText(self.log_window, bg="#0a0a0a", fg="#00ff00", font=("Consolas", 10))
        self.log_text_widget.pack(fill="both", expand=True)
        
        # Define colors
        self.log_text_widget.tag_config("system", foreground="#00aaaa")
        self.log_text_widget.tag_config("alert", foreground="#ff3333")
        self.log_text_widget.tag_config("ai", foreground="#ffffff")
        self.log_text_widget.tag_config("user", foreground="#aaaaaa")

        # Populate with history
        for text, tag in self.log_history:
            self.log_text_widget.insert(tk.END, f"{text}\n", tag)
        self.log_text_widget.see(tk.END)

    def log(self, text, tag="system"):
        # 1. Save to memory
        self.log_history.append((text, tag))
        # 2. Update Window if open
        if self.log_window is not None and self.log_window.winfo_exists():
            try:
                self.log_text_widget.insert(tk.END, f"{text}\n", tag)
                self.log_text_widget.see(tk.END)
            except: pass

    def set_status(self, main_text, sub_text, color="#00ff00"):
        self.root.after(0, lambda: self._update_status_gui(main_text, sub_text, color))

    def _update_status_gui(self, main_text, sub_text, color):
        self.lbl_big_status.config(text=main_text, fg=color)
        self.lbl_sub_status.config(text=sub_text)

    def load_model(self):
        global classifier
        try:
            classifier = pipeline(
                task="zero-shot-audio-classification",
                model="laion/clap-htsat-unfused",
                device=-1
            )
            self.log("[SYSTEM] Pain Detection Model Loaded.", "system")
            self.set_status("STANDBY", "System Ready. Press Activate.", "#00ccff")
        except Exception as e:
            self.log(f"[ERROR] Model Load Failed: {e}", "alert")
            self.set_status("ERROR", "Model Failed to Load", "#ff0000")

    def toggle_mic(self):
        self.mic_enabled = not self.mic_enabled
        if self.mic_enabled:
            self.btn_mic.config(text="MIC: ON", bg="#004444", fg="white")
            self.log("[PRIVACY] Microphone Enabled", "system")
        else:
            self.btn_mic.config(text="MIC: OFF", bg="#440000", fg="#ffcccc")
            self.log("[PRIVACY] Microphone Muted", "system")

    def toggle_run(self):
        if not self.running:
            if classifier is None:
                messagebox.showwarning("Loading", "Model is still loading...")
                return
            self.running = True
            self.stop_event.clear()
            self.btn_run.config(text="DEACTIVATE", bg="#aa0000")
            self.set_status("MONITORING", "Listening for distress signals...", "#00ff00")
            self.thread = threading.Thread(target=self.run_logic, daemon=True)
            self.thread.start()
        else:
            self.running = False
            self.stop_event.set()
            self.btn_run.config(text="ACTIVATE SYSTEM", bg="#004400")
            self.set_status("STANDBY", "System Halted", "#555555")
            self.log("[SYSTEM] Deactivation requested...", "system")

    # --- 3. MAIN LOGIC LOOP (Threaded) ---
    def run_logic(self):
        p = pyaudio.PyAudio()
        try:
            stream = p.open(format=pyaudio.paFloat32, channels=1, rate=RATE,
                            input=True, frames_per_buffer=CHUNK)
        except Exception as e:
            self.log(f"Mic Error: {e}", "alert")
            return

        speak("E.C.H.O. online.", self.log)
        
        while self.running and not self.stop_event.is_set():
            if not self.mic_enabled:
                time.sleep(1)
                continue

            try:
                data = stream.read(CHUNK, exception_on_overflow=False)
                samples = np.frombuffer(data, dtype=np.float32)
                vol = np.abs(samples).max()

                if vol > VOLUME_THRESHOLD:
                    self.set_status("ANALYZING...", "High Volume Detected", "#ffff00")
                    self.log(f"[ANALYZING] High Volume: {vol:.2f}", "system")
                    
                    result = classifier(samples, candidate_labels=CANDIDATE_LABELS)
                    top_label = result[0]['label']
                    top_score = result[0]['score']

                    self.log(f" > Heard: {top_label} ({int(top_score*100)}%)", "system")

                    if top_label in DISTRESS_LABELS and top_score > CONFIDENCE_THRESHOLD or vol > 0.6:
                        is_severe = (top_label in SEVERE_LABELS and top_score >= SEVERE_SCORE_THRESHOLD) or vol > SEVERE_VOLUME

                        alert_msg = f"[!!!] {'SEVERE' if is_severe else 'POSSIBLE'} INJURY: {top_label} ({top_score:.1%})"
                        self.log(alert_msg, "alert")
                        self.set_status("DISTRESS DETECTED", f"{top_label.split()[-1].upper()}", "#ff0000")

                        # === SOS FOR SEVERE CASE ===
                        if is_severe:
                            self.log("🚨 SEVERE DISTRESS → IMMEDIATE SOS SENT", "alert")
                            send_sos_email(top_label, top_score)

                        speak(f"I detected {top_label.split(' ')[-1]}. Are you injured?", self.log)
                        
                        global conversation_active, last_user_response_time
                        conversation_active = True
                        last_user_response_time = time.time()

                        # Start timeout watchdog
                        def sos_watchdog():
                            global conversation_active
                            time.sleep(SOS_TIMEOUT)
                            if conversation_active:
                                self.log("🚨 NO RESPONSE FOR 65s → SOS TRIGGERED", "alert")
                                send_sos_email(top_label, top_score, is_timeout=True)
                                speak("Sending emergency alert to contacts.", self.log)
                                conversation_active = False

                        threading.Thread(target=sos_watchdog, daemon=True).start()

                        # --- Conversation Loop (slightly modified) ---
                        chat_history = [
                            {'role': 'system', 'content': "You are E.C.H.O. emergency AI. Keep responses short."},
                            {'role': 'user', 'content': f"Context: {top_label} detected."}
                        ]

                        in_conversation = True
                        while in_conversation and self.running and self.mic_enabled:
                            try:
                                self.set_status("LISTENING", "Waiting for your voice...", "#00ccff")
                                user_audio = listen_to_existing_stream(stream, self.log, seconds=6)
                                text = r.recognize_google(user_audio)

                                if not text.strip():
                                    continue

                                self.log(f"User: {text}", "user")
                                last_user_response_time = time.time()   # Reset timer

                                if any(phrase in text.lower() for phrase in ["ok", "good", "fine", "satisfied", "i am good", "no injury", "care complete", "stop", "deactivate", "enough"]):
                                    speak("Understood. Resuming monitoring.", self.log)
                                    conversation_active = False
                                    in_conversation = False
                                    break

                                self.set_status("THINKING", "Processing response...", "#ff00ff")
                                chat_history.append({'role': 'user', 'content': text})
                                response = ollama.chat(model=LOCAL_MODEL, messages=chat_history)
                                ai_reply = response['message']['content']
                                speak(ai_reply, self.log)
                                chat_history.append({'role': 'assistant', 'content': ai_reply})

                            except sr.UnknownValueError:
                                continue
                            except sr.RequestError:
                                self.log("[ERROR] Internet/API Connection lost.", "alert")
                            except Exception as e:
                                self.log(f"STT Error: {e}", "error")

                        conversation_active = False   # Safety
                        self.set_status("MONITORING", "Listening for distress signals...", "#00ff00")
                        stream.read(CHUNK, exception_on_overflow=False)

                    else:
                        # Return to green if it was just noise
                        self.set_status("MONITORING", "Listening for distress signals...", "#00ff00")

            except Exception as e:
                self.log(f"Error in loop: {e}", "alert")
        
        stream.stop_stream()
        stream.close()
        p.terminate()

if __name__ == "__main__":
    try:
        import pyi_splash
        pyi_splash.close()
    except:
        pass
        
    root = tk.Tk()
    app = EchoApp(root)
    root.mainloop()