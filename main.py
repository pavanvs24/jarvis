from dotenv import load_dotenv
import os
import requests

load_dotenv()

api_key = os.environ.get("GROQ_API_KEY")

response = requests.post(
    "https://api.groq.com/openai/v1/chat/completions",
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    },
    json = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "user", "content": "Say hello!"}
        ]
    }
)

data = response.json()

reply = data["choices"][0]["message"]["content"]

print(reply)