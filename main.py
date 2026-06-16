from dotenv import load_dotenv
import os
import requests
import json

load_dotenv()

api_key = os.environ.get("GROQ_API_KEY")

system_prompt = "You are a helpful personal assistant. When the user asks about weather in any city, do not reply normally. Instead reply with exactly: WEATHER:cityname. Replace the cityname with the city they mentioned"

conversation_history = []

try:
    with open("memory.json", "r") as file:
        conversation_history = json.load(file)
except (json.JSONDecodeError, FileNotFoundError):
    pass

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

while True:
    user_input = input("You: ")

    conversation_history.append({"role": "user", "content": user_input})

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json = {
            "model": "llama-3.1-8b-instant",
            "messages": [{"role": "system", "content": system_prompt}] + conversation_history
        }
    )

    data = response.json()
    reply = data["choices"][0]["message"]["content"]

    if reply.startswith("WEATHER:"):
        city = reply.split(":")[1]
        weather_info = get_weather(city)
        print(f"\nJarvis: {weather_info}\n")
        conversation_history.append({"role": "assistant", "content": weather_info})
        continue

    conversation_history.append({"role": "assistant", "content": reply})

    with open("memory.json", "w") as file:
        json.dump(conversation_history, file)

    print(f"\nJarvis: {reply}\n")