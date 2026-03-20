import os
import joblib
import pandas as pd
from datetime import datetime, timedelta

# Use ENV variables
REJECT_THRESHOLD = float(os.getenv("FRAUD_REJECT_THRESHOLD", 0.65))
REVIEW_THRESHOLD = float(os.getenv("FRAUD_REVIEW_THRESHOLD", 0.35))

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "ai_models", "fraud_model.pkl")
_model = None

# Safe sklearn import for Render deployment
try:
    from sklearn.ensemble import RandomForestClassifier
except ImportError:
    class RandomForestClassifier:
        pass

CITY_BOUNDS = {
    "mumbai":    (18.85, 19.35, 72.75, 73.05),
    "delhi":     (28.40, 28.90, 76.85, 77.40),
    "chennai":   (12.85, 13.25, 80.10, 80.35),
    "bangalore": (12.80, 13.15, 77.45, 77.80),
    "hyderabad": (17.25, 17.65, 78.25, 78.65),
    "kolkata":   (22.40, 22.70, 88.20, 88.50),
    "pune":      (18.40, 18.65, 73.75, 74.05),
}

def _gps_valid(city, lat, lng):
    bounds = CITY_BOUNDS.get(city.lower())
    if not bounds: return True
    return bounds[0] <= lat <= bounds[1] and bounds[2] <= lng <= bounds[3]

def _load_model():
    global _model
    if _model is None:
        try:
            if os.path.exists(MODEL_PATH):
                _model = joblib.load(MODEL_PATH)
                print(f"✅ Fraud model loaded from {MODEL_PATH}")
            else:
                print(f"⚠️ Model not found at {MODEL_PATH}")
        except Exception as e:
            print(f"❌ Failed to load model: {e}")
            _model = None
    return _model


def detect_fraud(worker_id, trigger_type, amount, location, gps_lat=None, gps_lng=None):
    from app.utils.database import get_worker_claims, duplicate_exists

    score = 0.0
    flags = []

    all_claims    = get_worker_claims(worker_id)
    recent_7d     = [c for c in all_claims if c["created_at"] >= datetime.utcnow() - timedelta(days=7)]
    past_claims   = len(all_claims)
    claim_freq    = len(recent_7d)
    avg_claim     = sum(c["amount"] for c in all_claims) / max(len(all_claims), 1)
    days_since    = (datetime.utcnow() - all_claims[-1]["created_at"]).days if all_claims else 999

    # Rule 1: Duplicate claim today
    if duplicate_exists(worker_id, trigger_type):
        score += 0.50
        flags.append("DUPLICATE_CLAIM_TODAY")

    # Rule 2: Too many claims in 7 days
    if claim_freq >= 4:
        score += 0.25
        flags.append(f"HIGH_FREQUENCY_{claim_freq}_IN_7D")

    # Rule 3: GPS validation
    if gps_lat and gps_lng and not _gps_valid(location, gps_lat, gps_lng):
        score += 0.40
        flags.append("LOCATION_MISMATCH")
    elif not gps_lat:
        score += 0.10
        flags.append("NO_GPS")

    # Rule 4: Abnormal amount
    if amount > 500:
        score += 0.20
        flags.append("ABNORMAL_AMOUNT")

    # ML model (optional — runs only if model loaded successfully)
    model = _load_model()
    if model:
        try:
            input_df = pd.DataFrame([{
                "claim_amount":     amount,
                "risk_score":       0.5,
                "disruption_count": claim_freq,
                "past_claims":      past_claims,
                "avg_claim":        avg_claim,
                "days_since":       days_since,
            }])
            pred = model.predict(input_df)[0]
            if pred == 1:
                score = min(score + 0.40, 1.0)
                flags.append("ML_FRAUD_DETECTED")
        except Exception as e:
            print(f"ML prediction error: {e}")

    score  = round(min(score, 1.0), 2)
    status = "rejected" if score >= REJECT_THRESHOLD else "review" if score >= REVIEW_THRESHOLD else "approved"
    return score, flags, status
