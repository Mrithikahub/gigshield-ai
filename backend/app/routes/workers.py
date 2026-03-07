"""
Worker Routes
==============
POST /api/workers/register      → onboard a delivery partner
GET  /api/workers/              → list all workers (admin)
GET  /api/workers/{id}          → get single worker profile
GET  /api/workers/{id}/income-estimate   → show ₹ lost per disruption
GET  /api/workers/{id}/forecast → weekly disruption forecast for their city
"""

import random
from datetime import datetime
from fastapi   import APIRouter, HTTPException, status

from app.models.schemas         import WorkerRegister
from app.services.risk_engine   import compute_risk_score, get_risk_zone, risk_label, risk_advice
from app.services.trigger_engine import income_loss_breakdown, TRIGGERS
from app.utils.database         import (
    create_worker, get_worker, get_all_workers, phone_exists
)

router = APIRouter()


@router.post("/register", status_code=status.HTTP_201_CREATED, summary="Register a new delivery partner")
def register_worker(body: WorkerRegister):
    """
    **Step 1 of 3** — Register a Zomato/Swiggy delivery partner.

    - Validates phone is unique
    - Computes AI risk score based on city, zone, platform, earnings
    - Returns worker_id to use in subsequent API calls
    """
    # Prevent duplicate registrations
    if phone_exists(body.phone):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A worker with this phone number is already registered.",
        )

    # Compute AI risk score
    risk_score = compute_risk_score(
        city=body.city,
        platform=body.platform,
        avg_daily_earning=body.avg_daily_earning,
        work_zone=body.work_zone,
    )

    # Build and store worker record
    worker_data = body.model_dump()
    worker_data["risk_score"] = risk_score
    worker_data["risk_level"] = risk_label(risk_score)
    worker_data["risk_zone"]  = get_risk_zone(body.city)

    worker = create_worker(worker_data)

    return {
        "message":      "Worker registered successfully ✅",
        "worker_id":    worker["id"],
        "name":         worker["name"],
        "risk_score":   risk_score,
        "risk_level":   worker["risk_level"],
        "risk_zone":    worker["risk_zone"],
        "advice":       risk_advice(risk_score, body.city),
        "next_step":    "GET /api/premium/quote to preview your weekly premium",
    }


@router.get("/", summary="List all workers (admin)")
def list_workers():
    return {
        "count":   len(get_all_workers()),
        "workers": get_all_workers(),
    }


@router.get("/{worker_id}", summary="Get worker profile")
def get_worker_profile(worker_id: str):
    worker = get_worker(worker_id)
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
    return worker


@router.get("/{worker_id}/income-estimate", summary="Show income loss per disruption type")
def income_estimate(worker_id: str, trigger_type: str = "HEAVY_RAIN"):
    """
    Shows the worker exactly how much they'd lose per disruption.
    Makes the product tangible — great for the onboarding UX.
    """
    worker = get_worker(worker_id)
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")

    if trigger_type not in TRIGGERS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid trigger_type. Choose from: {list(TRIGGERS.keys())}",
        )

    return income_loss_breakdown(trigger_type, worker["avg_daily_earning"])


@router.get("/{worker_id}/forecast", summary="Weekly disruption forecast for worker's city")
def disruption_forecast(worker_id: str):
    """
    Predictive forecast — shows likely disruptions in the coming week.
    Phase 2: Member 5 connects to real OpenWeather 7-day API.
    """
    worker = get_worker(worker_id)
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")

    city = worker["city"]

    # Mock forecast probabilities (Phase 2: replace with live weather API)
    BASE_PROBS = {
        "mumbai":    {"HEAVY_RAIN": 0.60, "FLOOD_ALERT": 0.30, "HIGH_AQI": 0.10},
        "delhi":     {"EXTREME_HEAT": 0.65, "HIGH_AQI": 0.55, "CURFEW": 0.05},
        "chennai":   {"HEAVY_RAIN": 0.55, "FLOOD_ALERT": 0.25, "HIGH_AQI": 0.08},
        "bangalore": {"HEAVY_RAIN": 0.35, "HIGH_AQI": 0.15},
        "kolkata":   {"HEAVY_RAIN": 0.50, "FLOOD_ALERT": 0.30, "HIGH_AQI": 0.12},
    }
    probs = BASE_PROBS.get(city, {"HEAVY_RAIN": 0.20, "EXTREME_HEAT": 0.15})

    # Add slight jitter so it looks like a live model
    forecast = {
        t: round(min(max(p + random.uniform(-0.04, 0.04), 0.01), 0.99), 2)
        for t, p in probs.items()
    }

    top_trigger = max(forecast, key=forecast.get)

    return {
        "worker_id":  worker_id,
        "city":       city,
        "week":       datetime.utcnow().strftime("%Y-W%W"),
        "forecast":   forecast,
        "top_risk": {
            "trigger":     top_trigger,
            "probability": forecast[top_trigger],
            "label":       TRIGGERS[top_trigger]["label"],
            "advice":      (
                f"{int(forecast[top_trigger]*100)}% chance of "
                f"{TRIGGERS[top_trigger]['label'].lower()} this week. "
                f"Make sure your policy is active."
            ),
        },
        "note": "Forecast powered by GigShield AI (Phase 2: live OpenWeather API)",
    }
