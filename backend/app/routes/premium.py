"""
Premium Routes
===============
GET  /api/premium/quote         → preview premium before buying (no auth needed)
GET  /api/premium/calculate     → calculate for a registered worker by ID
GET  /api/premium/thresholds    → see all trigger definitions
"""

from fastapi  import APIRouter, HTTPException, Query
from app.models.schemas              import PremiumQuoteRequest
from app.services.premium_calculator import get_premium_quote, calculate_premium
from app.services.risk_engine        import compute_risk_score
from app.services.trigger_engine     import TRIGGERS
from app.utils.database              import get_worker

router = APIRouter()


@router.post("/quote", summary="Get premium quote (before registering)")
def premium_quote(body: PremiumQuoteRequest):
    """
    **Pre-signup quote** — let users see their premium before committing.
    No worker_id needed. Great for the landing page / onboarding funnel.

    Returns:
    - `risk_level`  — Low / Medium / High
    - `premium`     — weekly INR amount
    - `coverage`    — payout per event
    - `breakdown`   — itemised cost
    - `advice`      — AI recommendation
    """
    return get_premium_quote(
        city=body.city,
        platform=body.platform,
        work_zone=body.work_zone,
        avg_daily_earning=body.avg_daily_earning,
    )


@router.get("/calculate", summary="Calculate premium for a registered worker")
def calculate_for_worker(worker_id: str = Query(..., description="Worker ID from /register")):
    """
    Recalculate premium for an existing worker.
    Useful when the worker wants to renew or see current pricing.

    Returns:
    - `risk_level`
    - `premium`
    - full `breakdown`
    """
    worker = get_worker(worker_id)
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")

    risk_score = compute_risk_score(
        city=worker["city"],
        platform=worker["platform"],
        avg_daily_earning=worker["avg_daily_earning"],
        work_zone=worker["work_zone"],
    )

    quote = get_premium_quote(
        city=worker["city"],
        platform=worker["platform"],
        work_zone=worker["work_zone"],
        avg_daily_earning=worker["avg_daily_earning"],
    )

    return {
        "worker_id":    worker_id,
        "worker_name":  worker["name"],
        **quote,
    }


@router.get("/thresholds", summary="View all parametric trigger definitions")
def get_trigger_thresholds():
    """
    Returns all disruption types, thresholds, and payout multipliers.
    Useful for the frontend to display coverage info to users.
    """
    return {
        "triggers": TRIGGERS,
        "note": "Payout = coverage_per_event × payout_multiplier",
    }
