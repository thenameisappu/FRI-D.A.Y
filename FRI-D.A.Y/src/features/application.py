from AppOpener import open as open_app_opener, close as close_app_opener
from src.core.voice import speak
import pygetwindow as gw
import contextlib
import io

# Suppress stdout context
@contextlib.contextmanager
def suppress_stdout():
    with contextlib.redirect_stdout(io.StringIO()):
        yield

# Function to open an app silently
def open_app(name):
    try:
        with suppress_stdout():
            open_app_opener(name, match_closest=True, throw_error=True)
        speak(f"Opened {name}")
    except Exception as e:
        speak(f"Sorry, couldn't open {name}. Error: {e}")

# Function to close an app silently
def close_app(name):
    try:
        with suppress_stdout():
            close_app_opener(name, match_closest=True, throw_error=True)
        speak(f"Closed {name}")
    except Exception as e:
        speak(f"Sorry, couldn't close {name}. Error: {e}")

# Function to minimize a window (only if running)
def minimize_window(app_name):
    windows = gw.getWindowsWithTitle(app_name)
    if windows:
        windows[0].minimize()
        speak(f"'{app_name}' minimized successfully.")
    else:
        speak(f"Could not find a window with title containing '{app_name}'.")

# Function to maximize a window (only if running)
def maximize_window(app_name):
    windows = gw.getWindowsWithTitle(app_name)
    if windows:
        windows[0].maximize()
        speak(f"'{app_name}' maximized successfully.")
    else:
        speak(f"Could not find a window with title containing '{app_name}'.")

