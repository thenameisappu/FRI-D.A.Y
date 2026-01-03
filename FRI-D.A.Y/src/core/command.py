import os
import webbrowser
import subprocess
import shutil
import pyautogui
import random
import time
import keyboard
import psutil
import logging
import spotify
import asyncio
from datetime import datetime, timedelta
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from src.core.animation import *
from src.core.voice import *
from src.features.system import WindowsRadioControl, SystemMonitor ,adjust_brightness,adjust_volume,tell_ip
from src.features.timer import Timer, Stopwatch
from src.features.files import search_and_open_file,handle_file_operation
from src.features.media import handle_music,SpotifyPlayer,MediaPlayer
from src.features.notes import handle_note_operations
from src.features.weather import WeatherService
from src.features.application import open_app,close_app,maximize_window,minimize_window
from src.features.whatsapp import send_message_whatsapp_app
from src.features import camera   
from src.features.camera import photo_triggers 
from src.utils.screen_utils import take_screenshot, record_screen
from src.utils import wifi_utils
from src.utils import bluetooth_utils
from src.utils import history_utils
from src.utils import content_filter_utils as cfu
from src.utils import search_utils as su
from resources.screentime.screen_time_tracker import get_idle_time, get_active_app,get_open_windows
try:
    from winrt.windows.devices import radios
except ModuleNotFoundError:
    import winsdk.windows.devices.radios as radios



logger = logging.getLogger(__name__)
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


