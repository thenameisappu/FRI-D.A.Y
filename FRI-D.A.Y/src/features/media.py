import os
import random
import pygame 
import pyautogui
import psutil
import time
import webbrowser
from src.core.voice import *
from AppOpener import open as open_app


class SpotifyPlayer:
    def __init__(self):
        self.initialized = False

    def is_spotify_running(self):
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'] and 'spotify' in proc.info['name'].lower():
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        return False

    def open_app(self):
        if self.initialized:
            return

        try:
            open_app("spotify")
            print("Trying to open Spotify app...")
        except Exception as e:
            print(f"Error launching Spotify app: {e}")
            return

        self.initialized = True

    def play(self):
        pyautogui.press("playpause")
        pyautogui.press("play")
        speak("Playing Spotify track")

    def pause(self):
        pyautogui.press("playpause")
        speak("Paused Spotify playback")

    def resume(self):
        pyautogui.press("playpause")
        speak("Resumed Spotify playback")

    def next_track(self):
        pyautogui.press("nexttrack")
        speak("Skipped to next Spotify track")

    def previous_track(self):
        pyautogui.press("prevtrack")
        speak("Went to previous Spotify track")


class MediaPlayer:
    """A generic controller for media applications like Spotify, VLC, etc."""
    def __init__(self, app_name):
        self.app_name = app_name.lower()
        self.initialized = False

    def is_app_running(self):
        """Check if the app is running via the process list."""
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'] and self.app_name in proc.info['name'].lower():
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        return False

    def open_app(self):
        """Open the app if it's not already running."""
        if self.initialized:
            return

        try:
            # Using match_closest for better reliability
            open_app(self.app_name, match_closest=True)
            print(f"Trying to open {self.app_name} app...")
            speak(f"Opening {self.app_name.title()}")
        except Exception as e:
            print(f"Error launching {self.app_name}: {e}")
            speak(f"Sorry, I couldn't open {self.app_name.title()}")
            return

        self.initialized = True

    def ensure_app_running(self):
        """Ensure the app is open before performing media actions."""
        if not self.is_app_running():
            self.open_app()

    def play(self):
        self.ensure_app_running()
        pyautogui.press("playpause")
        speak(f"Playing on {self.app_name.title()}")

    def pause(self):
        self.ensure_app_running()
        pyautogui.press("playpause")
        speak(f"Paused {self.app_name.title()}")

    def resume(self):
        self.ensure_app_running()
        pyautogui.press("playpause")
        speak(f"Resuming {self.app_name.title()}")

    def next_track(self):
        self.ensure_app_running()
        pyautogui.press("nexttrack")
        speak(f"Next track on {self.app_name.title()}")

    def previous_track(self):
        self.ensure_app_running()
        pyautogui.press("prevtrack")
        speak(f"Previous track on {self.app_name.title()}")


def handle_music(command):
    try:
        music_folder = r"C:\Users\User\Music"

        if not os.path.exists(music_folder):
            speak("Your Music folder was not found.")
            return

        music_files = [
            file for file in os.listdir(music_folder)
            if file.lower().endswith(".mp3")
        ]

        if not music_files:
            speak("No music files found.")
            return

        def ensure_mixer():
            if not pygame.mixer.get_init():
                pygame.mixer.init()

        def play_random():
            ensure_mixer()
            file_path = os.path.join(music_folder, random.choice(music_files))
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            speak(f"Playing {os.path.basename(file_path)}")

        if "play" in command and "change" not in command:
            play_random()

        elif "pause" in command:
            if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
                pygame.mixer.music.pause()
                speak("Music paused")
            else:
                speak("No music is currently playing")

        elif "resume" in command:
            ensure_mixer()
            pygame.mixer.music.unpause()
            speak("Music resumed")

        elif "stop" in command:
            if pygame.mixer.get_init():
                pygame.mixer.music.stop()
                speak("Music stopped")

        elif "change" in command or "next" in command:
            if pygame.mixer.get_init():
                pygame.mixer.music.stop()
            play_random()

        else:
            speak("Please specify play, pause, resume, stop or change.")

    except Exception as e:
        speak("Sorry, I encountered an error with the music operation Sir!")
        print(f"Media error: {e}")


