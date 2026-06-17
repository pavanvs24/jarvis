import json

def load_memory():
    try:
        with open("memory.json", "r") as file:
            return json.load(file)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def save_memory(conversation_history):
    with open("memory.json", "w") as file:
        json.dump(conversation_history, file)