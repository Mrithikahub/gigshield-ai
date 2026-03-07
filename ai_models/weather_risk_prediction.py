import requests
import joblib

# ----------------------------
# CONFIGURATION
# ----------------------------

API_KEY = "daece42502a7cf46cd53fa594fd62f46"
CITY = "Chennai"

# ----------------------------
# FETCH WEATHER DATA
# ----------------------------

url = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"

response = requests.get(url)
data = response.json()

# ----------------------------
# ERROR CHECK
# ----------------------------

if response.status_code != 200:
    print("API ERROR")
    print(data)
    exit()

# ----------------------------
# EXTRACT WEATHER DATA
# ----------------------------

temperature = data["main"]["temp"]
wind_speed = data["wind"]["speed"]

rainfall = 0
if "rain" in data:
    rainfall = data["rain"].get("1h", 0)

print("\nWeather Data")
print("Temperature:", temperature)
print("Rainfall:", rainfall)
print("Wind Speed:", wind_speed)

# ----------------------------
# SIMULATED FEATURES
# ----------------------------

aqi = 200
traffic_index = 60
flood_risk = 0

# ----------------------------
# LOAD TRAINED MODEL
# ----------------------------

model = joblib.load("risk_model.pkl")

# ----------------------------
# MAKE RISK PREDICTION
# ----------------------------

import pandas as pd

input_data = pd.DataFrame([{
    "temperature": temperature,
    "rainfall": rainfall,
    "aqi": aqi,
    "wind_speed": wind_speed,
    "traffic_index": traffic_index,
    "flood_risk": flood_risk
}])

prediction = model.predict(input_data)

if prediction[0] == 1:
    risk_level = "HIGH"
    premium = "₹50 / week"
else:
    risk_level = "LOW"
    premium = "₹30 / week"

print("\nAI Risk Prediction")
print("Risk Level:", risk_level)
print("Suggested Weekly Premium:", premium)