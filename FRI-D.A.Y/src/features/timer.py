import threading
import time
import sys
from src.core.animation import *
from src.core.voice import *

class Timer:
    def __init__(self, animation_controller=None):
        self.animation_controller = animation_controller
        self.running = False
        self.thread = None
        self._stop_event = threading.Event()

    def _run_timer(self, duration):
        while duration and not self._stop_event.is_set():
            mins, secs = divmod(duration, 60)
            timer_display = f"{mins:02}:{secs:02}"
            print(f"Time remaining: {timer_display}")
            if self.animation_controller:
              self.animation_controller.update_text(f"Time remaining: {timer_display}")
            time.sleep(1)
            duration -= 1
        
        if not self._stop_event.is_set():
            speak("Time's up!")
        self.running = False

    def start(self):
        try:
            if self.running:
                speak("Timer is already running")
                return

            speak("How many seconds would you like to set the timer for?")
            duration_str = listen_command() or get_text_command()
            duration = int(duration_str)
            
            self.running = True
            self._stop_event.clear()
            speak(f"Timer set for {duration} seconds.")
            
            self.thread = threading.Thread(target=self._run_timer, args=(duration,))
            self.thread.daemon = True
            self.thread.start()

        except ValueError:
            speak("Invalid input. Please provide a number in seconds.")

    def stop(self):
        if self.running:
            self._stop_event.set()
            if self.thread:
                self.thread.join()
            self.running = False
            speak("Timer stopped")
        else:
            speak("No timer is running")

class Stopwatch:
    def __init__(self):
        self.start_time = None
        self.running = False
        self.elapsed_time = 0
        self.thread = None

    def _run(self):
        while self.running:
            self.elapsed_time = time.time() - self.start_time
            mins, secs = divmod(int(self.elapsed_time), 60)
            milliseconds = int((self.elapsed_time - int(self.elapsed_time)) * 1000)
            sys.stdout.write(f"\rStopwatch running: {mins:02}:{secs:02}.{milliseconds:03} ")
            sys.stdout.flush()
            time.sleep(0.01)

    def start(self):
        if not self.running:
            self.start_time = time.time() - self.elapsed_time
            self.running = True
            self.thread = threading.Thread(target=self._run, daemon=True)
            self.thread.start()
            time.sleep(0.05)  
        else:
            print("\nStopwatch is already running.")

    def stop(self):
        if self.running:
            self.running = False
            self.thread.join()
            mins, secs = divmod(int(self.elapsed_time), 60)
            milliseconds = int((self.elapsed_time - int(self.elapsed_time)) * 1000)
            print(f"\nStopwatch stopped at: {mins:02}:{secs:02}.{milliseconds:03}")
            print(f"Ended time: {self.elapsed_time:.3f} seconds.\n")
        else:
            print("\nStopwatch is not running.")

    def reset(self):
        self.start_time = None
        self.running = False
        self.elapsed_time = 0
        print("\nStopwatch reset.")

timer = Timer()
stopwatch = Stopwatch()
