import time
import pyautogui
from AppOpener import open as open_app
from AppOpener import close as close_app
from src.core.voice import speak, listen_command, get_text_command

def send_message_whatsapp_app():
    try:
        speak("Opening WhatsApp to send your message.")
        open_app("whatsapp", match_closest=True, throw_error=True)
        time.sleep(6)

        speak("Who do you want to send a message to?")
        contact = ""
        contact = listen_command() or get_text_command()
        if not contact:
            speak("Sorry, I didn't catch the contact name.")
            return

        pyautogui.click(160, 100)  
        time.sleep(1)
        pyautogui.write(contact)
        time.sleep(1.5)
        pyautogui.press('down')
        time.sleep(1)
        pyautogui.press('enter')
        time.sleep(1)

        speak(f"What message would you like to send to {contact}?")
        message = ""
        message = listen_command() or get_text_command()
        if not message:
            speak("Message was empty. Cancelling.")
            return

        if message.strip().lower() == contact.strip().lower():
            speak("That sounds like the contact name. What message should I actually send?")
            message = listen_command() or get_text_command()
            if not message:
                speak("Still didn't catch a message. Cancelling.")
                return

        pyautogui.click(640, 718, clicks=2) 
        time.sleep(0.5)
        pyautogui.write(message)
        pyautogui.press('enter')

        speak(f"Message sent to {contact} successfully!")

        close_app("whatsapp", match_closest=True, throw_error=True)

    except Exception as e:
        speak(f"Failed to send message: {e}")
