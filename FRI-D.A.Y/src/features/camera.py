import cv2
import os
from datetime import datetime

photo_triggers = ["take photo", "click picture", "capture photo", "take a picture", "click photo", "snap photo", "cheese", "say cheese", "smile", "smile please", "let's take a picture", "capture this moment", "photo time", "take my photo"]

PHOTO_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'Camera Roll'))
os.makedirs(PHOTO_DIR, exist_ok=True)

def take_photo_silent(camera_index=0, speak_func=None):
    speak = speak_func or (lambda msg: print(f"[Friday] {msg}"))

    filename = datetime.now().strftime("photo_%Y%m%d_%H%M%S.jpg")
    filepath = os.path.join(PHOTO_DIR, filename)

    cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW if os.name == 'nt' else 0)
    if not cap.isOpened():
        speak("Unable to open the camera.")
        return None

    for _ in range(5):
        ret, frame = cap.read()


    if ret and frame is not None and frame.size > 0:
        success = cv2.imwrite(filepath, frame)
        if success:
            speak(f"Photo saved as: {filename}")
            return filename
        else:
            speak("Error: Could not save the image file.")
            return None
    else:
        speak("Failed to capture image.")
        return None
    cap.release()
