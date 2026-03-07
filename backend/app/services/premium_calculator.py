"""
Premium Calculator
===================
Dynamic weekly premium based on:
  1. City risk zone   (where the worker operates)
  2. AI risk score    (from risk_engine.py)
  3. Daily earnings   (sets coverage amount)

Called by:
  GET  /api/premium/quote   → preview before buying
  POST /api/policies/create → actual policy creation

Formula
-------
  weekly_premium = BASE_RATE
                 + ZONE_SURCHARGE[risk_zone]
                 + round(risk_score × RISK_LOADING, 2)

  coverage_per_event = min(avg_daily_earning × COVERAGE_RATIO, MAX_COVERAGE)
"""

from app.services.risk_engine import get_risk_zone, compute_risk_score, risk_label, risk_advice

# ── Config ─────────────────────────────────────────────────────────────────────

BASE_RATE       = 30.0   # INR/week — minimum premium
RISK_LOADING    = 15.0   # INR/week — multiplied by risk_score (0–1)
MAX_COVERAGE    = 400.0  # INR/event cap
COVERAGE_RATIO  = 0.80   # coverage = 80% of daily earning

ZONE_SURCHARGE: dict[str, float] = {
    "low":    0.0,
    "medium": 10.0,
    "high":   20.0,
}


# ── Core calculation ────────────────────────────────────────────────────────────

def calculate_premium(
    city:              str,
    avg_daily_earning: float,
    risk_score:        float,
) -> tuple[float, float, dict]:
    """
    Returns:
        weekly_premium      (float)  — INR per week
        coverage_per_event  (float)  — INR per triggered event
        breakdown           (dict)   — itemised for transparency
    """
    zone         = get_risk_zone(city)
    surcharge    = ZONE_SURCHARGE[zone]
    loading      = round(risk_score * RISK_LOADING, 2)
    premium      = round(BASE_RATE + surcharge + loading, 2)
    coverage     = round(min(avg_daily_earning * COVERAGE_RATIO, MAX_COVERAGE), 2)

    breakdown = {
        "base_rate":          BASE_RATE,
        "zone_surcharge":     surcharge,
        "risk_loading":       loading,
        "weekly_premium":     premium,
        "coverage_per_event": coverage,
        "risk_zone":          zone,
    }
    return premium, coverage, breakdown


def get_premium_quote(
    city:              str,
    platform:          str,
    work_zone:         str,
    avg_daily_earning: float,
) -> dict:
    """
    Full quote object — used by GET /api/premium/quote.
    No side effects, no DB writes.
    """
    risk_score = compute_risk_score(city, platform, avg_daily_earning, work_zone)
    premium, coverage, breakdown = calculate_premium(city, avg_daily_earning, risk_score)

    return {
        "risk_score":         risk_score,
        "risk_level":         risk_label(risk_score),
        "risk_zone":          get_risk_zone(city),
        "weekly_premium":     premium,
        "coverage_per_event": coverage,
        "monthly_estimate":   round(premium * 4, 2),
        "value_ratio":        round(coverage / premium, 1),
        "breakdown":          breakdown,
        "advice":             risk_advice(risk_score, city),
    }
