import os
import re
import requests
from config import APP_PATHS, SITE_URLS, MEDIA_PATHS
from rapidfuzz import process
import webbrowser
import shutil
import subprocess
import psutil
import datetime
from dateutil.relativedelta import relativedelta
import urllib.parse
import pyautogui

NOTES_FILE = "notes.txt"
TIMEOUT = 15


def open_website(sitename):
    sitename = sitename.lower().strip()

    if sitename in SITE_URLS:
        webbrowser.open(SITE_URLS[sitename])
        return

    if "." in sitename:
        site_url = f"https://{sitename}"
    else:
        site_url = f"https://{sitename}.com"

    webbrowser.open(site_url)


def open_app(appname):
    appname = appname.lower().strip()

    if appname in APP_PATHS:
        subprocess.Popen(APP_PATHS[appname])
        return True

    path = shutil.which(appname)
    if path:
        subprocess.Popen(path)
        return True

    return False


def get_weather(city):
    try:
        geo = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": city, "count": 1},
            timeout=TIMEOUT,
        )
        geo_data = geo.json()

        if not geo_data.get("results"):
            return f"Sorry, I couldn't find weather data for {city}."

        lat = geo_data["results"][0]["latitude"]
        lon = geo_data["results"][0]["longitude"]

        weather = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={"latitude": lat, "longitude": lon, "current_weather": "true"},
            timeout=TIMEOUT,
        )
        current = weather.json()["current_weather"]
    except (requests.RequestException, KeyError, ValueError):
        return "Couldn't fetch the weather right now."

    return (
        f"Temperature in {city}: {current['temperature']}°C, "
        f"Wind speed: {current['windspeed']} km/h"
    )


def remember_note(task):
    with open(NOTES_FILE, "a", encoding="utf-8") as file:
        file.write(task + "\n")


def read_notes():
    """Returns a list of notes (empty list if none)."""
    try:
        with open(NOTES_FILE, "r", encoding="utf-8") as file:
            return [line.rstrip("\n") for line in file if line.strip()]
    except FileNotFoundError:
        return []


def _write_notes(notes):
    with open(NOTES_FILE, "w", encoding="utf-8") as file:
        for note in notes:
            file.write(note + "\n")


def delete_note(note):
    notes = read_notes()
    if not notes:
        return "NoNotes"

    if note == "all":
        _write_notes([])
        return "ALL"

    if not note.isdigit():
        return "InvalidNoteNumber"

    index = int(note)
    if index < 1 or index > len(notes):
        return "InvalidNoteNumber"

    removed = notes.pop(index - 1)
    _write_notes(notes)
    return removed


def monitor_system():
    system_info = {}
    system_info["cpu_percent"] = psutil.cpu_percent()
    system_info["ram_percent"] = psutil.virtual_memory().percent
    system_info["disk_usage_percent"] = psutil.disk_usage(os.path.abspath(os.sep)).percent
    battery = psutil.sensors_battery()
    system_info["battery_percent"] = battery.percent if battery else None
    system_info["charging"] = battery.power_plugged if battery else None
    return system_info


def get_datetime():
    now = datetime.datetime.now()
    date = now.strftime("%a, %b %d")
    time = now.strftime("%I:%M %p")
    return {"date": date, "time": time}


def search_brave(query):
    query = urllib.parse.quote_plus(query)
    webbrowser.open(f"https://search.brave.com/search?q={query}")


def take_screenshot():
    image = pyautogui.screenshot()
    now = datetime.datetime.now()
    filename = now.strftime("screenshot_%Y%m%d_%H%M%S.png")
    image.save(filename)
    return filename


def play_movie(movie):
    folder = MEDIA_PATHS["movies"]
    try:
        files = os.listdir(folder)
    except OSError:
        return None

    if not files:
        return None

    match, score, _ = process.extractOne(movie, files)

    if score > 60:
        movie_path = os.path.join(folder, match)
        os.startfile(movie_path)
        return movie_path
    return None


def search_song(song):
    webbrowser.open(f"spotify:search:{song}")


def _find_date(relation):
    try:
        datetime.datetime.strptime(relation, "%Y-%m-%d")
        return relation
    except ValueError:
        pass

    today = datetime.datetime.today()
    if relation == "today":
        date = today
    elif relation == "yesterday":
        date = today - relativedelta(days=1)
    elif relation == "lastweek":
        date = today - relativedelta(weeks=1)
    elif relation == "lastmonth":
        date = today - relativedelta(months=1)
    elif relation == "lastyear":
        date = today - relativedelta(years=1)
    else:
        date = today

    return date.strftime("%Y-%m-%d")


def _parse_filters(filters):
    # "q='cricket',language=en" -> {"q": "cricket", "language": "en"}
    params = {}
    for key, value in re.findall(r"(\w+)=('[^']*'|[^,]*)", filters):
        params[key] = value.strip().strip("'")
    return params


def get_news(endpoint, time_interval, filters, number, news_key):
    if not news_key:
        return "error"

    params = _parse_filters(filters)
    params.setdefault("pageSize", number)

    # from/to are only valid for the "everything" endpoint
    if endpoint == "everything":
        from_time, _, to_time = time_interval.partition("|")
        params["from"] = _find_date(from_time)
        params["to"] = _find_date(to_time or "today")

    try:
        response = requests.get(
            f"https://newsapi.org/v2/{endpoint}",
            params=params,
            headers={"X-Api-Key": news_key},
            timeout=TIMEOUT,
        )
        news_data = response.json()
    except (requests.RequestException, ValueError):
        return "error"

    if news_data.get("status") == "error":
        return "error"

    if news_data.get("totalResults", 0) == 0:
        return "noresults"

    return news_data["articles"][:number]