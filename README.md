# WEKI – Natural Language Interface System

WEKI is a Python-based voice + text assistant designed for Windows first, with future expansion for Android and Web.

## Version 1.0 Features

- Open apps (`Chrome`, `VLC`, `Word`, `Notepad`)
- Search the web
- Tell time and date
- Read system status (battery and CPU)
- Open folders
- Play music from your Music directory
- Run simple math calculations
- Basic AI-style study/help responses (placeholder logic)

## Architecture

User Voice/Text → Speech Recognition → NLP/Intent Parsing → Command Execution → Response Generation → Text-to-Speech

## Tech Stack

- Python
- `speech_recognition`
- `pyttsx3`
- `psutil`
- `os`, `webbrowser`, `datetime`

## Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
```

> Windows note: microphone features usually require `pyaudio` to be installed correctly.

## Run WEKI

Voice mode (default):

```bash
python weki.py
```

Text mode (no microphone needed):

```bash
python weki.py --text
```

## Example Commands

- `open chrome`
- `open vlc`
- `open folder C:\\Users\\YourName\\Documents`
- `search Rwanda school AI assistant`
- `time`
- `date`
- `system status`
- `play music`
- `calculate 12 * (3 + 4)`
- `help me study`
- `exit`

## Future Roadmap

- Wake word support (`Hey WEKI`)
- OpenAI API integration for richer conversations and summaries
- GUI interface with chat history and status indicators
- Security features (voice authentication, encrypted logs)
