from app.services.risk_engine import (
    compute_risk_score, risk_label, compute_weekly_premium,
    get_risk_zone, CITY_WEATHER,
)


def calculate_premium(worker: dict) -> dict:
    city     = worker["city"]
    platform = worker["platform"]
    earning  = worker.get("avg_daily_earning", 500.0)

    score    = compute_risk_score(city, platform, earning)
    level    = risk_label(score)
    premium  = compute_weekly_premium(score, city, earning)
    coverage = round(min(earning * 0.80, 400.0), 2)
    weather  = CITY_WEATHER.get(city.lower(), {"rainfall": 10, "aqi": 100, "traffic_index": 60})
    disp_prob = round(min((weather["rainfall"] / 100 + weather["aqi"] / 500) / 2, 0.99), 2)

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
