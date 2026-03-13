"""
disruption_detector.py
----------------------
GigShield AI — Disruption Event Detection
Analyses WeatherData and flags events that trigger insurance payouts.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List

from weather_service import WeatherData, get_weather_by_city, get_weather_by_coords


# ── Disruption Types ──────────────────────────────────────────────────────────

class DisruptionType(str, Enum):
    HEAVY_RAIN      = "heavy_rain"
    EXTREME_HEAT    = "extreme_heat"
    SEVERE_POLLUTION = "severe_pollution"


# ── Thresholds (easily tuned per region / product tier) ───────────────────────

THRESHOLDS = {
    DisruptionType.HEAVY_RAIN:       50.0,   # mm/hr
    DisruptionType.EXTREME_HEAT:     42.0,   # °C
    DisruptionType.SEVERE_POLLUTION: 350,    # AQI index (0-500 scale)
}

# Severity bands per disruption type
SEVERITY_BANDS = {
    DisruptionType.HEAVY_RAIN: [
        (100, "critical"),
        (75,  "high"),
        (50,  "medium"),
    ],
    DisruptionType.EXTREME_HEAT: [
        (48,  "critical"),
        (45,  "high"),
        (42,  "medium"),
    ],
    DisruptionType.SEVERE_POLLUTION: [
        (450, "critical"),
        (400, "high"),
        (350, "medium"),
    ],
}


# ── Data Models ───────────────────────────────────────────────────────────────

@dataclass
class DisruptionEvent:
    type:        DisruptionType
    severity:    str            # "medium" | "high" | "critical"
    value:       float          # actual measured value
    threshold:   float          # threshold that was crossed
    description: str

    def to_dict(self) -> dict:
        return {
            "type":        self.type.value,
            "severity":    self.severity,
            "value":       self.value,
            "threshold":   self.threshold,
            "description": self.description,
        }


@dataclass
class DisruptionReport:
    city:       str
    disrupted:  bool
    events:     List[DisruptionEvent] = field(default_factory=list)
    risk_score: float = 0.0   # 0.0 – 1.0 composite score

    def to_dict(self) -> dict:
        return {
            "city":       self.city,
            "disrupted":  self.disrupted,
            "risk_score": round(self.risk_score, 3),
            "events":     [e.to_dict() for e in self.events],
        }


# ── Helpers ───────────────────────────────────────────────────────────────────

def _severity(disruption_type: DisruptionType, value: float) -> str:
    for band_value, label in SEVERITY_BANDS[disruption_type]:
        if value >= band_value:
            return label
    return "medium"


def _severity_weight(severity: str) -> float:
    return {"medium": 0.4, "high": 0.7, "critical": 1.0}.get(severity, 0.4)


# ── Core Detection ────────────────────────────────────────────────────────────

def detect_disruptions(weather: WeatherData) -> DisruptionReport:
    """
    Analyse a WeatherData snapshot and return a DisruptionReport.

    Args:
        weather: WeatherData from weather_service.py

    Returns:
        DisruptionReport with all triggered events and a composite risk score.
    """
    events: List[DisruptionEvent] = []

    # 1. Heavy rain
    if weather.rainfall_1h > THRESHOLDS[DisruptionType.HEAVY_RAIN]:
        sev = _severity(DisruptionType.HEAVY_RAIN, weather.rainfall_1h)
        events.append(DisruptionEvent(
            type        = DisruptionType.HEAVY_RAIN,
            severity    = sev,
            value       = weather.rainfall_1h,
            threshold   = THRESHOLDS[DisruptionType.HEAVY_RAIN],
            description = (
                f"Rainfall of {weather.rainfall_1h:.1f}mm/hr exceeds "
                f"safe threshold of {THRESHOLDS[DisruptionType.HEAVY_RAIN]}mm/hr."
            ),
        ))

    # 2. Extreme heat
    if weather.temperature > THRESHOLDS[DisruptionType.EXTREME_HEAT]:
        sev = _severity(DisruptionType.EXTREME_HEAT, weather.temperature)
        events.append(DisruptionEvent(
            type        = DisruptionType.EXTREME_HEAT,
            severity    = sev,
            value       = weather.temperature,
            threshold   = THRESHOLDS[DisruptionType.EXTREME_HEAT],
            description = (
                f"Temperature of {weather.temperature:.1f}°C exceeds "
                f"safe limit of {THRESHOLDS[DisruptionType.EXTREME_HEAT]}°C."
            ),
        ))

    # 3. Severe pollution
    if weather.aqi > THRESHOLDS[DisruptionType.SEVERE_POLLUTION]:
        sev = _severity(DisruptionType.SEVERE_POLLUTION, weather.aqi)
        events.append(DisruptionEvent(
            type        = DisruptionType.SEVERE_POLLUTION,
            severity    = sev,
            value       = float(weather.aqi),
            threshold   = float(THRESHOLDS[DisruptionType.SEVERE_POLLUTION]),
            description = (
                f"AQI of {weather.aqi} exceeds hazardous threshold "
                f"of {THRESHOLDS[DisruptionType.SEVERE_POLLUTION]}."
            ),
        ))

    # Composite risk score: max of individual weights (capped at 1.0)
    risk_score = min(
        sum(_severity_weight(e.severity) for e in events) / max(len(events), 1)
        if events else 0.0,
        1.0,
    )

    return DisruptionReport(
        city       = weather.city,
        disrupted  = len(events) > 0,
        events     = events,
        risk_score = risk_score,
    )


def detect_disruptions_by_city(city: str) -> DisruptionReport:
    """
    Convenience wrapper: fetch weather then detect disruptions.

    Args:
        city: City name string, e.g. "Chennai,IN"

    Returns:
        DisruptionReport (disrupted=False with empty events if fetch fails).
    """
    weather = get_weather_by_city(city)
    if not weather:
        return DisruptionReport(city=city, disrupted=False, risk_score=0.0)
    return detect_disruptions(weather)


def detect_disruptions_by_coords(lat: float, lon: float) -> DisruptionReport:
    """
    Convenience wrapper using GPS coordinates (for mobile worker tracking).
    """
    weather = get_weather_by_coords(lat, lon)
    if not weather:
        return DisruptionReport(city=f"{lat},{lon}", disrupted=False, risk_score=0.0)
    return detect_disruptions(weather)


# ── Test ──────────────────────────────────────────────────────────────────────

def test_disruption_detector():
    """
    Unit test using synthetic WeatherData objects — no API key needed.
    """
    from weather_service import WeatherData

    scenarios = [
        {
            "label":   "☀️  Normal day in Bangalore",
            "weather": WeatherData("Bangalore", 28.0, 0.0,  3.5, 55, "Clear",           80,  12.97, 77.59),
        },
        {
            "label":   "🌧️  Heavy monsoon in Mumbai",
            "weather": WeatherData("Mumbai",    30.0, 80.0, 12.0, 90, "Heavy Rain",      150, 19.07, 72.88),
        },
        {
            "label":   "🌡️  Heatwave in Rajasthan",
            "weather": WeatherData("Jaipur",    46.5, 0.0,  5.0, 10, "Clear",           100, 26.91, 75.79),
        },
        {
            "label":   "😷  Severe smog in Delhi",
            "weather": WeatherData("Delhi",     22.0, 0.0,  2.0, 70, "Smoke",           420, 28.70, 77.10),
        },
        {
            "label":   "⛈️  Multiple events (rain + heat)",
            "weather": WeatherData("Chennai",   43.0, 60.0, 8.0, 85, "Thunderstorm",    200, 13.08, 80.27),
        },
    ]

    for s in scenarios:
        print(f"\n{'─'*55}")
        print(f"  {s['label']}")
        report = detect_disruptions(s["weather"])
        print(f"  Disrupted : {report.disrupted}")
        print(f"  Risk Score: {report.risk_score:.2f}")
        if report.events:
            for ev in report.events:
                print(f"  • [{ev.severity.upper()}] {ev.type.value} — {ev.description}")
        else:
            print("  No disruption events detected.")


if __name__ == "__main__":
    test_disruption_detector()