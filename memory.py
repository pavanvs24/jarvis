import json
import brain

def load_memory():
    try:
        with open("memory.json", "r") as file:
            return json.load(file)
    except (json.JSONDecodeError, FileNotFoundError):
        history = {"provider": "gemini", "history": []}
        save_memory(history)
        return history

def save_memory(conversation_history):
    with open("memory.json", "w") as file:
        json.dump(conversation_history, file)

def append_user(conversation_history, text):
    if brain.PROVIDER == "gemini":
        conversation_history["history"].append({"role": "user", "parts": [{"text": text}]})
    elif brain.PROVIDER == "grok":
        conversation_history["history"].append({"role": "user", "content": text})

def append_assistant(conversation_history, text):
    if brain.PROVIDER == "gemini":
        conversation_history["history"].append({"role": "model", "parts": [{"text": text}]})
    elif brain.PROVIDER == "grok":
        conversation_history["history"].append({"role": "assistant", "content": text})

def to_internal(conversational_history, provider):
    internal = []

    if provider == "gemini":
        for chat in conversational_history["history"]:
            text = chat["parts"][0]["text"]
            if chat["role"] == "user":
                internal.append({"role": "user", "text": text})
            elif chat["role"] == "model":
                internal.append({"role": "assistant", "text": text})
    
    elif provider == "grok":
        for chat in conversational_history["history"]:
            text = chat["content"]
            if chat["role"] == "user":
                internal.append({"role": "user", "text": text})
            elif chat["role"] == "assistant":
                internal.append({"role": "assistant", "text": text})

    return internal

def to_provider(internal):
    new = {"provider": brain.PROVIDER, "history":[]}
    for chat in internal:
        text = chat["text"] 
        if chat["role"] == "user":
            append_user(new, text)
        elif chat["role"] == "assistant":
            append_assistant(new, text)
    return new
