import requests
import time
import pyttsx3
import sounddevice as sd
from scipy.io.wavfile import write
import numpy as np
import speech_recognition as sr


SERVER_BASE = "https://test2-wlxk.onrender.com"
GET_URL = f"{SERVER_BASE}/get"
UPLOAD_URL = f"{SERVER_BASE}/upload"
CONFIRM_TEXT_URL = f"{SERVER_BASE}/confirm_text"

def speak(text):
    eng=pyttsx3.init()
    eng.setProperty('rate',190)
    voices=eng.getProperty('voices')
    eng.setProperty('voice',voices[1].id)
    eng.say(text)
    eng.runAndWait()
    eng.stop()

def listen():
    r=sr.Recognizer()
    with sr.Microphone() as source:
        speak("Listening..., speak now")
        r.pause_threshold=1
        audio=r.listen(source)
        r.adjust_for_ambient_noise(source,duration=0.2)
        try:
            audio=r.listen(source,timeout=3,phrase_time_limit=3)
            
            speak("Recognizing...")
            text=r.recognize_google(audio,language='en-in')
            
            print(f"User said: {text}\n")
            if text in ["quit","stop","exit"]:
                speak("exiting")
                exit()
            else:
                return text.lower()
        except sr.UnknownValueError:
            speak("Sorry, I did not understand that.")
            return None
        except sr.RequestError:
            speak("using offline recognition sphinx.")
            try:
                audio=r.listen(source,timeout=5,phrase_time_limit=8)
                text=r.recognize_sphinx(audio)
                speak(f"You said: {text}")
                return text
            except Exception:
                speak("Sorry, I did not understand that.")
                return None

def receive_and_speak():
    speak("Listening for messages...")
    start = time.time()

    while True:
        
        if time.time()-start > 20:
            speak("No new messages.")
            return

        try:
            res = requests.get(GET_URL, timeout=3)
            data = res.json()
            message = data.get("message", "")

            
            if message:
                speak(f"New message: {message}")

               
                try:
                    requests.post(CONFIRM_TEXT_URL, timeout=3)
                    speak("Message deleted.")
                except:
                    speak("Could not delete message.")

            

        except:
            speak("Network error while checking.")
            return


def record_and_send_voice():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        speak("🎙️ Speak now... I will auto-stop when you finish.")
        recognizer.adjust_for_ambient_noise(source)

        try:
            
            audio = recognizer.listen(source, timeout=1, phrase_time_limit=6)
        except Exception:
            speak("No speech detected.")
            return

    
    data = np.frombuffer(audio.get_raw_data(), dtype=np.int16)
    fs = audio.sample_rate

    filename = "voice_message.wav"
    write(filename, fs, data)

    speak(" Recorded. Uploading...")

    try:
        with open(filename, 'rb') as f:
            r = requests.post(UPLOAD_URL, files={'file': f})
        if r.status_code == 200:
            speak(" Voice uploaded.")
        else:
            speak("Upload failed.")
    except Exception:
        speak(" Upload error.")
count=0
def main():
    global count
    speak("Voice controlled message system activated.")
    speak("welcome to messaging system ")

    
    speak("Say receive audio to listen messages. Say send audio to record voice. Say stop or exit to quit.")
    while True:
        speak("speak your option ")
        command = listen()

        if command is None and count==2:
            speak("exiting")
        if command is None:
            speak("no response detected or couldnot understand the audio")
            
        else:
            if "receive" in command.lower():
                receive_and_speak()

            elif "send" in command:
                record_and_send_voice()

            elif command.lower() in ["quit","stop","exit"]:
                speak("Shutting down system. Goodbye.")
                return
            else:
                speak("Invalid command. Say receive, send or exit.")
    
if __name__ == "__main__":
    main()
