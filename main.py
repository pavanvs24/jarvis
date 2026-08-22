from brain import get_response
from memory import load_memory, save_memory, append_user, append_assistant
from tool_handlers import check_tools
from voice import listen, speak

conversation_history = load_memory()

while True:
    #user_input = listen()
    #print(f"You: {user_input}")
    user_input = input("You: ")
    append_user(conversation_history, user_input)

    reply = get_response(conversation_history)

    is_tool, tool_reply, tool_log = check_tools(reply)
    if is_tool:
        if tool_log:
            append_assistant(conversation_history, tool_log)
            save_memory(conversation_history)
        if tool_reply:
            print(f"\nJarvis: {tool_reply}\n")
            speak(tool_reply)
        continue

    append_assistant(conversation_history, reply)
    save_memory(conversation_history)
    print(f"\nJarvis: {reply}\n")
    speak(reply)
