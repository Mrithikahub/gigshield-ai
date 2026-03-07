"""
Fraud Detector
===============
Phase 1 : 6 rule-based checks → fraud_score 0.0–1.0
Phase 3 : Member 4 replaces detect() with Isolation Forest / anomaly detection

Integration point for Member 4:
    from ml_models.fraud_model import score_claim
    fraud_score = score_claim(features)
    flags       = explain_fraud(features)
"""

from datetime import datetime, timedelta
from typing   import Optional

# ── Thresholds ─────────────────────────────────────────────────────────────────

AUTO_REJECT_SCORE = 0.60   # >= this → auto reject
MANUAL_REVIEW     = 0.30   # >= this → pending (human review)
MAX_CLAIMS_7D     = 4      # more than this in 7 days = suspicious

# Approximate city bounding boxes for GPS verification
CITY_BOUNDS: dict[str, tuple] = {
    "mumbai":    (18.85, 19.35, 72.75, 73.05),
    "chennai":   (12.85, 13.25, 80.10, 80.35),
    "delhi":     (28.40, 28.90, 76.85, 77.40),
    "bangalore": (12.80, 13.15, 77.45, 77.80),
    "hyderabad": (17.25, 17.65, 78.25, 78.65),
    "kolkata":   (22.40, 22.70, 88.20, 88.50),
    "pune":      (18.40, 18.65, 73.75, 74.05),
}


def _gps_in_city(city: str, lat: float, lng: float) -> bool:
    bounds = CITY_BOUNDS.get(city.lower())
    if not bounds:
        return True   # unknown city — don't penalise
    lat_min, lat_max, lng_min, lng_max = bounds
    return lat_min <= lat <= lat_max and lng_min <= lng <= lng_max


def detect(
    worker_id:    str,
    trigger_type: str,
    event_date:   datetime,
    city:         str,
    gps_lat:      Optional[float],
    gps_lng:      Optional[float],
) -> tuple[float, list[str], str]:
    """
    Runs all fraud checks. Returns (fraud_score, flags, decision).

    decision:
        "approved" → clean claim, pay immediately
        "pending"  → borderline, needs manual review
        "rejected" → high fraud score, deny payout
    """
    from app.utils.database import get_worker_claims, duplicate_claim_exists

    score: float    = 0.0
    flags: list[str] = []

    # ── Rule 1: Duplicate claim same event same day ────────────────────────────
    if duplicate_claim_exists(worker_id, trigger_type, event_date):
        score += 0.50
        flags.append("DUPLICATE_CLAIM_SAME_DAY")

    # ── Rule 2: High claim velocity (too many claims in 7 days) ───────────────
    all_claims = get_worker_claims(worker_id)
    recent_7d  = [
        c for c in all_claims
        if c["event_date"] >= datetime.utcnow() - timedelta(days=7)
    ]
    if len(recent_7d) >= MAX_CLAIMS_7D:
        score += 0.25
        flags.append(f"HIGH_VELOCITY_{len(recent_7d)}_CLAIMS_IN_7_DAYS")

    # ── Rule 3: Late submission (> 24 hrs after event) ─────────────────────────
    lag_hours = (datetime.utcnow() - event_date).total_seconds() / 3600
    if lag_hours > 24:
        score += 0.20
        flags.append(f"LATE_SUBMISSION_{int(lag_hours)}H_AFTER_EVENT")

    # ── Rule 4: Missing GPS on manual claim ────────────────────────────────────
    if gps_lat is None or gps_lng is None:
        score += 0.10
        flags.append("NO_GPS_PROVIDED")

    # ── Rule 5: GPS coordinates outside claimed city (spoofing) ───────────────
    elif not _gps_in_city(city, gps_lat, gps_lng):
        score += 0.40
        flags.append("GPS_OUTSIDE_CITY_BOUNDS — possible spoofing")

    # ── Rule 6: Multi-trigger stacking this week ───────────────────────────────
    triggers_this_week = set(c["trigger_type"] for c in recent_7d)
    if len(triggers_this_week) >= 3:
        score += 0.20
        flags.append(f"MULTI_TRIGGER_STACKING_{len(triggers_this_week)}_TYPES")

    # ── Decision ───────────────────────────────────────────────────────────────
    final_score = round(min(score, 1.0), 2)
    if final_score >= AUTO_REJECT_SCORE:
        decision = "rejected"
    elif final_score >= MANUAL_REVIEW:
        decision = "pending"
    else:
        decision = "approved"

    return final_score, flags, decision
