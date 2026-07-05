import whisper
import sounddevice as sd
import numpy as np
import pyttsx3
import threading
import keyboard

model = whisper.load_model("small")

def listen():
    print("[Listening for 10 seconds...]")
    recording = sd.rec(int(10 * 16000), samplerate=16000, channels=1, dtype='float32')
    sd.wait()
    print("[Processing...]")
    audio = np.squeeze(recording)
    result = model.transcribe(audio)
    return result["text"]

def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
    engine.stop()