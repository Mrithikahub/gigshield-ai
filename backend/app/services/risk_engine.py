"""
Risk Engine  — AI Risk Scoring
================================
Computes a risk score (0.0 → 1.0) for a delivery partner.

Phase 1 : Rule-based heuristics
Phase 2 : Member 4 swaps compute_risk_score() with trained ML model

Integration point for Member 4:
    from ml_models.risk_model import predict_risk
    return predict_risk(features)
"""

# ── City risk zones (based on historical disruption frequency) ─────────────────

CITY_RISK_ZONES: dict[str, str] = {
    # High — frequent floods, extreme heat, heavy rain, high AQI
    "mumbai":    "high",
    "chennai":   "high",
    "kolkata":   "high",
    "delhi":     "high",
    # Medium — moderate disruption history
    "bangalore": "medium",
    "hyderabad": "medium",
    "pune":      "medium",
    "ahmedabad": "medium",
    # Default for unknown cities
}

# Work zones historically prone to waterlogging / congestion
HIGH_RISK_ZONES: set[str] = {
    "bandra", "andheri", "dadar", "kurla",      # Mumbai
    "t-nagar", "velachery", "tambaram",          # Chennai
    "whitefield", "koramangala", "indiranagar",  # Bangalore
    "laxmi nagar", "rohini", "dwarka",           # Delhi
}


def get_risk_zone(city: str) -> str:
    return CITY_RISK_ZONES.get(city.strip().lower(), "low")


def compute_risk_score(
    city:              str,
    platform:          str,
    avg_daily_earning: float,
    work_zone:         str,
) -> float:
    """
    Returns risk score 0.0 – 1.0.

    Factors:
      - City disruption history
      - Work zone flood / heat exposure
      - Daily earning (lower = more vulnerable)
      - Platform (Swiggy covers more outer zones)

    TODO Phase 2 — replace body with:
        from ml_models.risk_model import predict_risk
        return predict_risk({
            "city": city, "platform": platform,
            "avg_daily_earning": avg_daily_earning, "work_zone": work_zone
        })
    """
    score = 0.20  # everyone starts with baseline risk

    city_lower = city.strip().lower()
    zone_lower = work_zone.strip().lower()

    # City contribution
    if city_lower in ("mumbai", "chennai", "kolkata", "delhi"):
        score += 0.30
    elif city_lower in ("bangalore", "hyderabad", "pune", "ahmedabad"):
        score += 0.15

    # Work zone contribution
    if zone_lower in HIGH_RISK_ZONES:
        score += 0.15

    # Income vulnerability — lower earners have less buffer
    if avg_daily_earning < 400:
        score += 0.10
    elif avg_daily_earning < 600:
        score += 0.05

    # Platform factor (Swiggy covers more outer/flood-prone areas)
    if platform.lower() == "swiggy":
        score += 0.05

    return round(min(score, 1.0), 2)


def risk_label(score: float) -> str:
    if score >= 0.65: return "High"
    if score >= 0.35: return "Medium"
    return "Low"


def risk_advice(score: float, city: str) -> str:
    zone = get_risk_zone(city)
    if zone == "high":
        return (
            f"{city.title()} is a high-disruption city. "
            "Weekly coverage is strongly recommended — especially during monsoon season."
        )
    if zone == "medium":
        return (
            f"{city.title()} has moderate disruption risk. "
            "Weekly coverage gives good income protection at a low cost."
        )
    return (
        f"{city.title()} is a lower-risk zone. "
        "Basic weekly coverage is still a good safety net."
    )
