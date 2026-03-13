"""
forecast_service.py
-------------------
Predict tomorrow's disruption risk using weather forecast
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")

BASE_URL = "https://api.openweathermap.org/data/2.5/forecast"


def get_tomorrow_weather(city):

    url = f"{BASE_URL}?q={city}&appid={API_KEY}&units=metric"

    response = requests.get(url)

    data = response.json()

    # forecast list contains 3-hour intervals
    tomorrow_data = data["list"][8]   # roughly 24 hours later

    weather = {
        "temperature": tomorrow_data["main"]["temp"],
        "rainfall": tomorrow_data.get("rain", {}).get("3h", 0),
        "wind_speed": tomorrow_data["wind"]["speed"],
        "humidity": tomorrow_data["main"]["humidity"]
    }

    return weather


def predict_tomorrow_risk(city):

    weather = get_tomorrow_weather(city)

    risk = "LOW"

    if weather["rainfall"] > 30:
        risk = "HIGH"

    if weather["temperature"] > 42:
        risk = "HIGH"

    print("\nTomorrow Weather Prediction")
    print(weather)

    print("\nPredicted Risk Level:", risk)


if __name__ == "__main__":

    predict_tomorrow_risk("Mumbai,IN")