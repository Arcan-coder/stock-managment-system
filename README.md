# stock-managment-system
Automated Inventory & Supplier Management System is a web-based MVP that helps businesses manage products, suppliers, and stock levels while automatically generating and emailing daily, weekly, and monthly reports through a mobile-friendly dashboard with admin and staff roles.

## WEKI – Natural Language Interface System (Prototype)
This repository now includes a standalone `WEKI` assistant prototype in Python (`weki_assistant.py`).

### Features in v1
- Voice input with speech recognition
- Text-to-speech replies
- Open apps on Windows (`Chrome`, `VLC`, `Word`)
- Web search
- Date/time answers
- System status (CPU + battery via `psutil`)
- Open folder paths
- Play music folder/file
- Basic math calculations (`calculate 12 / 3`)

### Setup
1. Install Python 3.9+
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

> Note: On Windows, if `pyaudio` install fails, install a compatible wheel for your Python version.

### Run
```bash
python weki_assistant.py
```

### Example voice commands
- "Open Chrome"
- "What is the time?"
- "Search" (then say the query)
- "System status"
- "Calculate 21 * 4"
- "Open folder C:\\Users\\YourName\\Documents"
- "Exit"
