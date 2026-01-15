import pyautogui
import time
from src.core.voice import speak, listen_command, get_text_command

# -----------------------------
# Keyboard Access
# -----------------------------
KEY_MAP = {
    "control": "ctrl",
    "ctrl": "ctrl",

    "windows": "win",
    "window": "win",
    "win": "win",

    "escape": "esc",
    "esc": "esc",
    "esacpe": "esc",   

    "caps": "capslock",
    "capslock": "capslock",

    "num": "numlock",
    "numlock": "numlock",
    "numeric": "numlock",
    "numeric lock": "numlock",
    "number lock": "numlock",

    "function": None,
    "fn": None,

    "return": "enter"
}

def press_keys(raw_keys):
    try:
        keys = []

        for k in raw_keys:
            k = k.lower().strip()
            mapped = KEY_MAP.get(k, k)

            # Skip unsupported keys like FN
            if mapped is None:
                speak(f"{k} key cannot be controlled")
                return

            keys.append(mapped)

        if not keys:
            speak("No valid keys detected")
            return

        time.sleep(0.2)
        pyautogui.hotkey(*keys)
        speak(f"Pressed {' '.join(keys)}")

    except Exception as e:
        speak("Keyboard action failed")
        print("Keyboard error:", e)


# -----------------------------
# Type With Command
# -----------------------------
def type_text(text: str, interval=0.05):
    try:
        pyautogui.write(text, interval=interval)
        speak("Text typed successfully")
    except Exception as e:
        speak("Failed to type text")
        print(e)


def handle_typing():
    speak("What should I type?")
    text = listen_command() or get_text_command()
    if text:
        type_text(text)
    else:
        speak("No text received")


# -----------------------------
# Search Bar Access
# -----------------------------
def get_active_app_title():
    try:
        win = gw.getActiveWindow()
        if win and win.title:
            return win.title.lower()
    except Exception:
        pass
    return ""


def open_active_app_search():
    try:
        title = get_active_app_title()
        time.sleep(0.2)
        if any(x in title for x in ["chrome", "edge", "firefox", "brave", "opera"]):
            pyautogui.hotkey("ctrl", "l")
            speak("Browser search opened")
            return
        if "explorer" in title:
            pyautogui.hotkey("ctrl", "f")
            speak("File search opened")
            return
        if "settings" in title:
            pyautogui.hotkey("ctrl", "f")
            speak("Settings search opened")
            return
        if any(x in title for x in ["code", "visual studio"]):
            pyautogui.hotkey("ctrl", "f")
            speak("Editor search opened")
            return
        if "whatsapp" in title:
            pyautogui.hotkey("ctrl", "f")
            speak("WhatsApp search opened")
            return
        pyautogui.hotkey("ctrl", "f")
        speak("App search opened")

    except Exception as e:
        speak("Unable to open search in this app")
        print("Search error:", e)


def search_in_active_app():
    open_active_app_search()
    time.sleep(0.3)

    speak("What should I search?")
    query = listen_command() or get_text_command()
    if query:
        pyautogui.write(query, interval=0.05)
        pyautogui.press("enter")
    else:
        speak("Search cancelled")
