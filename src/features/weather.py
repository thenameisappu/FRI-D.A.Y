import os
import requests
from dotenv import load_dotenv
from src.core.voice import *

load_dotenv()
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

class WeatherService:
    def get_current_weather(self, city):
        if not OPENWEATHER_API_KEY:
            speak("Weather API key is missing. Please add it to your .env file.")
            return None

        try:
            params = {
                "q": city,
                "appid": OPENWEATHER_API_KEY,
                "units": "metric"   # Celsius; use "imperial" for Fahrenheit
            }
            response = requests.get(BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            return {
                "temperature":  round(data["main"]["temp"]),
                "feels_like":   round(data["main"]["feels_like"]),
                "humidity":     data["main"]["humidity"],
                "description":  data["weather"][0]["description"].capitalize(),
                "wind_speed":   data["wind"]["speed"]
            }

        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response else "?"
            if status == 404:
                speak(f"Sorry, I couldn't find weather data for {city}.")
            elif status == 401:
                speak("Weather API key is invalid. Please check your key.")
            else:
                speak(f"Weather request failed with status {status}.")
            return None

        except requests.exceptions.ConnectionError:
            speak("No internet connection. Unable to fetch weather.")
            return None

        except requests.exceptions.Timeout:
            speak("Weather request timed out. Please try again.")
            return None

        except Exception as e:
            speak("An unexpected error occurred while fetching the weather.")
            print(f"Weather error: {e}")
            return None