import requests

# 🔑 YOUR WEATHER API KEY
API_KEY = "a89589b66d9e76fd6c120a419975a540"


# 🌦️ FETCH REAL WEATHER DATA
def get_weather(city: str):
    url = f"http://api.weatherapi.com/v1/current.json?key={API_KEY}&q={city}"

    try:
        response = requests.get(url)
        data = response.json()

        # 🧠 Extract useful values
        rainfall = data.get("current", {}).get("precip_mm", 0)
        aqi = data.get("current", {}).get("air_quality", {}).get("pm2_5", 50)

        # Fake traffic (since API doesn’t give it)
        traffic_index = 60

        return {
            "rainfall": rainfall,
            "aqi": aqi,
            "traffic_index": traffic_index
        }

    except:
        # fallback if API fails
        return {
            "rainfall": 10,
            "aqi": 100,
            "traffic_index": 60
        }


# 🧠 RISK ZONE BASED ON CITY
def get_risk_zone(city: str) -> str:
    city = city.lower()

    if city in ["mumbai", "delhi"]:
        return "high"
    elif city in ["chennai", "bangalore", "hyderabad"]:
        return "medium"
    else:
        return "low"


# 🧠 CALCULATE RISK SCORE
def compute_risk_score(city: str, platform: str, earning: float) -> float:
    weather = get_weather(city)

    # Step-by-step scoring
    rain_factor = weather["rainfall"] / 100        # 0–1
    aqi_factor = weather["aqi"] / 500              # 0–1
    traffic_factor = weather["traffic_index"] / 100

    # combine everything
    score = (rain_factor + aqi_factor + traffic_factor) / 3

    return round(min(score, 1.0), 2)


# 🏷️ RISK LABEL
def risk_label(score: float) -> str:
    if score < 0.3:
        return "low"
    elif score < 0.6:
        return "medium"
    else:
        return "high"


# 💰 PREMIUM CALCULATION
def compute_weekly_premium(score: float, city: str, earning: float) -> float:
    base_rate = 30

    zone = get_risk_zone(city)

    # zone surcharge
    if zone == "high":
        zone_charge = 25
    elif zone == "medium":
        zone_charge = 15
    else:
        zone_charge = 0

    # risk-based loading
    risk_loading = score * 20

    # disruption loading (extra risk from weather)
    disruption_loading = score * 30

    premium = base_rate + zone_charge + risk_loading + disruption_loading

    return round(premium, 2)