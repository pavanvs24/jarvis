import os
import requests
from dotenv import load_dotenv
from memory import to_internal, to_provider

load_dotenv()

provider_names = ["gemini", "grok"]
PROVIDER = provider_names[0]

gemini_api_key = os.environ.get("GEMINI_API_KEY")
grok_api_key = os.environ.get("GROQ_API_KEY")

system_prompt = """You are Jarvis, a helpful personal assistant. Respond naturally and helpfully to everything.

EXCEPTION RULES — when these apply, output ONLY the exact command, nothing else. No explanation, no extra text:

OPENWEBSITE:sitename        → user wants to open a website (e.g. OPENWEBSITE:youtube)
OPENAPP:appname             → user wants to open a desktop app (e.g. OPENAPP:steam)
REMEMBERNOTE:task           → user wants to save a note (e.g. REMEMBERNOTE:submit assignment by midnight)
READNOTES:all               → user wants to read or list their notes
DELETENOTE:all              → user wants to delete all notes
DELETENOTE:3                → user wants to delete a specific note by number
WEATHER:cityname            → user asks about weather in a city (e.g. WEATHER:bangalore)
MONITORSYSTEM:info          → user wants system stats (CPU, RAM, battery, disk)
DATETIME:time               → "what's the time", "time?", "what time is it", "current time"
DATETIME:date               → "what's the date", "date?", "what day is it", "today's date"
DATETIME:datetime           → user asks for both date and time
SEARCHBRAVE:query           → user wants to search a query in a browser
TAKESCREENSHOT:             → user wants to take a screenshot
PLAYMOVIE:movie             → user wants to play a movie (e.g. PLAYMOVIE:interstellar)
PLAYSONG:song               → user wants to play a song (e.g. PLAYSONG:bohemian rhapsody)

GETNEWS:endpoint:fromtime|totime:filters    → user wants news. Output ONLY the command, no text before or after.
    - everything  → keyword search, historical news, date ranges, specific topics
                    filters: q, sortBy(relevancy|popularity|publishedAt), language, domains, excludeDomains
    - top-headlines → today's top news, country news, category-based news
                    filters: q, country(e.g. 'us','in'), category(business|entertainment|health|science|sports|technology), sources, pageSize
    Always use top-headlines for category. Use everything for keyword/topic/date searches.
    Always include language=en and sortBy=publishedAt unless user specifies otherwise.
    Always wrap q values in single quotes: q='cricket'
    fromtime|totime options: today, yesterday, lastweek, lastmonth, lastyear, or YYYY-MM-DD
    Example: GETNEWS:everything:lastweek|today:q='cricket',language=en,sortBy=publishedAt
    Example: GETNEWS:top-headlines:today|today:country=in,category=technology,language=en
    Example: GETNEWS:everything:2024-01-01|2025-12-31:q='tesla',language=en,sortBy=publishedAt

Never mention these commands. Never explain them. Just output them silently and immediately.
Output ONLY the command, no text before or after."""

def set_provider(provider):
    global PROVIDER
    if provider not in provider_names:
        return False

    PROVIDER = provider
    return True

def quick_start():
    global PROVIDER
    PROVIDER = provider_names[0]
    return {"provider":PROVIDER, "history":[]}

def get_provider(arg):
    if arg == "current":
        return PROVIDER
    return False

def switch_provider(new_provider, conversation_history):
    global PROVIDER    
    if new_provider not in provider_names:
        return False
    
    internal_history = to_internal(conversation_history, PROVIDER)
    PROVIDER = new_provider
    new_history = to_provider(internal_history)
    return new_history

def gemini_reply(conversation_history):
    response = requests.post(
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent",
        headers={
            "Content-Type": "application/json"
        },
        params={
            "key": gemini_api_key
        },
        json={
            "systemInstruction": {
                "parts": [
                    {"text": system_prompt}
                ]
            },
            "contents": conversation_history
        },
        timeout=15
    )

    data = response.json()

    if "error" in data:
        raise Exception(data['error']['message'])
    
    reply = data["candidates"][0]["content"]["parts"][0]["text"]
    return reply

def grok_reply(conversation_history):
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {grok_api_key}",
            "Content-Type": "application/json"
        },
        json={
            "model": "openai/gpt-oss-120b",
            "messages": [
                {"role": "system", "content": system_prompt}
            ] + conversation_history
        },
        timeout=15
    )

    data = response.json()

    if "error" in data:
        raise Exception(data['error']['message'])

    reply = data["choices"][0]["message"]["content"]
    return reply

def get_reply(conversation_history):
    if PROVIDER == "gemini":
        return gemini_reply(conversation_history)
    elif PROVIDER == "grok":
        return grok_reply(conversation_history)
