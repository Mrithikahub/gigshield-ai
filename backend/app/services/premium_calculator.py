from app.services.risk_engine import (
    compute_risk_score, risk_label, compute_weekly_premium,
    get_risk_zone, get_weather
)


def calculate_premium(worker: dict) -> dict:
    city     = worker["city"]
    platform = worker["platform"]
    earning  = worker.get("avg_daily_earning", 500.0)

    # ✅ RISK SCORE (already uses weather internally)
    score    = compute_risk_score(city, platform, earning)
    level    = risk_label(score)

    # ✅ PREMIUM
    premium  = compute_weekly_premium(score, city, earning)

    # ✅ COVERAGE
    coverage = round(min(earning * 0.80, 400.0), 2)

    # ✅ REAL WEATHER CALL
    weather = get_weather(city)

    # ✅ NEW DISRUPTION LOGIC (based on REAL data)
    temp = weather["temperature"]
    humidity = weather["humidity"]
    wind = weather["wind"]
    condition = weather["condition"]

    disp_prob = 0

    if condition in ["Rain", "Thunderstorm"]:
        disp_prob += 0.4

    if wind > 10:
        disp_prob += 0.3

    if humidity > 80:
        disp_prob += 0.2

    disp_prob = round(min(disp_prob, 0.99), 2)

    return {
        "worker_id":              worker["worker_id"],
        "risk_level":             level,
        "risk_score":             score,
        "risk_zone":              get_risk_zone(city),
        "disruption_probability": disp_prob,
        "weekly_premium":         premium,
        "coverage_per_event":     coverage,
        "monthly_estimate":       round(premium * 4, 2),
        "breakdown": {
            "base_rate":          30,
            "zone_surcharge":     {"low": 0, "medium": 15, "high": 25}[get_risk_zone(city)],
            "disruption_loading": round(disp_prob * 30, 2),
            "risk_loading":       round(score * 20, 2),
        },
    }