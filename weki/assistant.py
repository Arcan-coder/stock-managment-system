"""WEKI - Natural Language Interface System (v1.0).

A lightweight voice+text assistant focused on Windows-friendly commands.
"""

from __future__ import annotations

import datetime as dt
import os
import subprocess
import webbrowser
from dataclasses import dataclass
from typing import Callable, Optional

import pyttsx3
import speech_recognition as sr


@dataclass
class IntentResult:
    handled: bool
    response: str
    should_exit: bool = False


class WekiAssistant:
    def __init__(self) -> None:
        self.engine = pyttsx3.init()
        self.recognizer = sr.Recognizer()
        self.handlers: list[Callable[[str], IntentResult]] = [
            self._open_apps,
            self._open_folder,
            self._search_web,
            self._tell_time_or_date,
            self._system_status,
            self._play_music,
            self._calculate,
            self._chat_and_help,
            self._exit,
        ]

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
            return ""
        except sr.RequestError:
            return "speech service unavailable"

    def handle_command(self, command: str) -> IntentResult:
        for handler in self.handlers:
            result = handler(command)
            if result.handled:
                return result

        return IntentResult(True, "I understood your words, but I do not know that command yet.")

    def run(self) -> None:
        self.speak("Hello, I am WEKI. How can I help you?")

        while True:
            command = self.listen()
            if not command:
                self.speak("Please repeat that.")
                continue

            result = self.handle_command(command)
            self.speak(result.response)

            if result.should_exit:
                break

    # ---- Intent handlers ----
    def _open_apps(self, command: str) -> IntentResult:
        app_map = {
            "open chrome": "start chrome",
            "open vlc": "start vlc",
            "open word": "start winword",
        }
        for phrase, cmd in app_map.items():
            if phrase in command:
                os.system(cmd)
                return IntentResult(True, f"Opening {phrase.replace('open ', '').title()}.")
        return IntentResult(False, "")

    def _open_folder(self, command: str) -> IntentResult:
        if command.startswith("open folder"):
            folder = command.replace("open folder", "", 1).strip() or os.path.expanduser("~")
            subprocess.run(["explorer", folder], check=False)
            return IntentResult(True, f"Opening folder {folder}.")
        return IntentResult(False, "")

    def _search_web(self, command: str) -> IntentResult:
        if "search" in command:
            query = command.replace("search", "", 1).strip()
            if not query:
                return IntentResult(True, "Tell me what to search for.")
            webbrowser.open(f"https://www.google.com/search?q={query}")
            return IntentResult(True, f"Showing results for {query}.")
        return IntentResult(False, "")

    def _tell_time_or_date(self, command: str) -> IntentResult:
        now = dt.datetime.now()
        if "time" in command:
            return IntentResult(True, f"The time is {now.strftime('%H:%M')}.")
        if "date" in command:
            return IntentResult(True, f"Today is {now.strftime('%A, %d %B %Y')}.")
        return IntentResult(False, "")

    def _system_status(self, command: str) -> IntentResult:
        if any(word in command for word in ["battery", "cpu", "system status"]):
            # Keep this dependency-light for v1.
            return IntentResult(
                True,
                "System status command is available. Install psutil to enable detailed battery and CPU info.",
            )
        return IntentResult(False, "")

    def _play_music(self, command: str) -> IntentResult:
        if "play music" in command:
            music_dir = os.path.join(os.path.expanduser("~"), "Music")
            if os.path.isdir(music_dir):
                subprocess.run(["explorer", music_dir], check=False)
                return IntentResult(True, "Opening your Music folder.")
            return IntentResult(True, "I could not find your Music folder.")
        return IntentResult(False, "")

    def _calculate(self, command: str) -> IntentResult:
        if command.startswith("calculate"):
            expression = command.replace("calculate", "", 1).strip()
            if not expression:
                return IntentResult(True, "Please provide a math expression.")
            try:
                result = eval(expression, {"__builtins__": {}}, {})
            except Exception:
                return IntentResult(True, "I could not calculate that expression.")
            return IntentResult(True, f"The answer is {result}.")
        return IntentResult(False, "")

    def _chat_and_help(self, command: str) -> IntentResult:
        knowledge = {
            "who are you": "I am WEKI, your voice and text assistant.",
            "study help": "I can help summarize topics and generate study questions for BTEC units.",
            "summarize": "Paste a paragraph in a text-enabled version and I will summarize it.",
            "generate ideas": "I can generate project ideas for school, church, and business use.",
        }

        for key, answer in knowledge.items():
            if key in command:
                return IntentResult(True, answer)

        return IntentResult(False, "")

    def _exit(self, command: str) -> IntentResult:
        if any(term in command for term in ["exit", "quit", "goodbye"]):
            return IntentResult(True, "Goodbye.", should_exit=True)
        return IntentResult(False, "")


if __name__ == "__main__":
    WekiAssistant().run()
