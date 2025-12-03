import asyncio
import subprocess
import re
import os
import time
try:
    from winrt.windows.devices import radios
except ModuleNotFoundError:
    import winsdk.windows.devices.radios as radios


def list_wifi_networks():
    networks = {}
    try:
        output = subprocess.check_output(
            ["netsh", "wlan", "show", "networks", "mode=BSSID"],
            text=True,
            stderr=subprocess.DEVNULL
        )
        network_blocks = output.strip().split("SSID")[1:]
        for block in network_blocks:
            SSID_match = re.search(r": (.+)", block)
            auth_match = re.search(r"Authentication\s*: (.+)", block)
            encr_match = re.search(r"Encryption\s*: (.+)", block)
            if SSID_match and auth_match and encr_match:
                SSID = SSID_match.group(1).strip()
                networks[SSID] = {
                    "auth": auth_match.group(1).strip(),
                    "encr": encr_match.group(1).strip()
                }
    except subprocess.CalledProcessError:
        pass 
    return networks


def create_wifi_profile(SSID, password, authentication, encryption):
    auth_map = {
        "WPA2-Personal": "WPA2PSK",
        "WPA3-Personal": "WPA3SAE",
        "Open": "open"
    }
    auth_str = auth_map.get(authentication, "WPA2PSK")
    encr_str = "AES" if "CCMP" in encryption else "TKIP"

    SSID_xml = SSID.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    password_xml = password.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

    key_block = f"""
        <sharedKey>
            <keyType>passPhrase</keyType>
            <protected>false</protected>
            <keyMaterial>{password_xml}</keyMaterial>
        </sharedKey>""" if auth_str != "open" else ""

    profile = f"""<?xml version="1.0"?>
<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
    <name>{SSID_xml}</name>
    <SSIDConfig><SSID><name>{SSID_xml}</name></SSID></SSIDConfig>
    <connectionType>ESS</connectionType>
    <connectionMode>manual</connectionMode>
    <MSM>
        <security>
            <authEncryption>
                <authentication>{auth_str}</authentication>
                <encryption>{encr_str}</encryption>
                <useOneX>false</useOneX>
            </authEncryption>{key_block}
        </security>
    </MSM>
</WLANProfile>"""

    with open("wifi_profile.xml", "w") as f:
        f.write(profile)


def connect_to_wifi(SSID, password, auth, encr):
    create_wifi_profile(SSID, password, auth, encr)
    try:
        # Add the profile BEFORE trying to connect
        subprocess.run(["netsh", "wlan", "add", "profile", f'filename="wifi_profile.xml"'],
                       check=True, capture_output=True)

        subprocess.run(["netsh", "wlan", "connect", f'name={SSID}'],
                       check=True, capture_output=True)

        start_time = time.time()
        while time.time() - start_time < 15:
            result = subprocess.check_output(
                ["netsh", "wlan", "show", "interfaces"],
                text=True,
                stderr=subprocess.DEVNULL
            )
            if re.search(rf'^\s*SSID\s*:\s*{re.escape(SSID)}\s*$', result, re.MULTILINE) and \
               re.search(r"^\s*State\s*:\s*connected\s*$", result, re.MULTILINE | re.IGNORECASE):
                return True
            time.sleep(1)
    except subprocess.CalledProcessError as e:
        print("Connection error:", e)
    finally:
        if os.path.exists("wifi_profile.xml"):
            os.remove("wifi_profile.xml")
    return False


async def handle_wifi_logic(speak, listen_command, get_text_command):
    try:
        wifi_radio = next(
            (r for r in await radios.Radio.get_radios_async() if r.kind == radios.RadioKind.WI_FI), None
        )
        if not wifi_radio:
            return speak("I could not find a Wi-Fi adapter on this device.")

        if wifi_radio.state == radios.RadioState.ON:
            speak("Wi-Fi is currently ON. Would you like to turn it OFF? Please say yes or no.")
            answer = (listen_command() or get_text_command() or "")
            if "yes" in answer or "off" in answer:
                await wifi_radio.set_state_async(radios.RadioState.OFF)
                return speak("Wi-Fi has been turned OFF.")
            speak("Okay, leaving Wi-Fi on.")
        else:
            speak("Wi-Fi is OFF. Turning it ON now.")
            if await wifi_radio.set_state_async(radios.RadioState.ON) != radios.RadioAccessStatus.ALLOWED:
                return speak("I failed to turn on the Wi-Fi.")
            speak("Wi-Fi is now ON. Scanning for networks...")
            await asyncio.sleep(3)

        networks = list_wifi_networks()
        if not networks:
            return speak("No Wi-Fi networks were found nearby.")

        SSID_list = list(networks.keys())
        speak("I found the following Wi-Fi networks.")
        for i, SSID in enumerate(SSID_list, 1):
            speak(f"{i}. {SSID}")

        speak("Would you like to connect to one of these? Please say yes or no.")
        if "yes" not in (listen_command() or get_text_command() or ""):
            return speak("Okay, not connecting now.")

        speak("Please say the number of the Wi-Fi network you'd like to connect to.")
        index_str = listen_command() or get_text_command() or ""
        try:
            index = int(index_str.strip()) - 1
            if 0 <= index < len(SSID_list):
                SSID = SSID_list[index]
                details = networks[SSID]

                if details["auth"] == "open":
                    password = ""
                    speak(f"Selected open network {SSID}. Connecting now...")
                else:
                    speak(f"You selected {SSID}. Please say the password.")
                    password = listen_command() or get_text_command()
                    if not password:
                        return speak("No password provided. Cancelling connection.")

                speak(f"Trying to connect to {SSID}...")
                success = connect_to_wifi(SSID, password, details["auth"], details["encr"])
                speak("Connected successfully." if success else "Connection failed.")
            else:
                speak("That number doesn't match any network.")
        except (ValueError, TypeError):
            speak("I didn't understand that number. Please try again.")
    except Exception:
        speak("Sorry, I encountered an error while managing Wi-Fi.")