def execute_command(command):
    if not command:
        return True

    command = command.strip()
    radio_control = WindowsRadioControl()
    spotify_player = SpotifyPlayer()
    system_monitor = SystemMonitor()
    timer = Timer()
    stopwatch = Stopwatch()
    weather_service = WeatherService()

    capabilities = [
                "open, close, maximize and minimize any applications",
                "adjust volume and brightness",
                "take screenshots",
                "record the screen for a specified duration",
                "get time and date",
                "check battery status",
                "control WiFi and Bluetooth",
                "manage hotspot and airplane mode",
                "toggle night light and battery saver",
                "open accessibility, projection, and cast menus",
                "shut down, restart, lock, hibernate, or sleep the system",
                "close windows or the most recent window",
                "check weather for any city",
                "monitor system status (CPU, memory, and disk usage)",
                "check individual CPU status",
                "check memory status",
                "check disk status",
                "start and control timer",
                "start, stop, and reset stopwatch",
                "play, pause, resume, stop, and change music",
                "control Spotify playback (play, pause, resume, next, previous)",
                "search for files by name",
                "open any file on your computer",
                "create and manage notes",
                "read, list, and delete notes",
                "search anything on the web, YouTube, or Google",
                "send WhatsApp messages",
                "take a photo using the camera",
                "tell your IP address",
                "calculate mathematical expressions",
                "find files or documents",
                "handle file operations like search, copy, move, and delete"
            ]

    responses = [
                "Hey there! Great to hear from you.",
                "Hello! How can I be useful for you today?",
                "Hi! What's on your mind?",
                "Hey! Ready when you are.",
                "Yo! What can I do for you?",
                "Hello again! Always happy to help.",
                "Hey! How's it going?",
                "Hi there! Need a hand with something?",
                "Hey! What's up?",
                "Hi! I was just thinking about you!",
                "Hey there! Always nice to hear your voice.",
                "Hello! What shall we tackle today?",
                "Hey chief! What can I help you with?",
                "Hi there! How are you doing today?",
                "Hey! I'm all ears — what's next?",
                "Hello! Let's make things happen.",
                "Yo! Back for more productivity?",
                "Hey! What's on today's plan?",
                "Hi again! How can I assist this time?",
                "Hey there! Hope you're having a good one."
            ]


    try:
        
        if any(word in command for word in ['search file', 'copy file', 'move file', 'delete file']):
            handle_file_operation(command)
        elif 'open file' in command:
            speak("What file would you like to open?")
            query = listen_command() or get_text_command()
            if query:
                search_and_open_file(query)


        elif 'calculate' in command:
            speak("What would you like to calculate?")
            expression = listen_command() or get_text_command()
            if expression:
                try:
                    result = eval(expression)
                    speak(f"The result is {result}")
                except:
                    speak("Sorry, I couldn't calculate that expression")


        elif 'start timer' in command:
            timer.start()
        elif 'stop timer' in command:
            timer.stop()
        elif 'start stopwatch' in command:
            stopwatch.start()
        elif 'stop stopwatch' in command:
            stopwatch.stop()
        elif 'reset stopwatch' in command:
            stopwatch.reset()


        elif 'what are you' in command:
            speak("I am your Laptop assistant. You can call me Friday!")
        elif 'what is your name' in command:
            speak("You can call me Friday!")
        elif 'friday' in command:
            speak("I'm here")
        elif 'how are you' in command:
            speak("I'm doing great! Appreciate you asking.")


        elif 'weather' in command:
            speak("Which city would you like to know the weather for?")
            city = listen_command() or get_text_command()
            if city:
                weather = weather_service.get_current_weather(city)
                speak(f"Current weather in {city}: {weather['temperature']}°C, {weather['description']}, "
                      f"humidity {weather['humidity']}%, wind speed {weather['wind_speed']} meters per second")


        elif 'system status' in command:
            status = system_monitor.get_system_status()
            speak(f"CPU usage is currently {status['cpu']}%")
            memory = status['memory']
            speak(f"Memory status: Total {memory['total']} GB, "
                  f"Used {memory['used']} GB, "
                  f"Available {memory['available']} GB, "
                  f"Usage percentage {memory['percent']}%")
            
            for disk in status['disk']:
                speak(f"Disk {disk['device']} mounted at {disk['mountpoint']}: "
                      f"Total {disk['total']} GB, "
                      f"Used {disk['used']} GB, "
                      f"Free {disk['free']} GB, "
                      f"Usage percentage {disk['percent']}%")
            speak(f"This information was collected at {status['timestamp']}")
        elif 'cpu status' in command:
            cpu_usage = system_monitor.get_cpu_info()
            speak(f"Current CPU usage is {cpu_usage}%")
        elif 'memory status' in command:
            memory = system_monitor.get_memory_info()
            speak(f"Memory status: Total {memory['total']} GB, "
                  f"Used {memory['used']} GB, "
                  f"Available {memory['available']} GB, "
                  f"Usage percentage {memory['percent']}%")
        elif 'disk status' in command or 'disc status' in command:
            disks = system_monitor.get_disk_info()
            for disk in disks:
                speak(f"Disk {disk['device']} mounted at {disk['mountpoint']}: "
                      f"Total {disk['total']} GB, "
                      f"Used {disk['used']} GB, "
                      f"Free {disk['free']} GB, "
                      f"Usage percentage {disk['percent']}%")


        elif 'hotspot' in command:
            speak("Toggling Mobile Hotspot")
            radio_control.hotspot()
        elif 'airplane mode' in command:
            speak("Toggling Airplane Mode")
            radio_control.airplane_mode()
        elif 'nigth light' in command:
            speak("Toggling Nigth Light")
            radio_control.nigth_light()
        elif 'battery saver' in command:
            speak("Toggling Battery Saver")
            radio_control.battery_saver()
        elif 'accessibility' in command:
            speak("Opening Accessibility Settings")
            radio_control.open_accessibility()
        elif 'projection' in command:
            speak("Opening Projection Menu")
            radio_control.open_projection()
        elif 'cast' in command:
            speak("Opening Cast Menu")
            radio_control.open_cast()


        elif 'bluetooth' in command:
            asyncio.run(bluetooth_utils.handle_bluetooth_logic(speak, listen_command, get_text_command))

        elif 'wifi' in command or 'wi-fi' in command:
            asyncio.run(wifi_utils.handle_wifi_logic(speak, listen_command, get_text_command))


        elif 'find file' in command or 'find my file' in command:
            speak("What file are you looking for?")
            query = listen_command() or get_text_command()
            if query:
                search_and_open_file(query)


        elif 'open' in command:
            predefined_apps = {
                'notepad': 'notepad',
                'word': 'start winword',
                'excel': 'start excel',
                'powerpoint': 'start powerpnt',
                'outlook': 'start outlook'
                }
            for app, cmd in predefined_apps.items():
                if app in command:
                    speak(f"Opening {app.capitalize()}")
                    os.system(cmd)
                    return True
            
            if any(term in command for term in ['file', 'document', 'pdf', 'presentation', 'spreadsheet', 'image']):
                file_query = command.replace('open', '').strip()
                if file_query:
                    search_and_open_file(file_query)
                else:
                    speak("What file would you like to open?")
                    file_query = listen_command() or get_text_command()
                    if file_query:
                        search_and_open_file(file_query)
                return True

            elif 'browser' in command or 'youtube' in command:
                platform = 'YouTube' if 'youtube' in command else 'Google'
                speak(f"What would you like to search for on {platform}?")
                query = listen_command() or get_text_command()
                if query:
                    speak(f"Searching for {query}")
                    url = f'https://www.youtube.com/results?search_query={query}' if platform == 'YouTube' else f'https://www.google.com/search?q={query}'
                    webbrowser.open(url)
                return True

            elif "open" in command:
                app_name = command.replace("open", "").strip()
                if app_name:
                    open_app(app_name)
                else:
                    speak("Please specify the app to open.")
            
        elif 'close' in command:
            if 'window' in command:
                speak("Closing the current window")
                pyautogui.hotkey('alt', 'f4')
            elif 'recent' in command:
                speak("Closing the most recent window")
                pyautogui.hotkey('alt', 'tab')
                pyautogui.sleep(0.2)  
                pyautogui.hotkey('alt', 'f4')
            elif "close" in command:
                app_name = command.replace("close", "").strip()
                close_app(app_name)


        elif 'note' in command or any(k in command for k in ['create note', 'add to note', 'read note', 'list notes', 'delete note']):
            handle_note_operations(command)


        elif any(k in command for k in ["minimize", "minimise", "min "]):
            keyword = next(k for k in ["minimize", "minimise", "min"] if k in command)
            app_name = command.replace(keyword, "", 1).strip()
            minimize_window(app_name)

        elif any(k in command for k in ["maximize", "maximise", "max "]):
            keyword = next(k for k in ["maximize", "maximise", "max"] if k in command)
            app_name = command.replace(keyword, "", 1).strip()
            maximize_window(app_name)



        elif 'shutdown' in command:
            speak("Shutting down the system", is_exit=True)
            subprocess.run('shutdown /s /t 1', shell=True, check=True)
            return False
        elif 'restart' in command:
            speak("Restarting the system", is_exit=True)
            subprocess.run('shutdown /r /t 1', shell=True, check=True)
            return False
        elif 'lock' in command:
            speak("Locking the system")
            subprocess.run('rundll32.exe user32.dll,LockWorkStation', shell=True, check=True)
        elif 'hibernate' in command:
            speak("Hibernating the system")
            subprocess.run('shutdown /h', shell=True, check=True)
        elif 'sleep' in command:
            speak("Putting the system to sleep")
            subprocess.run('rundll32.exe powrprof.dll,SetSuspendState 0,1,0', shell=True, check=True)


        elif 'volume' in command:
            speak("Would you like to increase or decrease the volume?")
            direction = listen_command() or get_text_command()
            if direction:
                adjust_volume(direction)


        elif 'brightness' in command:
            speak("Would you like to increase or decrease the brightness?")
            direction = listen_command() or get_text_command()
            if direction:
                adjust_brightness(direction)


        elif 'screenshot' in command or 'snapshot' in command:
            take_screenshot()
        elif 'record screen' in command or 'screen record' in command:
            speak("How many seconds should I record the screen for?")
            duration_str = listen_command() or get_text_command()
            try:
                duration = int(duration_str)
                record_screen(duration=duration)
            except ValueError:
                speak("Invalid duration. Please say a number of seconds.")


        elif 'time' in command:
            speak(f"The current time is {datetime.now().strftime('%I:%M %p')}")


        elif 'date' in command:
            speak(f"Today's date is {datetime.now().strftime('%B %d, %Y')}")


        elif 'battery' in command:
            battery = psutil.sensors_battery()
            if battery:
                speak(f"Battery is at {battery.percent}%. {'Plugged in' if battery.power_plugged else 'Not plugged in'}")
            else:
                speak("Battery information not available")


        elif 'delete' in command:
                speak("Which recording would you like to delete?")
                filename = listen_command() or get_text_command()
                if filename:
                    speak("Delete functionality is not yet implemented")
                else:
                    speak("Please specify what you would like to delete")            


        elif 'what can you do' in command:
            for capability in capabilities:
                speak(f"I can {capability}.")
        

        elif 'send message on whatsapp' in command or 'send' in command or 'send whatsapp message' in command or 'open whatsapp to send' in command:
            send_message_whatsapp_app()


        elif any(word in command for word in ['play music', 'pause music', 'resume music', 'stop music']) or 'change music' in command or 'next song' in command:
            handle_music(command)

        elif "play on spotify" in command:
            spotify_player = SpotifyPlayer()
            spotify_player.open_app()
            spotify_player.play()
        elif "pause spotify" in command:
            spotify_player = SpotifyPlayer()
            spotify_player.pause()
        elif "resume spotify" in command:
            spotify_player = SpotifyPlayer()
            spotify_player.resume()
        elif "next spotify track" in command:
            spotify_player = SpotifyPlayer()
            spotify_player.next_track()
        elif "previous spotify track" in command:
            spotify_player = SpotifyPlayer()
            spotify_player.previous_track()

        elif command in ('play', 'pause', 'resume', 'next', 'previous'):
            known_media_players = ["spotify", "vlc", "itunes", "potplayer", "foobar2000", "wmplayer"]
            media_is_running = False
            try:
                for proc in psutil.process_iter(['name']):
                    if any(player in proc.info['name'].lower() for player in known_media_players):
                        media_is_running = True
                        break
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

            if not media_is_running:
                speak("No media player is running. Would you like me to open Spotify?")
                response = listen_command() or get_text_command()
                if response and 'yes' in response.lower():
                    spotify_player.play() 
                else:
                    speak("Okay, I won't open anything.")
            else:
                if command == 'play' or command == 'resume':
                    pyautogui.press("playpause")
                    speak("Playing")
                elif command == 'pause':
                    pyautogui.press("playpause")
                    speak("Pausing")
                elif command == 'next':
                    pyautogui.press("nexttrack")
                    speak("Next track")
                elif command == 'previous':
                    pyautogui.press("prevtrack")
                    speak("Previous track")


        elif any(trigger in command for trigger in photo_triggers):
            speak("Alright, Get ready.")
            speak("say cheese!")
            camera.take_photo_silent(speak_func=speak)
        

        elif "ip address" in command or "my ip" in command:
            tell_ip()


        elif 'okay' in command or 'thanks' in command or 'thank you' in command:
            speak("You're welcome!")


        elif 'chat history' in command or 'show my history' in command:
            speak("Opening your chat history.")
            try:
                os.startfile(history_utils.HISTORY_FILE)
            except Exception as e:
                speak("Sorry, I could not open the history file.")
                logger.error(f"Failed to open history file: {e}")
        

        elif 'hi' in command or 'hello' in command or 'hey' in command or 'yo' in command or 'sup' in command:
            speak(random.choice(responses))


        elif 'search document for' in command or 'find in document' in command:
            su.handle_document_search(speak, listen_command, get_text_command)


        elif 'search history for' in command or 'find in my history' in command:
            su.handle_history_search(speak, listen_command, get_text_command)
        
        
        elif 'screen time' in command or 'screen usage' in command or 'track my screen time' in command:
            idle_time_sec = get_idle_time()
            active_app = get_active_app()
            open_windows = get_open_windows()  
            
            other_windows = [title for title in open_windows if title != active_app and title]
        
            app_list_speech = ""
            if other_windows:
                # Join the first few app names for a clean spoken response
                other_apps_str = ", ".join(other_windows[:4])
                if len(other_windows) > 4:
                    other_apps_str += f", and {len(other_windows) - 4} others"
            
                app_list_speech = f" Other open windows include: {other_apps_str}."
            else:
                app_list_speech = " No other application windows are open."

            idle_minutes = int(idle_time_sec // 60)
            idle_seconds = int(idle_time_sec % 60)
        
            idle_speech = ""
            if idle_minutes > 0:
                idle_speech = f"You have been idle for {idle_minutes} minutes and {idle_seconds} seconds."
            else:
                idle_speech = f"You have been idle for {idle_seconds} seconds."

            # Combine all parts and speak
            speak(f"{idle_speech} "
                  f"The current active window is {active_app}."
                  f"{app_list_speech}") 


        elif any(key in command for key in ['filter', 'block', 'unblock']):
            if 'list' in command or 'show' in command:
                rules = cfu.list_rules()
                speak("Here are your current filters.")
                if rules.get("domains"): speak(f"Blocked domains are: {', '.join(rules['domains'])}")
                if rules.get("keywords"): speak(f"Blocked keywords are: {', '.join(rules['keywords'])}")
                if not rules.get("domains") and not rules.get("keywords"): speak("You have no active filters.")
            elif 'add' in command or 'block' in command:
                if 'domain' in command:
                    speak("Which domain to block?")
                    domain = listen_command() or get_text_command()
                    if domain and cfu.add_domain(domain): speak(f"Domain {domain} is now blocked.")
                    else: speak(f"Failed to add {domain}.")
                elif 'keyword' in command:
                    speak("What keyword to block?")
                    keyword = listen_command() or get_text_command()
                    if keyword and cfu.add_keyword(keyword): speak(f"Keyword {keyword} is now blocked.")
                    else: speak("Failed to add keyword.")
            elif 'remove' in command or 'unblock' in command:
                if 'domain' in command:
                    speak("Which domain to unblock?")
                    domain = listen_command() or get_text_command()
                    if domain and cfu.remove_domain(domain): speak(f"Unblocked {domain}.")
                    else: speak(f"Could not find a filter for {domain}.")
                elif 'keyword' in command:
                    speak("Which keyword to unblock?")
                    keyword = listen_command() or get_text_command()
                    if keyword and cfu.remove_keyword(keyword): speak(f"Unblocked {keyword}.")
                    else: speak(f"Could not find a filter for {keyword}.")


        elif 'exit' in command or 'quit' in command or 'goodbye' in command or 'bye' in command or 'stop' in command:
            speak("Goodbye!", is_exit=True)
            return False

        else:
            speak("I didn't catch that. Can you please clarify?")
    except Exception as e:
        logging.error(f"Error executing command '{command}': {e}")
        speak("Sorry, I encountered an error executing that command")
        
    return True

