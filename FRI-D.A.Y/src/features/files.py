import os
import shutil
import logging
import time
from datetime import datetime
from src.core.voice import speak
from src.core.command import get_text_command, listen_command

logger = logging.getLogger(__name__)

def search_files(query, search_path=None, max_depth=5, file_extensions=None):
    found_files = []
    search_start = time.time()
    timeout = 30

    if search_path is None:
        drives = [d + ":\\" for d in "CDEFGHIJKLMNOPQRSTUVWXYZ" if os.path.exists(d + ":")]
        search_paths = drives
    else:
        search_paths = [search_path]

    try:
        for base_path in search_paths:
            for root, dirs, files in os.walk(base_path):
                if time.time() - search_start > timeout:
                    break

                depth = root.count(os.sep) - base_path.count(os.sep)
                if max_depth is not None and depth > max_depth:
                    continue

                dirs[:] = [d for d in dirs if not d.startswith('$') and d not in ['Windows', 'Program Files', 'Program Files (x86)', 'ProgramData']]

                for file in files:
                    if file_extensions and not any(file.lower().endswith(ext.lower()) for ext in file_extensions):
                        continue
                    if query.lower() in file.lower():
                        found_files.append(os.path.join(root, file))
                        if len(found_files) >= 20:
                            return found_files
    except Exception as e:
        logger.error(f"Search error: {e}")

    return found_files

def open_file(file_path):
    try:
        if os.path.exists(file_path):
            speak(f"Opening {os.path.basename(file_path)}")
            os.startfile(file_path)
            return True
        else:
            speak("File not found")
            return False
    except Exception as e:
        logger.error(f"Open error: {e}")
        speak("Sorry, I couldn't open that file")
        return False

def search_and_open_file(query, location=None):
    try:
        speak(f"Searching for {query}...")
        common_exts = [".doc", ".docx", ".pdf", ".txt", ".xls", ".xlsx", ".csv", ".ppt", ".pptx", ".jpg", ".png", ".mp3", ".mp4"]
        if "." in query:
            ext = query[query.rfind("."):]
            if len(ext) <= 5:
                common_exts.append(ext)

        common_dirs = [
            os.path.join(os.path.expanduser("~"), "Documents"),
            os.path.join(os.path.expanduser("~"), "Desktop"),
            os.path.join(os.path.expanduser("~"), "Downloads")
        ]

        files = []
        for loc in common_dirs:
            files.extend(search_files(query, loc, 2, common_exts))
            if files:
                break

        if not files:
            files = search_files(query, location, 5, common_exts)

        if files:
            files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            speak(f"Found {len(files)} files. Here are a few:")
            for i, file in enumerate(files[:5], 1):
                speak(f"{i}: {os.path.basename(file)}")

            speak("Say the number to open, or say 'none'")
            response = listen_command() or get_text_command()
            if response and response.isdigit():
                index = int(response) - 1
                if 0 <= index < len(files[:5]):
                    return open_file(files[index])
            elif response and response.lower() in ['none', 'no', 'cancel']:
                speak("Okay, not opening any file")
            else:
                speak("I didn't understand your response")
        else:
            speak("No files matched your query")
    except Exception as e:
        logger.error(f"Search-open error: {e}")
        speak("An error occurred while searching for files")
    return False

def handle_file_operation(command):
    try:
        if 'search' in command:
            speak("Which file would you like to search?")
            query = listen_command() or get_text_command()
            if query:
                files = search_files(query)
                if files:
                    speak(f"Found {len(files)} files:")
                    for file in files[:5]:
                        speak(os.path.basename(file))
                else:
                    speak("No matching files found")

        elif 'open' in command:
            speak("What file would you like to open?")
            query = listen_command() or get_text_command()
            if query:
                search_and_open_file(query)

        elif 'copy' in command or 'move' in command:
            op = 'copy' if 'copy' in command else 'move'
            speak(f"What file should I {op}?")
            query = listen_command() or get_text_command()
            if query:
                files = search_files(query)
                if files:
                    src = files[0]
                    speak(f"Where should I {op} it to?")
                    dst = listen_command() or get_text_command()
                    if dst:
                        if op == 'copy':
                            shutil.copy(src, dst)
                        else:
                            shutil.move(src, dst)
                        speak(f"Successfully {op}ed the file")
                else:
                    speak("No file found")

        elif 'delete' in command:
            speak("Which file should I delete?")
            query = listen_command() or get_text_command()
            if query:
                files = search_files(query)
                if files:
                    file_path = files[0]
                    speak(f"Delete {os.path.basename(file_path)}? Confirm yes or no.")
                    confirm = listen_command() or get_text_command()
                    if confirm and 'yes' in confirm.lower():
                        os.remove(file_path)
                        speak("File deleted")
                    else:
                        speak("Delete cancelled")
                else:
                    speak("No matching file found")
    except Exception as e:
        logger.error(f"Operation error: {e}")
        speak("Something went wrong during the file operation")

