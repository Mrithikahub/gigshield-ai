"""
TriggerPe - Fraud Audit Routes (Phase 3)
Provides a structured audit trail for any filed claim.

GET  /fraud/report/{claim_id}   → full GPS + weather + behavioral audit
POST /fraud/check-gps           → standalone GPS spoof check (reuses check_gps_spoof)
GET  /fraud/validate-weather    → standalone historical weather validation
"""
from fastapi   import APIRouter, HTTPException, Query
from pydantic  import BaseModel
from typing    import Optional
from datetime  import datetime, timedelta

from app.utils.database      import get_claim, get_worker, get_worker_claims
from app.services.fraud_detector import (
    check_gps_spoof,
    validate_weather_history,
    score_behavior,
)

router = APIRouter()


# ── Request body for GPS check ────────────────────────────────────────────────
class GPSCheckRequest(BaseModel):
    worker_city: str
    current_lat: float
    current_lon: float
    ip_city: Optional[str] = None   # optional: triggers IP/GPS mismatch detection


# ═══════════════════════════════════════════════════════════════════════════════
# POST /fraud/check-gps
# ═══════════════════════════════════════════════════════════════════════════════
@router.post("/check-gps")
def check_gps_endpoint(body: GPSCheckRequest):
    """
    Standalone GPS spoof detection.

    Compares the submitted GPS coordinates against the registered city centroid
    using the Haversine formula. Deviations > 5km raise a fraud signal (+0.40).

    Optionally accepts ip_city: if the IP-resolved city differs from the GPS
    city, an additional boost (+0.30) is applied (IP/VPN mismatch detection).

    POST /fraud/check-gps
    Body: { worker_city, current_lat, current_lon, ip_city? }
    """
    result = check_gps_spoof(
        worker_city = body.worker_city,
        current_lat = body.current_lat,
        current_lon = body.current_lon,
        ip_city     = body.ip_city,
    )
    result["input"] = {
        "worker_city": body.worker_city,
        "current_lat": body.current_lat,
        "current_lon": body.current_lon,
        "ip_city":     body.ip_city,
    }
    result["flagged"] = result["score_boost"] > 0
    return result


# ═══════════════════════════════════════════════════════════════════════════════
# GET /fraud/validate-weather
# ═══════════════════════════════════════════════════════════════════════════════
@router.get("/validate-weather")
def validate_weather_endpoint(
    city:         str = Query(..., description="City name (must be in reference list)"),
    date:         str = Query(..., description="Date of claim in YYYY-MM-DD format"),
    trigger_type: str = Query(..., description="Trigger type e.g. HEAVY_RAIN, EXTREME_HEAT"),
):
    """
    Standalone historical weather validation via Open-Meteo free archive API.

    Cross-checks whether the claimed weather trigger actually occurred at the
    given city and date. Returns a fraud signal (score_boost=0.35) if the
    trigger threshold was NOT met according to historical records.

    Note: AQI (HIGH_AQI), CURFEW, STRIKE, PROTEST triggers are social/civil
    events not covered by the Open-Meteo archive — these return valid=null with
    score_boost=0.0 (safe skip, no false fraud signal).

    Archive has ~5-day lag for recent dates — recent claims return valid=null.

    GET /fraud/validate-weather?city=Chennai&date=2025-06-10&trigger_type=HEAVY_RAIN
    """
    if not date or len(date) != 10:
        raise HTTPException(status_code=422, detail="date must be in YYYY-MM-DD format")
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=422, detail="date must be a valid calendar date")

    result = validate_weather_history(city=city, date=date, trigger_type=trigger_type)
    result["input"] = {"city": city, "date": date, "trigger_type": trigger_type}
    result["fraud_signal"] = result.get("score_boost", 0.0) > 0
    return result



