import time
import ctypes
import datetime
import os
import json
from collections import Counter
import psutil
import win32gui
import win32process
import traceback
import pygetwindow as gw


# --- Windows API setup ---
class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [('cbSize', ctypes.c_uint), ('dwTime', ctypes.c_uint)]


def get_active_app():
    """Return the currently active window's process name."""
    try:
        hwnd = win32gui.GetForegroundWindow()
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        process = psutil.Process(pid)
        # Let's return the window title, it's more user-friendly
        return win32gui.GetWindowText(hwnd) or process.name()
    except Exception:
        return "Unknown"

# --- Add this NEW function ---
def get_open_windows():
    """
    Gets a list of titles for all visible, non-minimized windows.
    """
    window_titles = []
    try:
        for window in gw.getAllWindows():
            # Filter for windows that have a title and are not minimized
            if window.title and window.visible and not window.isMinimized:
                if window.title not in window_titles: # Avoid duplicates
                    window_titles.append(window.title)
    except Exception as e:
        print(f"Error getting windows: {e}") # Or your log() function
        
    return window_titles

def get_idle_time():
    """Return system idle time in seconds (no keyboard/mouse input)."""
    last_input_info = LASTINPUTINFO()
    last_input_info.cbSize = ctypes.sizeof(LASTINPUTINFO)
    ctypes.windll.user32.GetLastInputInfo(ctypes.byref(last_input_info))
    millis = ctypes.windll.kernel32.GetTickCount() - last_input_info.dwTime
    return millis / 1000.0


def get_active_app():
    """Return the currently active window's process name."""
    try:
        hwnd = win32gui.GetForegroundWindow()
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        process = psutil.Process(pid)
        return process.name()
    except Exception:
        return "Unknown"


# --- Utility functions ---
def format_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


# --- Directory and File Setup ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DAILY_FILE = os.path.join(BASE_DIR, "daily_log.json")
WEEKLY_FILE = os.path.join(BASE_DIR, "weekly_log.json")
MONTHLY_FILE = os.path.join(BASE_DIR, "monthly_log.json")
APP_FILE = os.path.join(BASE_DIR, "app_usage.json")
LOG_FILE = os.path.join(BASE_DIR, "tracker_output.log")


def log(msg):
    """Append log messages with timestamps."""
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")


def load_json(path):
    """Load JSON data safely."""
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        log(f"⚠️ JSON decode error in {path}, resetting file.")
        return {}
    except Exception as e:
        log(f"❌ Failed to load JSON {path}: {e}")
        return {}


def save_json(path, data):
    """Save dictionary as formatted JSON."""
    try:
        with open(path, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        log(f"❌ Failed to save {path}: {e}")


def get_period_totals(logs):
    """Return daily, weekly, and monthly totals."""
    today = datetime.date.today()
    week_start = today - datetime.timedelta(days=today.weekday())
    month_start = today.replace(day=1)

    day_total = logs.get(today.strftime("%Y-%m-%d"), 0)
    week_total = sum(seconds for date, seconds in logs.items()
                     if datetime.date.fromisoformat(date) >= week_start)
    month_total = sum(seconds for date, seconds in logs.items()
                      if datetime.date.fromisoformat(date) >= month_start)
    return day_total, week_total, month_total


# --- Main Tracker ---
def track_screen_time(idle_threshold=300, check_interval=5):
    total_active_seconds = 0
    app_times = Counter()
    current_app = get_active_app()
    app_start_time = time.time()

    log("🚀 Screen Time Tracker started successfully (background mode).")

    try:
        while True:
            idle_time = get_idle_time()
            active_app = get_active_app()

            if idle_time < idle_threshold:
                total_active_seconds += check_interval

                # Track app switch
                if active_app != current_app:
                    duration = time.time() - app_start_time
                    app_times[current_app] += duration
                    current_app = active_app
                    app_start_time = time.time()

            # --- Update JSON every loop ---
            daily_logs = load_json(DAILY_FILE)
            today_str = datetime.date.today().strftime("%Y-%m-%d")
            daily_logs[today_str] = total_active_seconds
            save_json(DAILY_FILE, daily_logs)

            day_total, week_total, month_total = get_period_totals(daily_logs)
            save_json(WEEKLY_FILE, {"week_total_seconds": week_total, "formatted": format_time(week_total)})
            save_json(MONTHLY_FILE, {"month_total_seconds": month_total, "formatted": format_time(month_total)})

            # Save partial app usage every few minutes
            if int(time.time()) % 60 == 0:
                app_data = load_json(APP_FILE)
                app_data[today_str] = {app: int(sec) for app, sec in app_times.items()}
                save_json(APP_FILE, app_data)

            time.sleep(check_interval)

    except KeyboardInterrupt:
        log("⏹ Tracker manually stopped by user.")
    except Exception as e:
        log(f"💥 ERROR: {e}\n{traceback.format_exc()}")
    finally:
        app_times[current_app] += time.time() - app_start_time
        today_str = datetime.date.today().strftime("%Y-%m-%d")
        daily_logs = load_json(DAILY_FILE)
        daily_logs[today_str] = total_active_seconds
        save_json(DAILY_FILE, daily_logs)

        # Weekly & monthly totals
        day_total, week_total, month_total = get_period_totals(daily_logs)
        save_json(WEEKLY_FILE, {"week_total_seconds": week_total, "formatted": format_time(week_total)})
        save_json(MONTHLY_FILE, {"month_total_seconds": month_total, "formatted": format_time(month_total)})

        # Final app usage
        app_data = load_json(APP_FILE)
        app_data[today_str] = {app: int(sec) for app, sec in app_times.items()}
        save_json(APP_FILE, app_data)

        log(f"✅ JSON logs saved successfully.")
        log(f"📊 Final Totals → Day: {format_time(day_total)}, Week: {format_time(week_total)}, Month: {format_time(month_total)}")


# --- Auto start ---
if __name__ == "__main__":
    track_screen_time()
