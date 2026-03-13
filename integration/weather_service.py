"""
weather_service.py
------------------
GigShield AI — Weather Data Integration
Fetches real-time weather metrics from OpenWeatherMap API.
"""
import os
import requests
from dotenv import load_dotenv
from dataclasses import dataclass
from typing import Optional

load_dotenv()


# ── Config ────────────────────────────────────────────────────────────────────

OWM_BASE_URL = "https://api.openweathermap.org/data/2.5"
OWM_AIR_URL  = "http://api.openweathermap.org/data/2.5/air_pollution"
API_KEY      = os.getenv("OPENWEATHERMAP_API_KEY", "YOUR_API_KEY_HERE")


# ── Data Model ────────────────────────────────────────────────────────────────

@dataclass
class WeatherData:
    city:        str
    temperature: float   # °C
    rainfall_1h: float   # mm in last hour
    wind_speed:  float   # m/s
    humidity:    int     # %
    description: str
    aqi:         int     # Air Quality Index (1–5 scale → mapped to 0–500)
    lat:         float
    lon:         float

    def to_dict(self) -> dict:
        return {
            "city":        self.city,
            "temperature": self.temperature,
            "rainfall_1h": self.rainfall_1h,
            "wind_speed":  self.wind_speed,
            "humidity":    self.humidity,
            "description": self.description,
            "aqi":         self.aqi,
            "lat":         self.lat,
            "lon":         self.lon,
        }


# ── Helpers ───────────────────────────────────────────────────────────────────

def _owm_aqi_to_index(owm_aqi: int) -> int:
    """
    Map OpenWeatherMap's 1–5 AQI scale to a 0–500 US AQI-style index
    so disruption_detector.py can use a single threshold (e.g. >350).
    """
    mapping = {1: 25, 2: 75, 3: 150, 4: 250, 5: 400}
    return mapping.get(owm_aqi, 0)


# ── Core Functions ────────────────────────────────────────────────────────────

def get_weather_by_city(city: str, api_key: str = API_KEY) -> Optional[WeatherData]:
    """
    Fetch current weather for a named city.

    Args:
        city:    City name, e.g. "Mumbai" or "Delhi,IN"
        api_key: OpenWeatherMap API key (defaults to env var)

    Returns:
        WeatherData dataclass or None on failure.
    """
    try:
        # --- Current weather ---
        weather_resp = requests.get(
            f"{OWM_BASE_URL}/weather",
            params={"q": city, "appid": api_key, "units": "metric"},
            timeout=10,
        )
        weather_resp.raise_for_status()
        w = weather_resp.json()

        lat = w["coord"]["lat"]
        lon = w["coord"]["lon"]

        # --- Air pollution ---
        aqi_raw  = _fetch_aqi(lat, lon, api_key)

        return WeatherData(
            city        = w.get("name", city),
            temperature = w["main"]["temp"],
            rainfall_1h = w.get("rain", {}).get("1h", 0.0),
            wind_speed  = w["wind"]["speed"],
            humidity    = w["main"]["humidity"],
            description = w["weather"][0]["description"].title(),
            aqi         = aqi_raw,
            lat         = lat,
            lon         = lon,
        )

    except requests.RequestException as exc:
        print(f"[WeatherService] API error for '{city}': {exc}")
        return None


def get_weather_by_coords(lat: float, lon: float, api_key: str = API_KEY) -> Optional[WeatherData]:
    """
    Fetch current weather by GPS coordinates (useful when worker location
    is known from the delivery app).

    Args:
        lat, lon: GPS coordinates
        api_key:  OpenWeatherMap API key

    Returns:
        WeatherData dataclass or None on failure.
    """
    try:
        weather_resp = requests.get(
            f"{OWM_BASE_URL}/weather",
            params={"lat": lat, "lon": lon, "appid": api_key, "units": "metric"},
            timeout=10,
        )
        weather_resp.raise_for_status()
        w = weather_resp.json()

        aqi_raw = _fetch_aqi(lat, lon, api_key)

        return WeatherData(
            city        = w.get("name", f"{lat:.2f},{lon:.2f}"),
            temperature = w["main"]["temp"],
            rainfall_1h = w.get("rain", {}).get("1h", 0.0),
            wind_speed  = w["wind"]["speed"],
            humidity    = w["main"]["humidity"],
            description = w["weather"][0]["description"].title(),
            aqi         = aqi_raw,
            lat         = lat,
            lon         = lon,
        )

    except requests.RequestException as exc:
        print(f"[WeatherService] API error for coords ({lat},{lon}): {exc}")
        return None


def _fetch_aqi(lat: float, lon: float, api_key: str) -> int:
    """Internal helper — fetch AQI and convert to 0-500 scale."""
    try:
        aqi_resp = requests.get(
            OWM_AIR_URL,
            params={"lat": lat, "lon": lon, "appid": api_key},
            timeout=10,
        )
        aqi_resp.raise_for_status()
        owm_aqi = aqi_resp.json()["list"][0]["main"]["aqi"]
        return _owm_aqi_to_index(owm_aqi)
    except Exception:
        return 0  # graceful fallback


# ── Test ──────────────────────────────────────────────────────────────────────

def test_weather_service():
    """Quick smoke-test — prints results for a few Indian cities."""
    cities = ["Mumbai,IN", "Chennai,IN", "Delhi,IN"]

    for city in cities:
        print(f"\n{'─'*50}")
        print(f"📍  Fetching weather for: {city}")
        data = get_weather_by_city(city)
        if data:
            for key, val in data.to_dict().items():
                print(f"    {key:<15} {val}")
        else:
            print("    ⚠️  Failed to fetch data (check API key)")


if __name__ == "__main__":
    test_weather_service()