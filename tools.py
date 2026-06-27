import requests
from config import APP_PATHS, SITE_URLS
import webbrowser
import shutil
import subprocess
import psutil
import datetime
import urllib.parse

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
    geo = requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1")
    geo_data = geo.json()

    if "results" not in geo_data or len(geo_data["results"]) == 0:
        return f"Sorry, I couldn't find weather data for {city}."

    lat = geo_data["results"][0]["latitude"]
    lon = geo_data["results"][0]["longitude"]

    weather = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true")
    weather_data = weather.json()

    temp = weather_data["current_weather"]["temperature"]
    windspeed = weather_data["current_weather"]["windspeed"]

    return f"Temperature in {city}: {temp}°C, Wind speed: {windspeed} km/h"

def remember_note(task):
    with open("notes.txt", "a") as file:
        file.write(task + "\n")

def read_notes():
    try:
        with open("notes.txt", "r") as file:
            return file.read()

    except (FileNotFoundError):
        return None

def delete_note(note):
    try:
        with open("notes.txt", "r") as file:
            lines = file.readlines()
            content = "".join(lines)
            if content.strip() == "":
                return "NoNotes"

    except FileNotFoundError:
        return "NoNotes"
    
    if note == "all":
        with open("notes.txt", "w") as file:
            return "ALL"

    note = int(note)
    if note > len(lines) or note < 1:
        return "InvalidNoteNumber"

    result = lines[note - 1] 
    del lines[note - 1]

    with open("notes.txt", "w") as file:
        file.writelines(lines)
        return result
    
    return False

def monitor_system():
    system_info = {}
    system_info["cpu_percent"] = psutil.cpu_percent()
    system_info["ram_percent"] = psutil.virtual_memory().percent
    system_info["battery_percent"] = psutil.sensors_battery().percent
    system_info["charging"] = psutil.sensors_battery().power_plugged
    system_info["disk_usage_percent"] = psutil.disk_usage('/').percent
    return system_info

def get_datetime():
    print("[Getting Datetime...]")
    now = datetime.datetime.now()
    date = now.strftime("%a, %b %d")
    time = now.strftime("%I:%M %p")
    return {"date": date, "time": time}

def search_brave(query):
    query = urllib.parse.quote_plus(query)
    search_url = f"https://search.brave.com/search?q={query}"
    webbrowser.open(search_url)
