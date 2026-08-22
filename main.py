from dotenv import load_dotenv
import os
import requests
from memory import load_memory, save_memory, append_user, append_assistant
from tools import (
    search_song, find_movie, take_screenshot, 
    search_brave, get_weather, open_website, open_app, 
    remember_note, read_notes, delete_note, 
    monitor_system, get_datetime, get_news
)
from tool_handlers import check_tools
from voice import listen, speak

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")

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

conversation_history = load_memory()

while True:
    #user_input = listen()
    #print(f"You: {user_input}")
    user_input = input("You: ")
    append_user(conversation_history, user_input)

    response = requests.post(
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent",
        headers={
            "Content-Type": "application/json"
        },
        params={
            "key": api_key
        },
        json={
            "systemInstruction": {
                "parts": [
                    {"text": system_prompt}
                ]
            },
            "contents": conversation_history
        }
    )
    data = response.json()

    if "error" in data:
        print(f"\nGemini Error: {data['error']['message']}\n")
        continue
    reply = data["candidates"][0]["content"]["parts"][0]["text"]

    is_tool, tool_reply, tool_log = check_tools(reply)
    if is_tool:
        if tool_log:
            append_assistant(conversation_history, tool_log)
            save_memory(conversation_history)
        if tool_reply:
            print(f"\nJarvis: {tool_reply}\n")
            speak(tool_reply)
        continue

    append_assistant(conversation_history, reply)
    save_memory(conversation_history)
    print(f"\nJarvis: {reply}\n")
    speak(reply)
