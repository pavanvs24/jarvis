from brain import get_reply, set_provider, get_provider, switch_provider, quick_start
from memory import load_memory, save_memory, append_user, append_assistant
from tool_handlers import check_tools
from voice import listen, speak, stop_speaking

conversation_history = load_memory()

if not set_provider(conversation_history["provider"]):
    conversation_history = quick_start()
    save_memory(conversation_history)

speak("All Systems Optimal and Ready for Action, Sir. What we up to today ?")

while True:
    #user_input = listen()
    #print(f"You: {user_input}")
    user_input = input("You: ")
    stop_speaking()

    if not user_input.strip():
        continue

    if user_input.startswith("GETPROVIDER:"):
        arg = user_input.split(":", 1)[1].strip().lower()
        result = get_provider(arg)
        if not result:
            reply = "Invalid Arguement, Sir."
            print(f"\nJarvis: {reply}\n")
            speak(reply)
            continue
        reply = f"The current provider is {result}, Sir."
        print(f"\nJarvis: {reply}\n")
        speak(reply)
        continue

    if user_input.startswith("SWITCHPROVIDER:"):
        new_provider = user_input.split(":", 1)[1].strip().lower()
        new_history = switch_provider(new_provider, conversation_history)
        if not new_history:
            reply = "Provider doesn't exist, Sir."
            print(f"\nJarvis: {reply}\n")
            speak(reply)
            continue
        conversation_history = new_history
        save_memory(conversation_history)
        reply = f"{new_provider} is active, Sir."
        print(f"\nJarvis: {reply}\n")
        speak(reply)
        continue

    append_user(conversation_history, user_input)
    
    try:
        reply = get_reply(conversation_history["history"])
    except Exception as error:
        conversation_history["history"].pop()
        print(f"\nJarvis: An Error occured, Sir\n\n{error}\n")
        speak("An Error occured, Sir.")
        continue

    is_tool, tool_reply, tool_log = check_tools(reply)

    if is_tool:
        if tool_log:
            append_assistant(conversation_history, tool_log)
            save_memory(conversation_history)
        else:
            conversation_history["history"].pop()
        
        if tool_reply:
            print(f"\nJarvis: {tool_reply}\n")
            speak(tool_reply)
        continue

    append_assistant(conversation_history, reply)
    save_memory(conversation_history)
    print(f"\nJarvis: {reply}\n")
    speak(reply)
