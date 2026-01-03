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
        contact = listen_command() or get_text_command()
        if not contact:
            speak("I didn't catch the contact name. Cancelling.")
            return

        pyautogui.hotkey("ctrl", "f")
        time.sleep(0.5)
        pyautogui.write(contact, interval=0.05)
        time.sleep(1)

        pyautogui.press("enter")
        time.sleep(2)

        speak(f"What message would you like to send to {contact}?")
        message = listen_command() or get_text_command()
        if not message or not message.strip():
            speak("Message was empty. Cancelling.")
            return

        if message.strip().lower() == contact.strip().lower():
            speak("That sounded like the contact name. Please say the message again.")
            message = listen_command() or get_text_command()
            if not message:
                speak("Still no message. Cancelling.")
                return

        pyautogui.write(message, interval=0.03)
        pyautogui.press("enter")
        time.sleep(0.5)

        speak(f"Message sent to {contact} successfully.")

        close_app("whatsapp", match_closest=True, throw_error=True)

    except Exception as e:
        speak("I couldn't send the WhatsApp message.")
        print("WhatsApp error:", e)