@router.get("/report/{claim_id}")
def get_fraud_report(claim_id: str):
    """
    Fraud Audit Report — re-runs GPS spoof detection, historical weather
    validation, and behavioral anomaly scoring for a stored claim.

    Returns a structured audit trail with per-check results, composite
    fraud score, and a final decision label.

    GET /fraud/report/{claim_id}
    """
    # ── Fetch claim & worker ──────────────────────────────────────────────────
    claim = get_claim(claim_id)
    if not claim:
        raise HTTPException(status_code=404, detail=f"Claim '{claim_id}' not found")

    worker = get_worker(claim["worker_id"])
    if not worker:
        raise HTTPException(
            status_code=404,
            detail=f"Worker '{claim['worker_id']}' associated with claim not found",
        )

    all_claims = get_worker_claims(claim["worker_id"])

    # ── 1. GPS Spoof Check ────────────────────────────────────────────────────
    gps_lat = claim.get("gps_lat")
    gps_lng = claim.get("gps_lng")

    if gps_lat and gps_lng:
        gps_check = check_gps_spoof(
            worker_city = worker.get("city", ""),
            current_lat = float(gps_lat),
            current_lon = float(gps_lng),
        )
        gps_check["performed"] = True
    elif not claim.get("is_auto"):
        # Manual claim without GPS coords — inherent risk signal
        gps_check = {
            "performed":   False,
            "score_boost": 0.10,
            "reasons":     ["Manual claim submitted without GPS coordinates"],
            "distance_km": None,
            "city_checked": worker.get("city", ""),
        }
    else:
        # Auto-trigger: GPS not required
        gps_check = {
            "performed":   False,
            "score_boost": 0.0,
            "reasons":     ["Auto-triggered claim — GPS not required"],
            "distance_km": None,
            "city_checked": worker.get("city", ""),
        }

    # ── 2. Historical Weather Validation ──────────────────────────────────────
    created_at = claim.get("created_at")
    if hasattr(created_at, "date"):
        claim_date = created_at.date().isoformat()
    else:
        claim_date = str(created_at)[:10]

    weather_check = validate_weather_history(
        city         = claim.get("location", worker.get("city", "")),
        date         = claim_date,
        trigger_type = claim.get("trigger_type", ""),
    )

    # ── 3. Behavioral Anomaly Score ───────────────────────────────────────────
    now          = datetime.utcnow()
    recent_7d    = [c for c in all_claims if c["created_at"] >= now - timedelta(days=7)]
    avg_claim    = sum(c["amount"] for c in all_claims) / max(len(all_claims), 1)
    days_since   = (now - all_claims[-1]["created_at"]).days if all_claims else 999
    trigger_set  = list(set(c["trigger_type"] for c in all_claims))
    gps_mismatch = 1 if (gps_check.get("score_boost") or 0) > 0 else 0

    behavioral_features = {
        "claims_per_month":          len(recent_7d) * 4,
        "avg_payout_requested":      avg_claim,
        "trigger_type_diversity":    len(trigger_set),
        "time_between_claims_hours": (days_since * 24) if days_since < 999 else 999.0,
        # Use stored risk_score (0–1) scaled to 0–100 for zone_risk_score feature
        "zone_risk_score":           float(worker.get("risk_score") or 0.5) * 100,
        "platform_tenure_months":    12,   # not stored in DB; neutral default
        "gps_mismatch_count":        gps_mismatch,
        "ip_city_mismatch_count":    0,    # not yet tracked at request level
    }
    behavioral_score = score_behavior(behavioral_features)

    # ── 4. Composite Fraud Score & Decision ──────────────────────────────────
    # IMPORTANT: stored_fraud_score is the authoritative score used for the
    # original claim decision. GPS, weather, and behavioral scores are already
    # baked into it from detect_fraud(). We surface them here as a breakdown
    # for auditability — NOT added on top (that would double-count).
    stored_score  = float(claim.get("fraud_score") or 0.0)
    gps_boost     = float(gps_check.get("score_boost") or 0.0)
    weather_boost = float(weather_check.get("score_boost") or 0.0)
    b_boost       = round(behavioral_score * 0.30, 2) if behavioral_score > 0.6 else 0.0
    final_score   = stored_score   # authoritative — do not re-add components

    decision = (
        "AUTO_REJECTED"  if final_score >= 0.65
        else "MANUAL_REVIEW" if final_score >= 0.35
        else "AUTO_APPROVED"
    )

    # ── 5. Reason Codes ───────────────────────────────────────────────────────
    reason_codes = list(claim.get("fraud_flags") or [])   # stored flags from original check
    if gps_boost > 0:
        reason_codes.extend(gps_check.get("reasons", []))
    if weather_boost > 0:
        reason_codes.append(weather_check.get("reason", "Historical weather mismatch"))
    if behavioral_score > 0.6:
        reason_codes.append(f"Behavioral anomaly score: {behavioral_score:.4f}")

    return {
        "claim_id":           claim_id,
        "worker_id":          claim["worker_id"],
        "trigger_type":       claim.get("trigger_type"),
        "claim_location":     claim.get("location"),
        "claim_date":         claim_date,

        "stored_fraud_score": stored_score,
        "stored_status":      claim.get("status"),

        "gps_check":          gps_check,
        "weather_validation": weather_check,
        "behavioral_score":   behavioral_score,

        "final_fraud_score":  final_score,
        "decision":           decision,
        "reason_codes":       reason_codes,

        "audit_timestamp":    datetime.utcnow().isoformat() + "Z",
    }
