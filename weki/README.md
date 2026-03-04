# WEKI (v1.0)

WEKI is a Python-based natural language assistant with voice input/output for Windows.

## Features in this starter

- Voice recognition loop (`speech_recognition`)
- Offline speech output (`pyttsx3`)
- Basic intent handling for:
  - Open apps (Chrome, VLC, Word)
  - Search the web
  - Tell time/date
  - Open folders
  - Play music (opens Music folder)
  - Simple calculations (`calculate 10*5+2`)
  - Basic conversational/study-help replies

## Run

```bash
cd weki
pip install -r requirements.txt
python assistant.py
```

## Notes

- This version is focused on Windows commands (`start`, `explorer`).
- For richer system status (battery/CPU), add `psutil` and extend `_system_status`.
- For AI answers/summarization, add OpenAI API integration in `_chat_and_help`.
