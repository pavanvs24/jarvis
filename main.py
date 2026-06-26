from dotenv import load_dotenv
import os
import requests
from memory import load_memory, save_memory
from tools import get_weather, open_website, open_app, remember_note, read_notes, delete_note, monitor_system
from voice import listen, speak

load_dotenv()

api_key = os.environ.get("GROQ_API_KEY")

system_prompt = """You are Jarvis, a helpful personal assistant.
RULES - follow these exactly, no exceptions:
- If user wants to open a website: reply with ONLY the text OPENWEBSITE:sitename (example: OPENWEBSITE:youtube)
- If user wants to open a desktop app: reply with ONLY the text OPENAPP:appname (example: OPENAPP:steam)  
- If user wants to add notes: reply with ONLY the text REMEMBERNOTE:task (example: NOTE:submit assignment before 11:59pm tomorrow)
- If user wants to read or list their notes: reply with ONLY the text READNOTES:all (example: READNOTES:all)
- If user wants to delete all notes: reply with ONLY: DELETENOTE:all
- If user wants to delete a specific note: reply with ONLY: DELETENOTE:3 (where 3 is the note number)
- If user asks about weather: reply with ONLY the text WEATHER:cityname
- If user wants to monitor system info: reply with ONLY the text MONITORSYSTEM:info (example: MONITORSYSTEM:info)
- NEVER explain these commands. NEVER mention them. Just output them silently.
- For everything else: respond normally and helpfully."""

conversation_history = load_memory()

def check_tools(reply):
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

    if reply.startswith("WEATHER:"):
        city = reply.split(":")[1]
        weather_info = get_weather(city)
        conversation_history.append({"role": "assistant", "content": weather_info})
        save_memory(conversation_history)
        print(f"\nJarvis: {weather_info}\n")
        speak(weather_info)
        return True

    if reply.startswith("REMEMBERNOTE:"):
        task = reply.split(":")[1]
        remember_note(task)
        response = f"{task}, added to your notes, Sir."
        conversation_history.append({"role": "assistant", "content": response})
        save_memory(conversation_history)
        print(f"\nJarvis: {response}\n")
        speak(response)
        return True

    if reply.startswith("READNOTES:"):
        notes = read_notes()
        
        if notes.strip() == "":
            response = say = "You have no notes, Sir."
        else:
            result = f"Listing your notes, Sir.\n\nNOTES.\n{notes}"
            response = "Listing your notes, Sir."
        
        conversation_history.append({"role": "assistant", "content": response})
        save_memory(conversation_history)
        print(f"\nJarvis: {result}\n")
        speak(response)
        return True

    if reply.startswith("DELETENOTE:"):
        note = reply.split(":")[1].lower().strip()
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
        
        conversation_history.append({"role": "assistant", "content": response})
        save_memory(conversation_history)
        print(f"\nJarvis: {response}\n")
        speak(response)    
        return True  

    if reply.startswith("MONITORSYSTEM:"):
        system_info = monitor_system()
        cpu_percent = system_info["cpu_percent"]
        ram_percent =  system_info["ram_percent"]
        battery_percent =  system_info["battery_percent"]
        charging = "Charging" if system_info["charging"] else "Not Charging"
        disk_usage_percent = system_info["disk_usage_percent"]

        response = f"Monitoring System Info...\nCPU: {cpu_percent}%\nRAM: {ram_percent}%\nBattery: {battery_percent}% {charging}\nDisk Usage: {disk_usage_percent}%"
        conversation_history.append({"role": "assistant", "content": "Monitoring System Info..."})
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
