import os
import threading
import whisper
import keyboard
import sounddevice as sd
import numpy as np
from piper import PiperVoice

model = whisper.load_model("small")

VOICE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "voices", "en_US-lessac-medium.onnx")

_voice = None
_thread = None
_stop = threading.Event()

def listen():
    print("[Listening for 10 seconds...]")
    recording = sd.rec(int(10 * 16000), samplerate=16000, channels=1, dtype='float32')
    sd.wait()
    print("[Processing...]")
    audio = np.squeeze(recording)
    result = model.transcribe(audio)
    return result["text"]

def _get_voice():
    global _voice
    if not _voice:
        _voice = PiperVoice.load(VOICE_PATH)
    return _voice

def _run(text):
    stream = None
    hotkey = None
    try:
        voice = _get_voice()
        for chunk in voice.synthesize(text):
            if _stop.is_set():
                break
            if stream is None:
                stream = sd.RawOutputStream(samplerate=chunk.sample_rate, 
                                            channels=chunk.sample_channels,
                                            dtype="int16")
                stream.start()
            data = chunk.audio_int16_bytes
            step = 2048 * chunk.sample_width * chunk.sample_channels
            for i in range(0, len(data), step):
                if _stop.is_set():
                    break
                stream.write(data[i:i + step])
        if stream:
            stream.abort() if _stop.is_set() else stream.stop()
    except Exception as e:
        print(f"[TTS error] {e}")
    finally:
        stream.close()

def speak(text, block=False):
    global _thread
    stop_speaking()
    text = text.replace("#", "").replace("*", "")
    if not text.strip():
        return
    _stop.clear()
    _thread = threading.Thread(target=_run, args=(text,), daemon=True)
    _thread.start()
    if block:
        _thread.join()

def stop_speaking():
    global _thread
    _stop.set()
    if _thread and _thread.is_alive():
        _thread.join(timeout=2)
    _thread = None
