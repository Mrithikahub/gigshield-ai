"""
Claims Routes
==============
POST /api/claims/submit             → manual claim by worker
GET  /api/claims/worker/{id}        → worker's claim history
GET  /api/claims/{claim_id}         → single claim detail
GET  /api/claims/                   → all claims (admin)
PATCH /api/claims/{id}/approve      → admin approves pending claim
PATCH /api/claims/{id}/reject       → admin rejects claim
"""
from fastapi import APIRouter, HTTPException, status

from app.models.schemas import ClaimSubmit

from app.services.fraud_detector import detect
from app.services.trigger_engine import calculate_payout
from app.services.payout_service import process_payout

from app.utils.database import (
    create_claim,
    get_claim,
    get_worker,
    get_all_claims,
    get_worker_claims,
    get_active_policy,
)
router = APIRouter()


@router.post("/submit", status_code=status.HTTP_201_CREATED, summary="Submit a manual claim")
def submit_claim(body: ClaimSubmit):
    """
    Worker manually reports a disruption event.

    - Checks that worker has an active policy
    - Runs 6-point fraud detection
    - Auto-approves clean claims + fires payout immediately
    - Flags borderline claims for manual review
    - Rejects high-fraud-score claims
    """
    worker = get_worker(body.worker_id)
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")

    policy = get_active_policy(body.worker_id)
    if not policy:
        raise HTTPException(
            status_code=400,
            detail="No active policy found. Buy a policy before filing a claim.",
        )

    # Run fraud detection
    fraud_score, fraud_flags, decision = detect(
        worker_id=body.worker_id,
        trigger_type=body.trigger_type,
        event_date=body.event_date,
        city=body.location,
        gps_lat=body.gps_lat,
        gps_lng=body.gps_lng,
    )

    # Only pay if clean
    payout_amount  = calculate_payout(body.trigger_type, policy["coverage_per_event"]) \
                     if decision == "approved" else 0.0
    payout_receipt = None

    if decision == "approved" and payout_amount > 0:
        payout_receipt = process_payout(
            worker_id=body.worker_id,
            claim_id="PENDING",
            amount=payout_amount,
            phone=worker["phone"],
        )

    claim = create_claim({
        "worker_id":      body.worker_id,
        "policy_id":      policy["id"],
        "trigger_type":   body.trigger_type,
        "event_date":     body.event_date,
        "location":       body.location,
        "payout_amount":  payout_amount,
        "status":         decision,
        "fraud_score":    fraud_score,
        "fraud_flags":    fraud_flags,
        "is_auto":        False,
        "payout_receipt": payout_receipt,
    })

    return {
        "message":        f"Claim {decision}",
        "claim_id":       claim["id"],
        "status":         decision,
        "payout_inr":     payout_amount,
        "fraud_score":    fraud_score,
        "fraud_flags":    fraud_flags,
        "payout_receipt": payout_receipt,
        "note": (
            "Payout sent instantly via UPI ✅" if decision == "approved"
            else "Under review — our team will process within 24 hrs" if decision == "pending"
            else "Claim rejected due to fraud risk ❌"
        ),
    }


@router.get("/worker/{worker_id}", summary="Get claim history for a worker")
def worker_claim_history(worker_id: str):
    if not get_worker(worker_id):
        raise HTTPException(status_code=404, detail="Worker not found")
    claims = get_worker_claims(worker_id)
    total_earned = sum(
        c["payout_amount"] for c in claims if c["status"] in ("approved", "paid")
    )
    return {
        "worker_id":     worker_id,
        "total_claims":  len(claims),
        "total_earned":  total_earned,
        "claims":        claims,
    }


@router.get("/{claim_id}", summary="Get single claim detail")
def get_claim_detail(claim_id: str):
    claim = get_claim(claim_id)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    return claim


@router.get("/", summary="List all claims (admin)")
def list_all_claims():
    all_c = get_all_claims()
    return {
        "total":    len(all_c),
        "approved": sum(1 for c in all_c if c["status"] == "approved"),
        "paid":     sum(1 for c in all_c if c["status"] == "paid"),
        "pending":  sum(1 for c in all_c if c["status"] == "pending"),
        "rejected": sum(1 for c in all_c if c["status"] == "rejected"),
        "claims":   all_c,
    }


@router.patch("/{claim_id}/approve", summary="Admin: approve a pending claim")
def approve_claim(claim_id: str):
    """Approves a claim that was flagged for manual review. Fires payout."""
    claim = get_claim(claim_id)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    if claim["status"] != "pending":
        raise HTTPException(status_code=400, detail=f"Claim status is '{claim['status']}', not 'pending'")

    worker = get_worker(claim["worker_id"])
    payout_receipt = process_payout(
        worker_id=claim["worker_id"],
        claim_id=claim_id,
        amount=claim["payout_amount"],
        phone=worker["phone"] if worker else "0000000000",
    )
    claim["status"]         = "paid"
    claim["payout_receipt"] = payout_receipt

    return {
        "message":        "Claim approved and payout sent ✅",
        "claim_id":       claim_id,
        "payout_inr":     claim["payout_amount"],
        "payout_receipt": payout_receipt,
    }


@router.patch("/{claim_id}/reject", summary="Admin: reject a fraudulent claim")
def reject_claim(claim_id: str):
    claim = get_claim(claim_id)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    if claim["status"] == "paid":
        raise HTTPException(status_code=400, detail="Cannot reject an already paid claim")
    claim["status"] = "rejected"
    return {"message": "Claim rejected ❌", "claim_id": claim_id}
