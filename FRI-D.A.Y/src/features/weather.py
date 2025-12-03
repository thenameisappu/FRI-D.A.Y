import random
from src.core.voice import *

class WeatherService:
    def get_current_weather(self, city):
        mock_data = {
            "temperature": random.randint(15, 35),
            "feels_like": random.randint(14, 34),
            "humidity": random.randint(40, 90),
            "description": random.choice(["Clear sky", "Cloudy", "Rainy", "Sunny"]),
            "wind_speed": round(random.uniform(1.0, 5.0), 2)
        }
        return mock_data
