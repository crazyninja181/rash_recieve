import requests
import time
import pyttsx3
import sounddevice as sd
from scipy.io.wavfile import write

# -------- CONFIG --------
SERVER_BASE = "https://test1-1-rrdb.onrender.com/"  # replace with your actual Render URL
GET_URL = f"{SERVER_BASE}/get"
UPLOAD_URL = f"{SERVER_BASE}/upload"

engine = pyttsx3.init()
engine.setProperty('rate', 160)

# -------- RECEIVE TEXT AND SPEAK --------
def receive_and_speak():
    """Check the server for new text messages and speak them."""
    last_message = ""
    print("🔊 Checking for messages from server (Ctrl+C to stop)...")
    try:
        while True:
            res = requests.get(GET_URL, timeout=5)
            data = res.json()
            message = data.get("message", "")
            if message and message != last_message:
                print(f"📥 New message: {message}")
                engine.say(message)
                engine.runAndWait()
                last_message = message
            time.sleep(3)
    except KeyboardInterrupt:
        print("\n⏹️  Stopped listening.\n")

# -------- RECORD AND SEND VOICE --------
def record_and_send_voice():
    """Record a 5-second voice clip and upload it to Flask."""
    fs = 44100
    duration = 5  # seconds
    print("🎙️ Recording... speak now!")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()
    filename = "voice_message.wav"
    write(filename, fs, recording)
    print("✅ Recording complete, saved as", filename)

    try:
        with open(filename, 'rb') as f:
            files = {'file': f}
            r = requests.post(UPLOAD_URL, files=files)
        if r.status_code == 200:
            print("✅ Voice message uploaded successfully!")
        else:
            print("❌ Upload failed:", r.text)
    except Exception as e:
        print("⚠️  Upload error:", e)

# -------- MAIN MENU --------
def main():
    while True:
        print("\n=== Raspberry Pi Message System ===")
        print("1️⃣  Listen and speak text messages")
        print("2️⃣  Record and send a voice message")
        print("3️⃣  Exit")
        choice = input("Enter choice: ")

        if choice == "1":
            receive_and_speak()
        elif choice == "2":
            record_and_send_voice()
        elif choice == "3":
            print("👋 Exiting program.")
            break
        else:
            print("❌ Invalid option, try again.")

if __name__ == "__main__":
    main()
