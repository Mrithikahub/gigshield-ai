"""
Parametric Trigger Engine
==========================
Defines all disruption types, their thresholds, and payout rules.

When a disruption breaches its threshold:
  1. Find every active policy holder in that city
  2. Auto-create an approved claim for each
  3. Fire an instant mock payout (UPI)
  4. Return full summary

Phase 2: Member 5 connects live OpenWeather / AQI APIs to fire() automatically.
"""

from datetime import datetime

# ── Trigger definitions ─────────────────────────────────────────────────────────

TRIGGERS: dict[str, dict] = {
    "HEAVY_RAIN": {
        "label":       "Heavy Rainfall",
        "description": "Rainfall makes outdoor delivery impossible",
        "unit":        "mm",
        "threshold":   50.0,
        "operator":    ">=",
        "payout_mult": 1.00,   # 100% of coverage
        "hours_lost":  4,
    },
    "EXTREME_HEAT": {
        "label":       "Extreme Heat",
        "description": "Dangerous temperatures prevent safe outdoor work",
        "unit":        "°C",
        "threshold":   42.0,
        "operator":    ">=",
        "payout_mult": 0.75,   # 75% of coverage
        "hours_lost":  3,
    },
    "HIGH_AQI": {
        "label":       "Severe Air Pollution",
        "description": "AQI spike — hazardous to work outdoors",
        "unit":        "AQI",
        "threshold":   400.0,
        "operator":    ">=",
        "payout_mult": 0.75,
        "hours_lost":  3,
    },
    "FLOOD_ALERT": {
        "label":       "Flood Alert",
        "description": "Active flood alert — roads impassable",
        "unit":        "alert flag",
        "threshold":   1.0,
        "operator":    "==",
        "payout_mult": 1.25,   # 125% — multi-day impact
        "hours_lost":  8,
    },
    "CURFEW": {
        "label":       "Curfew / Lockdown",
        "description": "Government-imposed movement restriction",
        "unit":        "flag",
        "threshold":   1.0,
        "operator":    "==",
        "payout_mult": 1.00,
        "hours_lost":  8,
    },
}


# ── Core functions ──────────────────────────────────────────────────────────────

def is_triggered(trigger_type: str, value: float) -> bool:
    """Returns True if the event value breaches the defined threshold."""
    rule = TRIGGERS.get(trigger_type)
    if not rule:
        return False
    op  = rule["operator"]
    thr = rule["threshold"]
    if op == ">=": return value >= thr
    if op == "==": return value == thr
    if op == ">":  return value > thr
    if op == "<=": return value <= thr
    return False


def calculate_payout(trigger_type: str, coverage_per_event: float) -> float:
    """Payout = coverage × multiplier for this disruption type."""
    mult = TRIGGERS[trigger_type]["payout_mult"]
    return round(coverage_per_event * mult, 2)


def income_loss_breakdown(trigger_type: str, avg_daily_earning: float) -> dict:
    """
    Shows the worker exactly how many hours and ₹ they lose.
    Used by GET /api/workers/{id}/income-estimate
    """
    rule        = TRIGGERS.get(trigger_type, {})
    hours_lost  = rule.get("hours_lost", 4)
    hourly_rate = round(avg_daily_earning / 10, 2)   # assume 10-hr work day
    income_lost = round(hourly_rate * hours_lost, 2)
    return {
        "trigger_type":    trigger_type,
        "label":           rule.get("label", trigger_type),
        "hours_lost":      hours_lost,
        "hourly_rate_inr": hourly_rate,
        "estimated_loss":  income_lost,
        "covered_by_gigshield": income_lost,
        "message": (
            f"A {rule.get('label','disruption')} typically costs you {hours_lost} hrs "
            f"≈ ₹{income_lost}. GigShield covers this automatically."
        ),
    }
