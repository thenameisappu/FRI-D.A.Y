import os
from datetime import datetime

# Define the directory for history logs and ensure it exists
HISTORY_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'history'))
os.makedirs(HISTORY_DIR, exist_ok=True)
HISTORY_FILE = os.path.join(HISTORY_DIR, 'chat_log.txt')

def log_entry(speaker, message):
    """Logs a message from a speaker to the history file."""
    # Do not log empty commands or messages
    if not message or not message.strip():
        return
        
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_line = f"[{timestamp}] {speaker}: {message.strip()}\n"
    
    try:
        with open(HISTORY_FILE, 'a', encoding='utf-8') as f:
            f.write(log_line)
    except Exception as e:
        print(f"Error: Could not write to history log file. {e}")

