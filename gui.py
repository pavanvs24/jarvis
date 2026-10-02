import queue
import threading
import customtkinter as ctk

from core import handle_message
from voice import speak, stop_speaking

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

GREETING = "All Systems Optimal and Ready for Action, Sir. What we up to today ?"


class JarvisApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Jarvis")
        self.geometry("760x620")
        self.minsize(480, 400)

        self.results = queue.Queue()   # worker thread -> window
        self.busy = False

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # chat area
        self.chat = ctk.CTkTextbox(self, wrap="word", font=("Segoe UI", 14), state="disabled")
        self.chat.grid(row=0, column=0, padx=12, pady=(12, 4), sticky="nsew")
        self.chat.tag_config("user", foreground="#6cb6ff")
        self.chat.tag_config("jarvis", foreground="#7ee787")

        # status line
        self.status = ctk.CTkLabel(self, text="", anchor="w", text_color="gray")
        self.status.grid(row=1, column=0, padx=16, sticky="ew")

        # input row
        bottom = ctk.CTkFrame(self, fg_color="transparent")
        bottom.grid(row=2, column=0, padx=12, pady=(4, 12), sticky="ew")
        bottom.grid_columnconfigure(0, weight=1)

        self.entry = ctk.CTkEntry(bottom, placeholder_text="Ask anything", height=38)
        self.entry.grid(row=0, column=0, padx=(0, 8), sticky="ew")
        self.entry.bind("<Return>", lambda e: self.send())

        self.send_btn = ctk.CTkButton(bottom, text="Send", width=80, height=38, command=self.send)
        self.send_btn.grid(row=0, column=1, padx=(0, 8))

        self.stop_btn = ctk.CTkButton(bottom, text="Stop", width=80, height=38,
                                      fg_color="#b33a3a", hover_color="#8f2e2e",
                                      command=stop_speaking)
        self.stop_btn.grid(row=0, column=2)

        # Esc stops speech while this window is focused
        self.bind("<Escape>", lambda e: stop_speaking())
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.entry.focus()
        self.add_message("Jarvis", GREETING, "jarvis")
        speak(GREETING)
        self.after(100, self.poll_results)

    def add_message(self, sender, text, tag):
        self.chat.configure(state="normal")
        self.chat.insert("end", f"{sender}: ", tag)
        self.chat.insert("end", f"{text}\n\n")
        self.chat.configure(state="disabled")
        self.chat.see("end")

    def set_busy(self, busy):
        self.busy = busy
        self.send_btn.configure(state="disabled" if busy else "normal")
        self.status.configure(text="Jarvis is thinking..." if busy else "")

    def send(self):
        text = self.entry.get().strip()
        if not text or self.busy:
            return
        stop_speaking()
        self.entry.delete(0, "end")
        self.add_message("You", text, "user")
        self.set_busy(True)
        threading.Thread(target=self.worker, args=(text,), daemon=True).start()

    def worker(self, text):
        # runs off the main thread so the window never freezes
        try:
            result = handle_message(text)
        except Exception as error:
            result = (f"An Error occured, Sir.\n\n{error}", "An Error occured, Sir.")
        self.results.put(result)

    def poll_results(self):
        try:
            result = self.results.get_nowait()
        except queue.Empty:
            pass
        else:
            if isinstance(result, str):
                display = speech = result
            else:
                display, speech = result
            if display:
                self.add_message("Jarvis", display, "jarvis")
            if speech:
                speak(speech)
            self.set_busy(False)
            self.entry.focus()
        self.after(100, self.poll_results)

    def on_close(self):
        stop_speaking()
        self.destroy()

if __name__ == "__main__":
    JarvisApp().mainloop()
