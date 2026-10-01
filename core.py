from brain import get_reply, set_provider, get_provider, switch_provider, quick_start
from memory import load_memory, save_memory, append_user, append_assistant
from tool_handlers import check_tools

conversation_history = load_memory()

if not set_provider(conversation_history["provider"]):
    conversation_history = quick_start()
    save_memory(conversation_history)

def handle_message(user_input):
    global conversation_history

    if user_input.startswith("GETPROVIDER:"):
        arg = user_input.split(":", 1)[1].strip().lower()
        result = get_provider(arg)
        if not result:
            return "Invalid Arguement, Sir."
        return f"The current provider is {result}, Sir."

    if user_input.startswith("SWITCHPROVIDER:"):
        new_provider = user_input.split(":", 1)[1].strip().lower()
        new_history = switch_provider(new_provider, conversation_history)
        if not new_history:
            return "Provider doesn't exist, Sir."
        conversation_history = new_history
        save_memory(conversation_history)
        return f"{new_provider} is active, Sir."

    append_user(conversation_history, user_input)

    try:
        reply = get_reply(conversation_history["history"])
    except Exception as error:
        conversation_history["history"].pop()
        return f"An Error occured, Sir.\n\n{error}"

    is_tool, display, speech = check_tools(reply)

    if is_tool:
        append_assistant(conversation_history, reply.strip())
        save_memory(conversation_history)
        return display, speech

    append_assistant(conversation_history, reply)
    save_memory(conversation_history)
    return reply