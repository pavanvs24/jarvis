from dotenv import load_dotenv
import os
import requests
import json
from memory import load_memory, save_memory
from tools import get_weather
from voice import listen, speak

load_dotenv()

api_key = os.environ.get("GROQ_API_KEY")

system_prompt = """You are Jarvis, a helpful and conversational personal assistant. 
Talk naturally and helpfully in response to anything the user says.
The ONLY exception: if the user asks about weather in a specific city, respond with exactly WEATHER:cityname and nothing else.
For everything else, respond normally like a helpful assistant."""

conversation_history = load_memory()

def check_tools(reply):
    if reply.startswith("WEATHER:"):
        city = reply.split(":")[1]
        weather_info = get_weather(city)
        conversation_history.append({"role": "assistant", "content": weather_info})
        save_memory(conversation_history)
        print(f"\nJarvis: {weather_info}\n")
        speak(weather_info)
        return True

    return False

while True:
    user_input = listen()
    print(f"You: {user_input}")

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

    if check_tools(reply):
        continue

    conversation_history.append({"role": "assistant", "content": reply})
    save_memory(conversation_history)

    print(f"\nJarvis: {reply}\n")
    speak(reply)