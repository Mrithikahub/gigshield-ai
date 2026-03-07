"""
Payout Service
===============
Simulates instant UPI payout after a claim is approved.

Phase 2: Member 5 replaces process_payout() with Razorpay sandbox:

    import razorpay
    client = razorpay.Client(auth=(RAZORPAY_KEY, RAZORPAY_SECRET))
    result = client.payout.create({
        "account_number": "...",
        "fund_account_id": worker_razorpay_fund_id,
        "amount": int(amount * 100),   # paise
        "currency": "INR",
        "mode": "UPI",
        "purpose": "payout",
        "narration": f"GigShield claim {claim_id}",
    })
"""

import uuid
from datetime import datetime


def process_payout(
    worker_id: str,
    claim_id:  str,
    amount:    float,
    phone:     str,
) -> dict:
    """
    Simulated UPI payout.
    Returns a receipt dict identical to what Razorpay would return.
    """
    if amount <= 0:
        return {
            "status":  "skipped",
            "reason":  "Zero payout amount",
            "amount":  0,
        }

    transaction_id = "TXN" + str(uuid.uuid4())[:10].upper()
    upi_id         = f"{phone}@upi"

    return {
        "transaction_id": transaction_id,
        "upi_id":         upi_id,
        "amount_inr":     amount,
        "currency":       "INR",
        "mode":           "UPI",
        "status":         "success",
        "worker_id":      worker_id,
        "claim_id":       claim_id,
        "processed_at":   datetime.utcnow().isoformat() + "Z",
        "note":           f"GigShield income protection payout (simulated)",
    }
