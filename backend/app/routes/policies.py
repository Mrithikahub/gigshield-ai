"""
Policy Routes
==============
POST /api/policies/create           → buy weekly insurance
GET  /api/policies/active/{id}      → check if worker is currently covered
GET  /api/policies/worker/{id}      → all policies for a worker (history)
GET  /api/policies/                 → all policies (admin)
"""

from fastapi   import APIRouter, HTTPException, status
from datetime  import datetime, timedelta

from app.models.schemas              import PolicyCreate
from app.services.premium_calculator import calculate_premium
from app.services.risk_engine        import compute_risk_score
from app.utils.database              import (
    create_policy, get_worker, get_active_policy,
    get_worker_policies, get_all_policies,
)

router = APIRouter()


@router.post("/create", status_code=status.HTTP_201_CREATED, summary="Create a weekly insurance policy")
def create_insurance_policy(body: PolicyCreate):
    """
    **Step 3 of 3** — Activate weekly income protection.

    - Worker must be registered first
    - Cannot have two active policies at the same time
    - Premium is dynamically calculated using AI risk score
    - Coverage amount = min(80% of daily earning, ₹400 per event)
    """
    worker = get_worker(body.worker_id)
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found. Register first.")

    # Block duplicate active policy
    existing = get_active_policy(body.worker_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Worker already has active policy {existing['id']} "
                f"valid until {existing['end_date'].strftime('%Y-%m-%d')}. "
                f"Renew after it expires."
            ),
        )

    # Dynamic premium via AI
    risk_score = worker["risk_score"]
    premium, coverage, breakdown = calculate_premium(
        city=worker["city"],
        avg_daily_earning=worker["avg_daily_earning"],
        risk_score=risk_score,
    )

    now   = datetime.utcnow()
    end   = now + timedelta(weeks=body.weeks)

    policy = create_policy({
        "worker_id":          body.worker_id,
        "weeks":              body.weeks,
        "weekly_premium":     premium,
        "total_premium":      round(premium * body.weeks, 2),
        "coverage_per_event": coverage,
        "start_date":         now,
        "end_date":           end,
        "status":             "active",
        "breakdown":          breakdown,
    })

    return {
        "message":            "Policy activated ✅ You are now protected.",
        "policy_id":          policy["id"],
        "worker_name":        worker["name"],
        "weekly_premium":     premium,
        "total_charged":      policy["total_premium"],
        "coverage_per_event": coverage,
        "valid_from":         now.strftime("%Y-%m-%d"),
        "valid_until":        end.strftime("%Y-%m-%d"),
        "premium_breakdown":  breakdown,
        "next_step":          "Disruptions are now monitored. Payouts are automatic.",
    }


@router.get("/active/{worker_id}", summary="Check if worker has active coverage")
def check_active_policy(worker_id: str):
    """Used by frontend to show coverage status badge (active/inactive)."""
    if not get_worker(worker_id):
        raise HTTPException(status_code=404, detail="Worker not found")
    policy = get_active_policy(worker_id)
    if not policy:
        raise HTTPException(status_code=404, detail="No active policy. Buy coverage first.")
    return policy


@router.get("/worker/{worker_id}", summary="Get all policies for a worker")
def worker_policy_history(worker_id: str):
    if not get_worker(worker_id):
        raise HTTPException(status_code=404, detail="Worker not found")
    return get_worker_policies(worker_id)


@router.get("/", summary="List all policies (admin)")
def list_all_policies():
    all_p = get_all_policies()
    return {
        "count":    len(all_p),
        "active":   sum(1 for p in all_p if p["status"] == "active"),
        "policies": all_p,
    }
