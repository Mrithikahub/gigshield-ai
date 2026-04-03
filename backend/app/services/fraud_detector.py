import os
import joblib
import pandas as pd
from datetime import datetime, timedelta

# 🔑 USE ENV VARIABLES
REJECT_THRESHOLD = float(os.getenv("FRAUD_REJECT_THRESHOLD", 0.65))
REVIEW_THRESHOLD = float(os.getenv("FRAUD_REVIEW_THRESHOLD", 0.35))

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "ai_models", "fraud_model.pkl")
_model = None

def _load_model():
    global _model
    if _model is None:
        try:  # ← ADD error handling
            if os.path.exists(MODEL_PATH):
                _model = joblib.load(MODEL_PATH)
                print(f"✅ Fraud model loaded from {MODEL_PATH}")
            else:
                print(f"⚠️ Model not found at {MODEL_PATH}")
        except Exception as e:
            print(f"❌ Failed to load model: {e}")
            _model = None
    return _model

# ... rest of your code stays the same ...

def detect_fraud(worker_id, trigger_type, amount, location, gps_lat=None, gps_lng=None):
    from app.utils.database import get_worker_claims, duplicate_exists

    score = 0.0
    flags = []

    all_claims = get_worker_claims(worker_id)
    recent_7d = [c for c in all_claims if c["created_at"] >= datetime.utcnow() - timedelta(days=7)]
    
    # ... your existing rules code ...

    model = _load_model()
    if model:  # ← Only use model if loaded successfully
        try:
            input_df = pd.DataFrame([{
                "claim_amount": amount,
                "risk_score": 0.5,
                "disruption_count": len(recent_7d),
                "past_claims": len(all_claims),
                "avg_claim": sum(c["amount"] for c in all_claims) / max(len(all_claims), 1),
                "days_since": (datetime.utcnow() - all_claims[-1]["created_at"]).days if all_claims else 999,
            }])
            pred = model.predict(input_df)[0]
            if pred == 1:
                score = min(score + 0.40, 1.0)
                flags.append("ML_FRAUD_DETECTED")
        except Exception as e:
            print(f"ML prediction error: {e}")  # ← Log error but continue

    score = round(min(score, 1.0), 2)
    status = "rejected" if score >= REJECT_THRESHOLD else "review" if score >= REVIEW_THRESHOLD else "approved"
    return score, flags, status