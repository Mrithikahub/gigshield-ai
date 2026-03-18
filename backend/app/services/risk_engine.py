import os
import joblib
import pandas as pd

CITY_RISK = {
    "mumbai": "high", "chennai": "high", "delhi": "high", "kolkata": "high",
    "bangalore": "medium", "hyderabad": "medium", "pune": "medium", "ahmedabad": "medium",
}

CITY_WEATHER = {
    "mumbai":    {"temperature": 32, "rainfall": 70, "aqi": 150, "wind_speed": 15, "traffic_index": 80, "flood_risk": 1},
    "delhi":     {"temperature": 40, "rainfall": 10, "aqi": 300, "wind_speed": 10, "traffic_index": 85, "flood_risk": 0},
    "chennai":   {"temperature": 34, "rainfall": 60, "aqi": 120, "wind_speed": 20, "traffic_index": 70, "flood_risk": 1},
    "bangalore": {"temperature": 28, "rainfall": 30, "aqi": 100, "wind_speed": 12, "traffic_index": 75, "flood_risk": 0},
    "hyderabad": {"temperature": 35, "rainfall": 20, "aqi": 130, "wind_speed": 10, "traffic_index": 65, "flood_risk": 0},
    "kolkata":   {"temperature": 33, "rainfall": 65, "aqi": 180, "wind_speed": 18, "traffic_index": 70, "flood_risk": 1},
    "pune":      {"temperature": 30, "rainfall": 25, "aqi": 90,  "wind_speed": 10, "traffic_index": 60, "flood_risk": 0},
}

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "ai_models", "risk_model.pkl")
_model = None

def _load_model():
    global _model
    if _model is None and os.path.exists(MODEL_PATH):
        _model = joblib.load(MODEL_PATH)
    return _model


def get_risk_zone(city: str) -> str:
    return CITY_RISK.get(city.strip().lower(), "low")


def compute_risk_score(city: str, platform: str, avg_daily_earning: float) -> float:
    model = _load_model()
    c = city.strip().lower()
    weather = CITY_WEATHER.get(c, {"temperature":30,"rainfall":10,"aqi":100,"wind_speed":10,"traffic_index":60,"flood_risk":0})

    if model:
        try:
            input_df = pd.DataFrame([{
                "temperature":   weather["temperature"],
                "rainfall":      weather["rainfall"],
                "wind":          weather["wind_speed"],
                "humidity":      70,
                "aqi":           weather["aqi"],
                "disruption_count": 1 if weather["rainfall"] > 50 or weather["aqi"] > 200 else 0,
                "risk_score":    0.5,
                "is_disrupted":  1 if weather["rainfall"] > 50 else 0,
            }])
            pred = model.predict(input_df)[0]
            return round(min(float(pred) / 3.0, 1.0), 2)
        except:
            pass

    score = 0.20
    if c in ("mumbai","chennai","delhi","kolkata"):      score += 0.30
    elif c in ("bangalore","hyderabad","pune","ahmedabad"): score += 0.15
    if avg_daily_earning < 400:   score += 0.10
    elif avg_daily_earning < 600: score += 0.05
    if platform.lower() == "swiggy": score += 0.05
    return round(min(score, 1.0), 2)


def risk_label(score: float) -> str:
    if score >= 0.65: return "high"
    if score >= 0.35: return "medium"
    return "low"


def compute_weekly_premium(score: float, city: str, avg_daily_earning: float) -> float:
    c = city.strip().lower()
    weather = CITY_WEATHER.get(c, {"rainfall":10,"aqi":100,"traffic_index":60})
    zone = get_risk_zone(city)
    surcharge = {"low": 0, "medium": 15, "high": 25}[zone]
    premium = 30 + surcharge + (weather["rainfall"] * 0.2) + (weather["aqi"]/100 * 2) + (weather["traffic_index"] * 0.05)
    if score >= 0.65: premium += 10
    return round(premium, 2)
