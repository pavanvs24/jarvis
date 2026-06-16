from dotenv import load_dotenv
import os
import requests
import json

load_dotenv()

api_key = os.environ.get("GROQ_API_KEY")

messages = []

try:
    with open("memory.json", "r") as file:
        messages = json.load(file)
except (json.JSONDecodeError, FileNotFoundError):
    pass

while True:
    user_input = input("You: ")

    messages.append({"role": "user", "content": user_input})

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json = {
            "model": "llama-3.1-8b-instant",
            "messages": messages
        }
    )

    data = response.json()
    reply = data["choices"][0]["message"]["content"]

    messages.append({"role": "assistant", "content": reply})

    with open("memory.json", "w") as file:
        json.dump(messages, file)

    print(f"\nJarvis: {reply}\n")