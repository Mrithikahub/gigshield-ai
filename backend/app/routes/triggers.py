from fastapi  import APIRouter
from datetime import datetime
from fastapi import APIRouter, HTTPException

from app.models.schemas          import TriggerInput
from app.services.trigger_engine import (
    detect_disruptions, detect_disruptions_live,
    fetch_live_weather, calculate_payout, get_all_thresholds
)
from app.services.fraud_detector import detect_fraud
from app.services.payout_service import process_payout
from app.utils.database          import (
    get_all_policies, get_worker, create_claim, duplicate_exists
)

router = APIRouter()


def _process_disruptions(city: str, disruptions: list, weather_data: dict = None):
    """Shared logic: find affected workers and auto-create claims."""
    if not disruptions:
        return {
            "triggered":  False,
            "city":       city,
            "weather":    weather_data,
            "message":    "No disruption thresholds breached.",
        }

    city_lower = city.strip().lower()
    active_policies = [
        p for p in get_all_policies()
        if p["status"] == "active"
        and get_worker(p["worker_id"]) is not None
        and get_worker(p["worker_id"])["city"] == city_lower
        and p["end_date"] >= datetime.utcnow()
    ]

    all_claims   = []
    total_payout = 0.0

    for disruption in disruptions:
        for policy in active_policies:
            worker = get_worker(policy["worker_id"])

            if duplicate_exists(policy["worker_id"], disruption["trigger_type"]):
                continue

            payout_amount = calculate_payout(policy["coverage_per_event"], disruption["payout_mult"])
            fraud_score, fraud_flags, status = detect_fraud(
                worker_id    = policy["worker_id"],
                trigger_type = disruption["trigger_type"],
                amount       = payout_amount,
                location     = city,
            )

            payout_receipt = process_payout(policy["worker_id"], "AUTO", payout_amount) if status == "approved" else None

            claim = create_claim({
                "worker_id":      policy["worker_id"],
                "policy_id":      policy["policy_id"],
                "trigger_type":   disruption["trigger_type"],
                "amount":         payout_amount,
                "status":         status,
                "fraud_score":    fraud_score,
                "fraud_flags":    fraud_flags,
                "location":       city,
                "is_auto":        True,
                "payout_receipt": payout_receipt,
            })

            if status == "approved":
                total_payout += payout_amount

            all_claims.append({
                "claim_id":     claim["claim_id"],
                "worker_name":  worker["name"],
                "trigger_type": disruption["trigger_type"],
                "amount":       payout_amount,
                "status":       status,
                "payout":       payout_receipt,
            })

    return {
        "triggered":            True,
        "city":                 city,
        "weather":              weather_data,
        "disruptions_detected": [d["trigger_type"] for d in disruptions],
        "workers_affected":     len(active_policies),
        "claims_created":       len(all_claims),
        "total_payout_inr":     round(total_payout, 2),
        "claims":               all_claims,
    }


# ── Manual trigger (for demo / frontend button) ───────────────────────────────
@router.post("")
def fire_trigger(body: TriggerInput):
    """Manual trigger — pass temperature, rainfall, aqi directly."""
    disruptions = detect_disruptions(body.city, body.temperature, body.rainfall, body.aqi)
    weather_data = {
        "temperature": body.temperature,
        "rainfall":    body.rainfall,
        "aqi":         body.aqi,
        "source":      "manual",
    }
    return _process_disruptions(body.city, disruptions, weather_data)


# ── Live auto-trigger using WeatherAPI ────────────────────────────────────────
@router.post("/auto/{city}")
def auto_trigger(city: str):
    """
    Fetches LIVE weather from WeatherAPI for the city,
    detects disruptions automatically, creates claims.
    POST /trigger/auto/Mumbai
    """
    disruptions, weather_data = detect_disruptions_live(city)

    if weather_data is None:
        return {
            "triggered": False,
            "city":      city,
            "message":   "Live weather fetch failed. Check WEATHER_API_KEY in .env",
        }

    return _process_disruptions(city, disruptions, weather_data)


