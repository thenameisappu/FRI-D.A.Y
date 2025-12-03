import asyncio
import subprocess
import re
try:
    from winrt.windows.devices import radios
except ModuleNotFoundError:
    import winsdk.windows.devices.radios as radios

def list_bluetooth_devices():

    cmd = [
        "powershell",
        "-Command",
        r"$devices = Get-PnpDevice -Class Bluetooth | "
        r"Where-Object { $_.FriendlyName -ne $null } | "
        r"Select-Object -ExpandProperty FriendlyName; "
        r"$devices = $devices | ForEach-Object { ($_ -split ' Avrcp Transport')[0] } | "
        r"ForEach-Object { ($_ -split ' Service')[0] } ; "
        r"$devices = $devices | Where-Object { $_ -notmatch 'Enumerator|Protocol|RFCOMM|Access|Gateway|NAP|Pse|Push' } ; "
        r"$devices | Sort-Object -Unique"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    devices = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    return devices


async def handle_bluetooth_logic(speak, listen_command, get_text_command):
    try:
        bt_radio = next(
            (r for r in await radios.Radio.get_radios_async() if r.kind == radios.RadioKind.BLUETOOTH), None
        )
        if not bt_radio:
            return speak("I could not find a Bluetooth adapter on this device.")

        if bt_radio.state == radios.RadioState.ON:
            speak("Bluetooth is currently ON. Would you like to turn it OFF? Please say yes or no.")
            answer = (listen_command() or get_text_command() or "").lower()
            if "yes" in answer or "off" in answer:
                await bt_radio.set_state_async(radios.RadioState.OFF)
                return speak("Bluetooth has been turned OFF.")
            speak("Okay, leaving Bluetooth on.")
        else:
            speak("Bluetooth is OFF. Turning it ON now.")
            if await bt_radio.set_state_async(radios.RadioState.ON) != radios.RadioAccessStatus.ALLOWED:
                return speak("I failed to turn on Bluetooth.")
            speak("Bluetooth is now ON. Scanning for devices...")
            await asyncio.sleep(2)

        devices = list_bluetooth_devices()
        if not devices:
            return speak("No Bluetooth devices found.")
        speak("I found the following Bluetooth devices:")
        for i, dev in enumerate(devices, 1):
            speak(f"{i}. {dev}")

        speak("Would you like to connect to one of these? Please say yes or no.")
        if "yes" not in (listen_command() or get_text_command() or "").lower():
            return speak("Okay, not connecting now.")

        speak("Please say the number of the Bluetooth device you'd like to connect to.")
        index_str = listen_command() or get_text_command() or ""
        try:
            index = int(index_str.strip()) - 1
            if 0 <= index < len(devices):
                device = devices[index]
                speak(f"You selected {device}. Attempting to connect...")

                success = False  # replace with real connection logic
                speak("Connected successfully." if success else "Connection attempt finished. Please pair manually if required.")
            else:
                speak("That number doesn't match any device.")
        except (ValueError, TypeError):
            speak("I didn't understand that number. Please try again.")

    except Exception:
        speak("Sorry, I encountered an error while managing Bluetooth.")
    
