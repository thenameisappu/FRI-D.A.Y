import os
from datetime import datetime

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))

HISTORY_DIR = os.path.join(BASE_DIR, "resources", "history")
os.makedirs(HISTORY_DIR, exist_ok=True)

HISTORY_FILE = os.path.join(HISTORY_DIR, "chat_log.txt")


def log_entry(speaker, message):
    if not message or not message.strip():
        return

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] {speaker}: {message.strip()}\n"

    try:
        with open(HISTORY_FILE, "a", encoding="utf-8") as f:
            f.write(log_line)
    except Exception as e:
        print(f"History log error: {e}")
