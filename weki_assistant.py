import datetime
import os
import platform
import subprocess
import webbrowser

import pyttsx3
import speech_recognition as sr


class WekiAssistant:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.recognizer = sr.Recognizer()
        self.running = True

    def speak(self, text: str) -> None:
        print(f"WEKI: {text}")
        self.engine.say(text)
        self.engine.runAndWait()

    def listen(self) -> str:
        with sr.Microphone() as source:
            print("Listening...")
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = self.recognizer.listen(source)

        try:
            command = self.recognizer.recognize_google(audio)
            print(f"You: {command}")
            return command.lower().strip()
        except sr.UnknownValueError:
            self.speak("Sorry, I did not catch that.")
            return ""
        except sr.RequestError:
            self.speak("Speech service is unavailable right now.")
            return ""

    def open_app(self, app_name: str) -> bool:
        app_commands = {
            "chrome": "start chrome",
            "vlc": "start vlc",
            "word": "start winword",
        }

        cmd = app_commands.get(app_name)
        if not cmd:
            return False

        os.system(cmd)
        self.speak(f"Opening {app_name}")
        return True

    def system_status(self) -> None:
        try:
            import psutil

            cpu = psutil.cpu_percent(interval=1)
            battery = psutil.sensors_battery()
            battery_text = (
                f"Battery is at {battery.percent} percent"
                if battery
                else "Battery information is unavailable"
            )
            self.speak(f"CPU usage is {cpu} percent. {battery_text}.")
        except ImportError:
            self.speak(
                "System status requires psutil. Install it with pip install psutil."
            )

    def calculate(self, command: str) -> None:
        expression = command.replace("calculate", "", 1).strip()
        if not expression:
            self.speak("Please say an expression after calculate.")
            return

        safe_chars = set("0123456789+-*/(). ")
        if not set(expression) <= safe_chars:
            self.speak("I can only calculate basic math expressions.")
            return

        try:
            result = eval(expression, {"__builtins__": {}}, {})
            self.speak(f"The result is {result}")
        except Exception:
            self.speak("I could not calculate that expression.")

    def open_folder(self, command: str) -> None:
        path = command.replace("open folder", "", 1).strip(' "')
        if not path:
            self.speak("Please tell me the folder path.")
            return

        if os.path.isdir(path):
            os.startfile(path)
            self.speak(f"Opening folder {path}")
        else:
            self.speak("That folder does not exist.")

    def play_music(self, command: str) -> None:
        path = command.replace("play music", "", 1).strip(' "')
        if path and os.path.exists(path):
            os.startfile(path)
            self.speak("Playing music")
            return

        music_dir = os.path.join(os.path.expanduser("~"), "Music")
        if os.path.isdir(music_dir):
            os.startfile(music_dir)
            self.speak("Opening your Music folder")
        else:
            self.speak("Could not find your music folder.")

    def answer_simple_question(self, command: str) -> bool:
        if "date" in command:
            today = datetime.date.today().strftime("%A, %d %B %Y")
            self.speak(f"Today's date is {today}")
            return True

        if "time" in command:
            now = datetime.datetime.now().strftime("%H:%M")
            self.speak(f"The time is {now}")
            return True

        if "who are you" in command:
            self.speak("I am WEKI, your voice and text assistant.")
            return True

        return False

    def handle_command(self, command: str) -> None:
        if not command:
            return

        if "exit" in command or "quit" in command:
            self.speak("Goodbye")
            self.running = False
            return

        if "open chrome" in command:
            self.open_app("chrome")
            return

        if "open vlc" in command:
            self.open_app("vlc")
            return

        if "open word" in command:
            self.open_app("word")
            return

        if "search" in command:
            self.speak("What should I search?")
            query = self.listen()
            if query:
                webbrowser.open(f"https://www.google.com/search?q={query}")
                self.speak("Here are the results")
            return

        if "system status" in command or "battery" in command or "cpu" in command:
            self.system_status()
            return

        if command.startswith("open folder"):
            self.open_folder(command)
            return

        if command.startswith("play music"):
            self.play_music(command)
            return

        if command.startswith("calculate"):
            self.calculate(command)
            return

        if self.answer_simple_question(command):
            return

        self.speak("I can help with apps, search, date/time, system status, and simple math.")

    def run(self) -> None:
        if platform.system().lower() != "windows":
            self.speak("Warning: WEKI v1 commands are optimized for Windows.")

        self.speak("Hello, I am WEKI. How can I help you?")

        while self.running:
            command = self.listen()
            self.handle_command(command)


if __name__ == "__main__":
    assistant = WekiAssistant()
    assistant.run()
