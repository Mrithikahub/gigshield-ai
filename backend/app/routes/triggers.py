"""
Trigger Routes  ⚡
==================
POST /api/triggers/fire             → fire a real disruption event
POST /api/triggers/simulate         → demo simulation (no real data needed)
GET  /api/triggers/thresholds       → all trigger definitions
GET  /api/triggers/forecast/{city}  → weekly risk forecast for a city
"""

from datetime  import datetime
from fastapi   import APIRouter, HTTPException, Query

from app.models.schemas          import TriggerFireRequest
from app.services.trigger_engine import is_triggered, calculate_payout, TRIGGERS
from app.services.payout_service import process_payout
from app.utils.database          import (
    get_worker, get_active_policies_in_city,
    create_claim, duplicate_claim_exists,
)

router = APIRouter()


@router.post("/fire", summary="⚡ Fire a parametric disruption event")
def fire_trigger(body: TriggerFireRequest):
    """
    **The core of GigShield.**

    1. Receives a disruption event (from weather API / mock)
    2. Checks if the value breaches the threshold
    3. If yes → finds ALL active policy holders in that city
    4. Auto-creates an approved claim for each worker
    5. Fires an instant UPI payout for each
    6. Returns full summary

    This is zero-touch for the worker. They wake up to money in their UPI.
    """
    rule      = TRIGGERS.get(body.trigger_type)
    triggered = is_triggered(body.trigger_type, body.value)

    # ── Not triggered ──────────────────────────────────────────────────────────
    if not triggered:
        return {
            "triggered":   False,
            "trigger_type": body.trigger_type,
            "label":       rule["label"],
            "city":        body.city,
            "value":       f"{body.value} {rule['unit']}",
            "threshold":   f"{rule['operator']} {rule['threshold']} {rule['unit']}",
            "message":     "Value is below threshold. No claims generated.",
        }

    # ── Triggered — find all affected workers ──────────────────────────────────
    active_policies = get_active_policies_in_city(body.city)
    claims_created  = []
    claims_skipped  = []

    for policy in active_policies:
        worker = get_worker(policy["worker_id"])
        if not worker:
            continue

        # Skip duplicates — same worker, same trigger, same day
        if duplicate_claim_exists(policy["worker_id"], body.trigger_type, body.timestamp):
            claims_skipped.append({
                "worker_id": policy["worker_id"],
                "reason":    "Duplicate claim — already paid today",
            })
            continue

        # Calculate payout for this worker
        payout_amount = calculate_payout(body.trigger_type, policy["coverage_per_event"])

        # Fire instant payout
        payout_receipt = process_payout(
            worker_id=policy["worker_id"],
            claim_id="AUTO",
            amount=payout_amount,
            phone=worker["phone"],
        )

        # Record claim
        claim = create_claim({
            "worker_id":      policy["worker_id"],
            "policy_id":      policy["id"],
            "trigger_type":   body.trigger_type,
            "event_date":     body.timestamp,
            "location":       body.city,
            "payout_amount":  payout_amount,
            "status":         "paid",
            "fraud_score":    0.0,
            "fraud_flags":    [],
            "is_auto":        True,
            "payout_receipt": payout_receipt,
        })

        claims_created.append({
            "claim_id":       claim["id"],
            "worker_name":    worker["name"],
            "phone":          worker["phone"],
            "payout_inr":     payout_amount,
            "transaction_id": payout_receipt["transaction_id"],
            "upi_id":         payout_receipt["upi_id"],
            "status":         "paid ✅",
        })

    total_payout = round(sum(c["payout_inr"] for c in claims_created), 2)

    return {
        "triggered":        True,
        "trigger_type":     body.trigger_type,
        "label":            rule["label"],
        "city":             body.city,
        "event_value":      f"{body.value} {rule['unit']}",
        "threshold":        f"{rule['operator']} {rule['threshold']} {rule['unit']}",
        "timestamp":        body.timestamp.isoformat(),
        "workers_paid":     len(claims_created),
        "workers_skipped":  len(claims_skipped),
        "total_payout_inr": total_payout,
        "claims":           claims_created,
        "skipped":          claims_skipped,
        "message": (
            f"✅ {len(claims_created)} workers paid ₹{total_payout} "
            f"via UPI instantly. Zero manual steps."
        ),
    }


@router.post("/simulate", summary="Quick simulation for demos")
def simulate_trigger(
    city:         str   = Query("mumbai",     description="City to simulate"),
    trigger_type: str   = Query("HEAVY_RAIN", description="Disruption type"),
    value:        float = Query(75.0,          description="Event value (above threshold)"),
):
    """
    Fires a fake event — perfect for the demo video.
    Use this to show judges the full auto-claim + payout chain.
    """
    if trigger_type not in TRIGGERS:
        raise HTTPException(400, f"Invalid trigger. Options: {list(TRIGGERS.keys())}")

    body = TriggerFireRequest(
        city=city,
        trigger_type=trigger_type,
        value=value,
        timestamp=datetime.utcnow(),
    )
    return fire_trigger(body)


@router.get("/thresholds", summary="All trigger definitions and thresholds")
def get_thresholds():
    return {
        "count":    len(TRIGGERS),
        "triggers": TRIGGERS,
    }


@router.get("/forecast/{city}", summary="Weekly disruption forecast for a city")
def city_forecast(city: str):
    """
    Returns predicted disruption probabilities for the coming week.
    Used by admin dashboard for planning.
    Phase 2: Member 5 replaces with live OpenWeather 7-day forecast.
    """
    import random
    BASE = {
        "mumbai":    {"HEAVY_RAIN": 0.60, "FLOOD_ALERT": 0.30, "HIGH_AQI": 0.10},
        "delhi":     {"EXTREME_HEAT": 0.65, "HIGH_AQI": 0.55},
        "chennai":   {"HEAVY_RAIN": 0.55, "FLOOD_ALERT": 0.25},
        "bangalore": {"HEAVY_RAIN": 0.35, "HIGH_AQI": 0.15},
        "kolkata":   {"HEAVY_RAIN": 0.50, "FLOOD_ALERT": 0.30},
        "hyderabad": {"EXTREME_HEAT": 0.40, "HIGH_AQI": 0.25},
        "pune":      {"HEAVY_RAIN": 0.30, "FLOOD_ALERT": 0.15},
    }
    probs = BASE.get(city.lower(), {"HEAVY_RAIN": 0.20, "EXTREME_HEAT": 0.15})
    forecast = {
        t: round(min(max(p + random.uniform(-0.04, 0.04), 0.01), 0.99), 2)
        for t, p in probs.items()
    }
    top = max(forecast, key=forecast.get)
    return {
        "city":     city,
        "week":     datetime.utcnow().strftime("%Y-W%W"),
        "forecast": forecast,
        "top_risk": {
            "trigger":     top,
            "probability": forecast[top],
            "label":       TRIGGERS[top]["label"],
        },
    }
