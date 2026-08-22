from tools import (
    search_song, play_movie, take_screenshot, 
    search_brave, get_weather, open_website, open_app, 
    remember_note, read_notes, delete_note, 
    monitor_system, get_datetime, get_news
)
import os
from dotenv import load_dotenv
from voice import speak

load_dotenv()

news_key = os.environ.get("NEWS_API_KEY")

def handle_monitor_system(command):
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
        f"Monitoring System Info, Sir...\n"
        f"CPU: {cpu_percent}%\n"
        f"RAM: {ram_percent}%\n"
        f"Battery: {battery_percent} {charging}\n"
        f"Disk Usage: {disk_usage_percent}%"
    )
    memory = None

    return True, response, memory

def handle_datetime(command):
    check = command.split(":", 1)[1].strip()
    now = get_datetime()

    if check == "date":
        response = f"{now['date']}"
    elif check == "time":
        response = f"{now['time']}"
    elif check == "datetime":
        response = f"{now['date']} | {now['time']}"
    else:
        return False, None, None

    memory = None

    return True, response, memory

def handle_open_website(command):
    sitename = command.split(":", 1)[1].strip()
    response = f"Opening {sitename}, Sir."
    memory = None
    open_website(sitename)
    return True, response, memory

def handle_open_app(command):
    appname = command.split(":", 1)[1].strip()

    if open_app(appname):
        response = f"Opening {appname}, Sir."
    else:
        response = f"Could not find {appname}, Sir."

    memory = None
    return True, response, memory

def handle_search_brave(command):
    query = command.split(":", 1)[1].strip()

    response = f"Searching for {query}, Sir."
    memory = None
    search_brave(query)
    return True, response, memory

def handle_get_weather(command):
    city = command.split(":", 1)[1].strip()
    weather_info = get_weather(city)
    response = weather_info
    memory = None
    return True, response, memory

def handle_take_screenshot(command):
    take_screenshot()
    response = "Screenshot Taken, Sir."
    memory = None
    return True, response, memory

def handle_remember_note(command):
    task = command.split(":", 1)[1].strip()
    remember_note(task)
    response = f"{task}, added to your notes, Sir."
    memory = None
    return True, response, memory

def handle_read_notes(command):
    notes = read_notes()

    if notes.strip() == "":
        response = "You have no notes, Sir."
    else:
        response = None
        result = f"Listing your notes, Sir.\n\nNOTES.\n{notes}"
        print(result)
        speak("Listing your notes, Sir.")

    memory = None
    return True, response, memory

def handle_delete_note(command):
    note = command.split(":", 1)[1].lower().strip()
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

    memory = None
    return True, response, memory

def handle_play_movie(command):
    movie = command.split(":", 1)[1].strip()
    movie_path = play_movie(movie)

    if movie_path is None:
        response = f"Could not find the movie {movie}, Sir."
    else:
        response = f"Playing Movie: {movie}, Sir."

    memory = None
    return True, response, memory

def handle_search_song(command):
    song = command.split(":", 1)[1].strip()
    response = f"Searching for {song} on Spotify, Sir."
    memory = None
    search_song(song)
    return True, response, memory

def handle_get_news(command):
    number = 5
    _, endpoint, time_interval, filters = command.split(":", 3)
    memory = None

    articles = get_news(
        endpoint,
        time_interval,
        filters,
        number,
        news_key
    )

    if articles == "error":
        response = "Unable to fetch news, Sir."
        return True, response, memory
    
    if articles == "noresults":
        response = "No results found, Sir."
        return True, response, memory

    headlines = []
    print("Top Headlines.")
    speak("Reading the news headlines, Sir.")
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

    return True, None, memory

TOOLS = {
    "MONITORSYSTEM:": handle_monitor_system,
    "DATETIME:": handle_datetime,
    "OPENWEBSITE:": handle_open_website,
    "OPENAPP:": handle_open_app,
    "SEARCHBRAVE:": handle_search_brave,
    "WEATHER:": handle_get_weather,
    "TAKESCREENSHOT:": handle_take_screenshot,
    "REMEMBERNOTE:": handle_remember_note,
    "READNOTES:": handle_read_notes,
    "DELETENOTE:": handle_delete_note,
    "PLAYMOVIE:": handle_play_movie,
    "PLAYSONG:": handle_search_song,
    "GETNEWS:": handle_get_news
}

def check_tools(command):
    for prefix, handler in TOOLS.items():
        if command.startswith(prefix):
            return handler(command)
    
    return False, None, None
