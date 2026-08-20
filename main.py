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
from voice import listen, speak

load_dotenv()

api_key = os.environ.get("GEMINI_API_KEY")
news_key = os.environ.get("NEWS_API_KEY")

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

def check_tools(reply):
    if reply.startswith("OPENWEBSITE:"):
        sitename = reply.split(":", 1)[1].strip()
        response = f"Opening {sitename}"

        append_assistant(conversation_history, response)
        save_memory(conversation_history)

        print(f"\nJarvis: {response}\n")
        speak(response)
        open_website(sitename)
        return True

    if reply.startswith("OPENAPP:"):
        appname = reply.split(":", 1)[1].strip()

        if open_app(appname):
            response = f"Opening {appname}"
        else:
            response = f"Could not find {appname}"

        append_assistant(conversation_history, response)
        save_memory(conversation_history)

        print(f"\nJarvis: {response}\n")
        speak(response)
        return True

    if reply.startswith("WEATHER:"):
        city = reply.split(":", 1)[1].strip()
        weather_info = get_weather(city)

        append_assistant(conversation_history, weather_info)
        save_memory(conversation_history)

        print(f"\nJarvis: {weather_info}\n")
        speak(weather_info)
        return True

    if reply.startswith("REMEMBERNOTE:"):
        task = reply.split(":", 1)[1].strip()
        remember_note(task)

        response = f"{task}, added to your notes, Sir."

        append_assistant(conversation_history, response)
        save_memory(conversation_history)

        print(f"\nJarvis: {response}\n")
        speak(response)
        return True

    if reply.startswith("READNOTES:"):
        notes = read_notes()

        if notes.strip() == "":
            response = "You have no notes, Sir."
            result = response
        else:
            result = f"Listing your notes, Sir.\n\nNOTES.\n{notes}"
            response = "Listing your notes, Sir."

        append_assistant(conversation_history, response)
        save_memory(conversation_history)

        print(f"\nJarvis: {result}\n")
        speak(response)
        return True

    if reply.startswith("DELETENOTE:"):
        note = reply.split(":", 1)[1].lower().strip()
        code = delete_note(note)

        if code == False:
            response = "An unknown error occured, Sir."
        elif code == "ALL":
            response = "All notes cleared, Sir."
        elif code == "NoNotes":
            response = "You have no Notes, Sir."
        elif code == "InvalidNoteNumber":
            response = f"{note} is an invalid note number, Sir."
        else:
            response = f"{code} note deleted, Sir."

        append_assistant(conversation_history, response)
        save_memory(conversation_history)

        print(f"\nJarvis: {response}\n")
        speak(response)
        return True

    if reply.startswith("MONITORSYSTEM:"):
        system_info = monitor_system()

        cpu_percent = system_info["cpu_percent"]
        ram_percent = system_info["ram_percent"]
        battery_percent = (
            f"{system_info['battery_percent']}%"
            if system_info["battery_percent"]
            else "No Battery"
        )
        charging = "Charging" if system_info["charging"] else "Not Charging"
        disk_usage_percent = system_info["disk_usage_percent"]

        response = (
            f"Monitoring System Info...\n"
            f"CPU: {cpu_percent}%\n"
            f"RAM: {ram_percent}%\n"
            f"Battery: {battery_percent} {charging}\n"
            f"Disk Usage: {disk_usage_percent}%"
        )

        print(f"\nJarvis: {response}\n")
        speak(response)
        return True

    if reply.startswith("DATETIME:"):
        check = reply.split(":", 1)[1].strip()
        now = get_datetime()

        if check == "date":
            response = f"{now['date']}"
        elif check == "time":
            response = f"{now['time']}"
        elif check == "datetime":
            response = f"{now['date']} | {now['time']}"
        else:
            return False

        print(f"\nJarvis: {response}\n")
        speak(response)
        return True

    if reply.startswith("SEARCHBRAVE:"):
        query = reply.split(":", 1)[1].strip()

        response = f"Searching for {query}, Sir."

        print(f"\nJarvis: {response}\n")
        speak(response)
        search_brave(query)
        return True

    if reply.startswith("TAKESCREENSHOT:"):
        take_screenshot()

        response = "Screenshot Taken, Sir."

        print(f"\nJarvis: {response}\n")
        speak(response)
        return True

    if reply.startswith("PLAYMOVIE:"):
        movie = reply.split(":", 1)[1].strip()
        movie_path = find_movie(movie)

        if movie_path is None:
            response = f"Could not find the movie {movie}, Sir."
            print(f"\nJarvis: {response}\n")
            speak(response)
        else:
            response = f"Playing Movie: {movie}, Sir."
            print(f"\nJarvis: {response}\n")
            speak(response)
            os.startfile(movie_path)

        return True

    if reply.startswith("PLAYSONG:"):
        song = reply.split(":", 1)[1].strip()

        response = f"Searching for {song} on Spotify, Sir."

        print(f"\nJarvis: {response}\n")
        speak(response)
        search_song(song)
        return True

    if reply.startswith("GETNEWS:"):
        number = 5

        _, endpoint, time_interval, filters = reply.split(":", 3)

        articles = get_news(
            endpoint,
            time_interval,
            filters,
            number,
            news_key
        )

        if articles == "error":
            response = "Unable to fetch news, Sir."

            print(f"\nJarvis: {response}\n")
            speak(response)
            return True

        if articles == "noresults":
            response = "No results found, Sir."

            print(f"\nJarvis: {response}\n")
            speak(response)
            return True

        speak("Reading the news headlines, Sir.")

        headlines = []

        print("Top Headlines.")

        for i in range(len(articles)):
            article = articles[i]

            print(f"\n{i + 1}. {article['title']}")
            print(f"   Source    : {article['source']['name']}")
            print(f"   Published : {article['publishedAt']}")
            print(f"   Summary   : {article['description']}")
            print(f"   Read more : {article['url']}")

            headlines.append(article["title"])

        for title in headlines:
            speak(title)

        return True

    return False

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

    if check_tools(reply):
        continue

    append_assistant(conversation_history, reply)

    save_memory(conversation_history)

    print(f"\nJarvis: {reply}\n")
    speak(reply)
