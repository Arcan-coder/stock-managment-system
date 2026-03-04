"""WEKI - Natural Language Interface System (v1.0)

A basic voice + text assistant for Windows-focused command execution.

Features:
- Open common apps/folders
- Web search
- Tell time/date
- System status (battery + CPU)
- Play music from a folder
- Simple math calculations
- AI-style study/help prompts (rule-based placeholder)

Dependencies:
- speech_recognition
- pyttsx3
- psutil
- pyaudio (for microphone input)
"""

from __future__ import annotations

import datetime as dt
import os
import sys
import webbrowser
from dataclasses import dataclass

import psutil
import pyttsx3
import speech_recognition as sr


@dataclass
class AssistantConfig:
    name: str = "WEKI"
    use_voice_input: bool = True
    music_folder: str = os.path.expanduser("~/Music")


class WekiAssistant:
    def __init__(self, config: AssistantConfig) -> None:
        self.config = config
        self.engine = pyttsx3.init()
        self.recognizer = sr.Recognizer()

    def speak(self, text: str) -> None:
        print(f"{self.config.name}: {text}")
        self.engine.say(text)
        self.engine.runAndWait()

    def listen(self) -> str:
        if not self.config.use_voice_input:
            return input("You: ").strip().lower()

        with sr.Microphone() as source:
            print("Listening...")
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = self.recognizer.listen(source)

        try:
            command = self.recognizer.recognize_google(audio)
            print(f"You: {command}")
            return command.lower()
        except sr.UnknownValueError:
            self.speak("Sorry, I did not catch that.")
        except sr.RequestError:
            self.speak("Speech service is unavailable. Falling back to text input.")
            self.config.use_voice_input = False
        return ""

    def open_app(self, app: str) -> None:
        app_map = {
            "chrome": "start chrome",
            "vlc": "start vlc",
            "word": "start winword",
            "notepad": "start notepad",
        }
        cmd = app_map.get(app)
        if not cmd:
            self.speak(f"I don't know how to open {app} yet.")
            return

        os.system(cmd)
        self.speak(f"Opening {app}")

    def open_folder(self, folder_path: str) -> None:
        if not os.path.exists(folder_path):
            self.speak("That folder does not exist.")
            return
        os.startfile(folder_path)  # type: ignore[attr-defined]
        self.speak("Opening folder")

    def play_music(self) -> None:
        folder = self.config.music_folder
        if not os.path.isdir(folder):
            self.speak("Music folder not found.")
            return
        try:
            files = [f for f in os.listdir(folder) if f.lower().endswith((".mp3", ".wav", ".m4a"))]
            if not files:
                self.speak("No music files found.")
                return
            os.startfile(os.path.join(folder, files[0]))  # type: ignore[attr-defined]
            self.speak(f"Playing {files[0]}")
        except OSError:
            self.speak("Unable to play music right now.")

    def system_status(self) -> None:
        battery = psutil.sensors_battery()
        cpu_percent = psutil.cpu_percent(interval=0.4)

        if battery:
            plugged = "plugged in" if battery.power_plugged else "on battery"
            status = f"Battery is {battery.percent:.0f} percent and {plugged}."
        else:
            status = "Battery information is unavailable on this device."

        self.speak(f"{status} CPU usage is {cpu_percent:.0f} percent.")

    def calculate(self, expression: str) -> None:
        allowed_chars = set("0123456789+-*/(). ")
        if not expression or any(char not in allowed_chars for char in expression):
            self.speak("Please provide a valid math expression.")
            return
        try:
            result = eval(expression, {"__builtins__": {}}, {})
            self.speak(f"The result is {result}")
        except Exception:
            self.speak("I could not calculate that.")

    def respond_ai_prompt(self, prompt: str) -> None:
        # Placeholder for OpenAI API integration.
        canned = [
            "Great question. For WEKI 1.0, I can help with summaries and study tips.",
            "Try breaking your topic into key points, then review with quick quizzes.",
            "For BTEC study support: focus on definitions, examples, and past assignments.",
        ]
        self.speak(canned[hash(prompt) % len(canned)])

    def handle_command(self, command: str) -> bool:
        if not command:
            return True

        if "open chrome" in command:
            self.open_app("chrome")
        elif "open vlc" in command:
            self.open_app("vlc")
        elif "open word" in command:
            self.open_app("word")
        elif command.startswith("open folder"):
            path = command.replace("open folder", "", 1).strip() or os.path.expanduser("~")
            self.open_folder(path)
        elif "time" in command:
            now = dt.datetime.now().strftime("%H:%M")
            self.speak(f"The time is {now}")
        elif "date" in command:
            today = dt.datetime.now().strftime("%A, %d %B %Y")
            self.speak(f"Today is {today}")
        elif command.startswith("search"):
            query = command.replace("search", "", 1).strip()
            if not query:
                self.speak("What should I search?")
                query = self.listen()
            if query:
                webbrowser.open(f"https://www.google.com/search?q={query}")
                self.speak("Here are the search results")
        elif "system status" in command or "battery" in command or "cpu" in command:
            self.system_status()
        elif "play music" in command:
            self.play_music()
        elif command.startswith("calculate"):
            expression = command.replace("calculate", "", 1).strip()
            self.calculate(expression)
        elif "help me study" in command or "summarize" in command or "idea" in command:
            self.respond_ai_prompt(command)
        elif command in {"exit", "quit", "stop"}:
            self.speak("Goodbye")
            return False
        else:
            self.speak("I can help with apps, search, time/date, status, music, and calculations.")

        return True

    def run(self) -> None:
        self.speak(f"Hello, I am {self.config.name}. How can I help you?")
        while True:
            command = self.listen()
            if not self.handle_command(command):
                break


def parse_args() -> AssistantConfig:
    use_voice = "--text" not in sys.argv
    return AssistantConfig(use_voice_input=use_voice)


if __name__ == "__main__":
    assistant = WekiAssistant(parse_args())
    assistant.run()
