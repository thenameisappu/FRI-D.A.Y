import threading
import time
import pvporcupine
import pyaudio
import struct
import speech_recognition as sr
import pyttsx3
from src.core import animation
from src.utils import history_utils

engine = pyttsx3.init()
engine.setProperty('rate', 150)


def speak(text, is_exit=False):
    history_utils.log_entry("Friday", text)
    text_with_sir = text if is_exit else text + " Sir!"
    animation.update_text(text_with_sir)
    print("Friday: " + text_with_sir)

    engine = pyttsx3.init()
    engine.say(text_with_sir)
    engine.runAndWait()

    if not is_exit:
        time.sleep(3)
        animation.update_text("Listening...")


def get_text_command():
    animation.update_text("Type your command...")
    command = input("Type your command: ").strip()

    if command:
        history_utils.log_entry("User", command)

    animation.update_text(f"You commanded: {command}")
    time.sleep(1)
    return command


def listen_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        animation.update_text("Listening...")
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)

        try:
            audio = recognizer.listen(source, timeout=5)
            command = recognizer.recognize_google(audio).lower().strip()

            if command:
                history_utils.log_entry("User", command)

            print(f"You said: {command}")
            animation.update_text(f"You said: {command}")
            time.sleep(1)
            return command

        except (sr.UnknownValueError, sr.WaitTimeoutError):
            return ""

        except sr.RequestError:
            speak("Sorry, my speech service is down.")
            return ""


def recognize_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for command...")
        audio = recognizer.listen(source)

    try:
        command = recognizer.recognize_google(audio).lower().strip()
        if command:
            history_utils.log_entry("User", command)
        return command
    except sr.UnknownValueError:
        return ""


def start_voice_loop():
    porcupine = pvporcupine.create(keywords=["friday"])
    pa = pyaudio.PyAudio()
    stream = pa.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=porcupine.sample_rate,
        input=True,
        frames_per_buffer=porcupine.frame_length,
    )

    print("Listening for wake word 'Friday'...")
    animation.update_text("Say 'Friday' to wake me up")

    while True:
        pcm = stream.read(porcupine.frame_length)
        pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)
        keyword_index = porcupine.process(pcm)

        if keyword_index >= 0:
            print("Wake word detected!")
            speak("Yes, how can I help you?")
            command = recognize_command()

            if command:
                animation.update_text(f"You said: {command}")
