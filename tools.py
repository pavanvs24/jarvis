import requests
from config import APP_PATHS, SITE_URLS
import webbrowser
import shutil
import subprocess

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