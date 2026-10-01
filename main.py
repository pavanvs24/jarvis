from core import handle_message
from voice import listen, speak, stop_speaking

speak("All Systems Optimal and Ready for Action, Sir. What we up to today ?")

while True:
    user_input = input("You: ")
    stop_speaking()

    if not user_input.strip():
        continue
    
    reply = handle_message(user_input)
    if reply:
        print(f"\nJarvis: {reply}\n")
        speak(reply)
