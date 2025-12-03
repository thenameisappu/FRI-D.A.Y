import os
import pyautogui
import subprocess
import socket
import psutil
import time
from datetime import datetime
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from src.core.voice import speak  

def get_ip_address():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80)) 
        ip_address = s.getsockname()[0]
        s.close()
        return ip_address
    except Exception as e:
        return f"Error fetching IP: {e}"

def tell_ip():
    ip = get_ip_address()
    speak(f"Your laptop's IP address is {ip}")
    return ip


class WindowsRadioControl:
    def hotspot(self) -> bool:
        try:
            pyautogui.hotkey('win', 'a')
            time.sleep(1)
            pyautogui.press('down', presses=2)  
            time.sleep(0.5)
            pyautogui.press('enter')  
            time.sleep(1)
            pyautogui.hotkey('win', 'a')
            return True
        except Exception as e:
            print("Error toggling Mobile Hotspot")
            return False

    def airplane_mode(self) -> bool:
        try:
            pyautogui.hotkey('win', 'a')
            time.sleep(1)
            pyautogui.press('right', presses=2)  
            time.sleep(0.5)
            pyautogui.press('enter')  
            time.sleep(1)
            pyautogui.hotkey('win', 'a')
            return True
        except Exception as e:
            print("Error toggling Airplane Mode")
            return False

    def open_accessibility(self) -> bool:
        try:
            pyautogui.hotkey('win', 'a')
            time.sleep(1)
            pyautogui.press('right', presses=2)  
            pyautogui.press('down', presses=2)   
            time.sleep(0.5)
            pyautogui.press('enter')  
            time.sleep(1)
            pyautogui.hotkey('win', 'a')
            return True
        except Exception as e:
            print("Error toggling Accessibility settings")
            return False
        
    def nigth_light(self) -> bool:
        try:
            pyautogui.hotkey('win', 'a')
            time.sleep(1)
            pyautogui.press('down')
            time.sleep(0.5)
            pyautogui.press('enter')
            time.sleep(1)
            pyautogui.hotkey('win', 'a')
            return True
        except Exception as e:
            print("Error toggling Nigth Light")
            return False

    def battery_saver(self) -> bool:
        try:
            pyautogui.hotkey('win', 'a')
            time.sleep(1)
            pyautogui.press('right')
            time.sleep(0.5)
            pyautogui.press('down', presses=2)  
            time.sleep(0.5)
            pyautogui.press('enter')  
            time.sleep(1)
            pyautogui.hotkey('win', 'a')
            return True
        except Exception as e:
            print("Error toggling Battery Saver")
            return False

    def open_projection(self) -> bool:
        try:
            pyautogui.hotkey('win', 'p')
            return True
        except Exception as e:
            print("Error opening projection")
            return False

    def open_cast(self) -> bool:
        try:
            pyautogui.hotkey('win', 'k')
            return True
        except Exception as e:
            print("Error opening cast")
            return False

class SystemMonitor:
    def get_cpu_info(self):
        return psutil.cpu_percent(interval=1)
    
    def get_memory_info(self):
        memory = psutil.virtual_memory()
        return {
            'total': self._bytes_to_gb(memory.total),
            'available': self._bytes_to_gb(memory.available),
            'used': self._bytes_to_gb(memory.used),
            'percent': memory.percent
        }
    
    def get_disk_info(self):
        disks = []
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disks.append({
                    'device': partition.device,
                    'mountpoint': partition.mountpoint,
                    'total': self._bytes_to_gb(usage.total),
                    'used': self._bytes_to_gb(usage.used),
                    'free': self._bytes_to_gb(usage.free),
                    'percent': usage.percent
                })
            except Exception:
                continue
        return disks
    
    def _bytes_to_gb(self, bytes):
        return round(bytes / (1024 ** 3), 2)
    
    def get_system_status(self):
        status = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'cpu': self.get_cpu_info(),
            'memory': self.get_memory_info(),
            'disk': self.get_disk_info()
        }
        return status

def adjust_brightness(action):
    try:
        current_brightness = int(subprocess.check_output([
            'powershell',
            '(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightness).CurrentBrightness'
        ]).strip())
        
        if action in ['up', 'increase', 'raise']:
            new_brightness = min(current_brightness + 10, 100)
        elif action in ['down', 'decrease', 'lower']:
            new_brightness = max(current_brightness - 10, 0)
        else:
            speak("Please say increase or decrease for brightness.")
            return

        subprocess.run([
            'powershell',
            f'(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,{new_brightness})'
        ], check=True)

        speak(f"Brightness set to {new_brightness} percent")
    except Exception as e:
        speak(f"Unable to adjust brightness: {str(e)}")


def adjust_volume(action):
    try:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, 1, None)
        volume = interface.QueryInterface(IAudioEndpointVolume)
        current_volume = volume.GetMasterVolumeLevelScalar()

        if action in ['up', 'increase', 'raise']:
            new_volume = min(current_volume + 0.1, 1.0)
        elif action in ['down', 'decrease', 'lower']:
            new_volume = max(current_volume - 0.1, 0.0)
        else:
            speak("Please say increase or decrease for volume.")
            return

        volume.SetMasterVolumeLevelScalar(new_volume, None)
        speak("Increasing volume" if action in ['up', 'increase', 'raise'] else "Decreasing volume")
    except Exception as e:
        speak(f"Unable to adjust volume: {str(e)}")

def check_battery():
    battery = psutil.sensors_battery()
    percent = battery.percent
    charging = battery.power_plugged
    status = f"Battery is at {percent}%"
    if charging:
        status += " and charging"
        if percent > 90:
            status += ". Please unplug the charger"
    else:
        status += " and not charging"
        if percent < 30:
            status += ". Please charge the laptop"
    speak(status)


