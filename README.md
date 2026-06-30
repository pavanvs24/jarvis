# Jarvis — Personal AI Assistant

A modular personal AI assistant built in Python, capable of helping with daily tasks through natural conversation. Powered by Groq's LLaMA API.

---

## Features

- **Conversational AI** — Natural language conversation with persistent memory across sessions
- **Weather** — Real-time weather data for any city
- **Notes** — Save, read, and delete personal notes by voice or text
- **Open Apps & Websites** — Launch desktop apps and websites by name
- **System Monitor** — Live CPU, RAM, battery, and disk usage
- **Movie Player** — Find and play movies from your local folder using fuzzy search
- **Music Search** — Search and play songs via Spotify URI
- **Web Search** — Search the web directly via Brave Search
- **Date & Time** — Get current date, time, or both on request
- **Screenshot** — Capture your screen on command
- **Voice Output** — Jarvis speaks responses out loud via text-to-speech

---

## Project Structure

```
jarvis/
├── main.py        # Core conversation loop and tool dispatcher
├── memory.py      # Persistent JSON-based conversation memory
├── tools.py       # All tool functions (weather, notes, apps, etc.)
├── voice.py       # Voice input (Whisper) and output (pyttsx3)
├── config.py      # App paths, site URLs, media folders
├── .env           # API keys (not committed)
└── memory.json    # Conversation history (not committed)
```

---

## Setup

### 1. Clone the repo
```bash
git clone https://github.com/pavanvs24/jarvis.git
cd jarvis
```

### 2. Create a virtual environment
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
```

### 3. Install dependencies
```bash
pip install python-dotenv requests psutil pyautogui rapidfuzz openai-whisper sounddevice numpy pyttsx3 plyer playsound==1.2.2
```

### 4. Set up your API key
Create a `.env` file in the root folder:
```
GROQ_API_KEY=your_key_here
```
Get a free key at [console.groq.com](https://console.groq.com)

### 5. Configure your apps and media
Edit `config.py` to add your app paths, favourite websites, and media folders.

### 6. Run
```bash
python main.py
```

---

## How It Works

Jarvis uses a keyword-command pattern — the LLM detects intent from your message and responds with a structured token like `WEATHER:bangalore` or `OPENAPP:steam`. The Python layer intercepts these tokens and executes the corresponding tool, keeping the LLM as the brain and Python as the hands.

---

## Tech Stack

- **LLM** — LLaMA 3.3 70B via Groq API
- **Speech-to-Text** — OpenAI Whisper (local)
- **Text-to-Speech** — pyttsx3
- **Fuzzy Matching** — rapidfuzz
- **System Info** — psutil
- **Weather** — Open-Meteo (no API key needed)

---

## Roadmap

- [ ] Web-based UI (Flask + HTML frontend)
- [ ] Voice input with better microphone support
- [ ] News headlines tool
- [ ] Reminder system with alarm
- [ ] Agentic multi-step task execution
- [ ] Switch to local models (Ollama) for privacy

---

## Author

**Pavan VS** ([@pavanvs24](https://github.com/pavanvs24))
First-year CSE student, building Jarvis as a hands-on learning project — software engineering, AI integration, and system architecture, one milestone at a time.

Started June 2026 — actively developed.