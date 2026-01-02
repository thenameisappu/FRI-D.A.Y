import os
import cv2
import time
import pyautogui
import numpy as np
from datetime import datetime

SCREENSHOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'screenshots'))
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

def take_screenshot():
    from src.core.voice import speak
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"screenshot_{timestamp}.png"
        full_path = os.path.join(SCREENSHOT_DIR, filename)
        screenshot = pyautogui.screenshot()
        screenshot.save(full_path)
        speak(f"Screenshot saved as {filename}")
    except Exception as e:
        speak(f"Error taking screenshot: {str(e)}")

def record_screen(duration=10):
    from src.core.voice import speak
    try:
        screen_size = pyautogui.size()
        fourcc = cv2.VideoWriter_fourcc(*"XVID")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"screen_record_{timestamp}.avi"
        full_path = os.path.join(SCREENSHOT_DIR, filename)

        out = cv2.VideoWriter(full_path, fourcc, 20.0, screen_size)
        speak("Screen recording started")
        start_time = time.time()

        while time.time() - start_time < duration:
            img = pyautogui.screenshot()
            frame = cv2.cvtColor(np.array(img), cv2.COLOR_BGR2RGB)
            out.write(frame)

        out.release()
        speak(f"Screen recording saved as {filename}")
    except Exception as e:
        speak(f"Error during screen recording: {str(e)}")