# ── Weather check (no claims created) ────────────────────────────────────────
@router.get("/weather/{city}")
def get_live_weather(city: str):
    """
    Returns current weather + disruption status for a city.
    No claims created. Used by frontend weather widget.
    GET /trigger/weather/Mumbai
    """
    weather = fetch_live_weather(city)

    if not weather:
        return {
            "city":    city,
            "status":  "error",
            "message": "Could not fetch weather. Check WEATHER_API_KEY in .env",
            "weather": None,
            "disrupted": False,
            "disruptions_detected": [],
        }

    from app.services.trigger_engine import detect_disruptions
    disruptions = detect_disruptions(
        city        = city,
        temperature = weather["temperature"],
        rainfall    = weather["rainfall"],
        aqi         = weather["aqi"],
    )

    return {
        "city":                 city,
        "weather":              weather,
        "disrupted":            len(disruptions) > 0,
        "disruptions_detected": [d["trigger_type"] for d in disruptions],
    }


@router.get("/thresholds")
def thresholds():
    return get_all_thresholds()

@router.post("/admin/curfew")
def set_curfew(city: str, active: bool):
    """Admin sets curfew - creates ₹400 claims for all workers in city"""
    from app.utils.database import get_all_workers, create_claim, get_active_policy
    from app.services.fraud_detector import detect_fraud
    from app.services.payout_service import process_payout
    
    if not active:
        return {"message": f"Curfew deactivated in {city}"}
    
    workers = [w for w in get_all_workers() if w["city"].lower() == city.lower()]
    claims_created = []
    
    for worker in workers:
        policy = get_active_policy(worker["worker_id"])
        if not policy:
            continue
            
        fraud_score, fraud_flags, status = detect_fraud(
            worker_id=worker["worker_id"],
            trigger_type="CURFEW",
            amount=400.0,
            location=city
        )
        
        payout = process_payout(worker["worker_id"], "AUTO", 400.0) if status == "approved" else None
        
        claim = create_claim({
            "worker_id": worker["worker_id"],
            "policy_id": policy["policy_id"],
            "trigger_type": "CURFEW",
            "amount": 400.0,
            "status": status,
            "fraud_score": fraud_score,
            "fraud_flags": fraud_flags,
            "location": city,
            "is_auto": True,
            "payout_receipt": payout,
        })
        claims_created.append(claim["claim_id"])
    
    return {
        "message": f"Curfew activated in {city}",
        "claims_created": len(claims_created),
        "claim_ids": claims_created
    }


@router.post("/admin/outage")
def set_outage(platform: str, duration_hrs: int, active: bool):
    """Admin sets platform outage - creates ₹350 claims for all workers on platform"""
    from app.utils.database import get_all_workers, create_claim, get_active_policy
    from app.services.fraud_detector import detect_fraud
    from app.services.payout_service import process_payout
    
    if platform.lower() not in ["swiggy", "zomato"]:
        raise HTTPException(400, "Platform must be 'swiggy' or 'zomato'")
    
    if not active:
        return {"message": f"{platform} outage deactivated"}
    
    workers = [w for w in get_all_workers() if w["platform"].lower() == platform.lower()]
    claims_created = []
    
    for worker in workers:
        policy = get_active_policy(worker["worker_id"])
        if not policy:
            continue
            
        fraud_score, fraud_flags, status = detect_fraud(
            worker_id=worker["worker_id"],
            trigger_type="OUTAGE",
            amount=350.0,
            location=worker["city"]
        )
        
        payout = process_payout(worker["worker_id"], "AUTO", 350.0) if status == "approved" else None
        
        claim = create_claim({
            "worker_id": worker["worker_id"],
            "policy_id": policy["policy_id"],
            "trigger_type": "OUTAGE",
            "amount": 350.0,
            "status": status,
            "fraud_score": fraud_score,
            "fraud_flags": fraud_flags,
            "location": worker["city"],
            "is_auto": True,
            "payout_receipt": payout,
        })
        claims_created.append(claim["claim_id"])
    
    return {
        "message": f"{platform} outage activated for {duration_hrs} hours",
        "claims_created": len(claims_created),
        "claim_ids": claims_created
    }


@router.get("/weather/log")
def get_weather_log(city: str, trigger_type: str, hours: int = 2):
    """Internal endpoint for fraud module to verify weather events"""
    from app.utils.database import get_conn
    from datetime import datetime, timedelta
    
    cutoff = (datetime.utcnow() - timedelta(hours=hours)).isoformat()
    conn = get_conn()
    rows = conn.execute("""
        SELECT * FROM weather_log 
        WHERE city = ? AND trigger_type = ? AND recorded_at >= ?
    """, (city, trigger_type, cutoff)).fetchall()
    conn.close()
    
    return {
        "city": city,
        "trigger_type": trigger_type,
        "time_window_hours": hours,
        "events_found": len(rows),
        "events": [{"value": row["value"], "recorded_at": row["recorded_at"]} for row in rows]
    }
