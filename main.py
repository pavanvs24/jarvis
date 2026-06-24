from dotenv import load_dotenv
import os
import requests
from memory import load_memory, save_memory
from tools import get_weather, open_website, open_app
from voice import listen, speak

load_dotenv()

api_key = os.environ.get("GROQ_API_KEY")

system_prompt = """You are Jarvis, a helpful personal assistant.
RULES - follow these exactly, no exceptions:
- If user wants to open a website: reply with ONLY the text OPENWEBSITE:sitename (example: OPENWEBSITE:youtube)
- If user wants to open a desktop app: reply with ONLY the text OPENAPP:appname (example: OPENAPP:steam)  
- If user asks about weather: reply with ONLY the text WEATHER:cityname
- NEVER explain these commands. NEVER mention them. Just output them silently.
- For everything else: respond normally and helpfully."""

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
    
    if reply.startswith("OPENWEBSITE:"):
        sitename = reply.split(":")[1]
        response = f"Opening {sitename}"
        conversation_history.append({"role": "assistant", "content": response})
        save_memory(conversation_history)
        print(f"\nJarvis: {response}\n")
        speak(response)
        open_website(sitename)
        return True

    if reply.startswith("OPENAPP:"):
        appname = reply.split(":")[1]
        if open_app(appname):
            response = f"Opening {appname}"
        else:
            response = f"Could not find {appname}"
        conversation_history.append({"role": "assistant", "content": response})
        save_memory(conversation_history)
        print(f"\nJarvis: {response}\n")
        speak(response)
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