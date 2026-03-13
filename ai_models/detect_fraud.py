import joblib
import pandas as pd
from datetime import datetime, timedelta

# load trained fraud model
model = joblib.load("fraud_model.pkl")

# simple memory store for past claims
claim_history = []

def detect_fraud(location_mismatch,
                 claim_frequency,
                 weather_match,
                 time_anomaly,
                 gps_speed,
                 worker_id,
                 disruption_type,
                 location):

    fraud_score = 0

    # ---------------------------
    # Rule-based anomaly checks
    # ---------------------------

    if location_mismatch == 1:
        fraud_score += 2

    if claim_frequency > 3:
        fraud_score += 2

    if weather_match == 0:
        fraud_score += 3   # strong signal

    if time_anomaly == 1:
        fraud_score += 1

    if gps_speed > 100:
        fraud_score += 1

    # ---------------------------
    # Duplicate claim detection
    # ---------------------------

    current_time = datetime.now()

    for claim in claim_history:

        if (claim["worker_id"] == worker_id and
            claim["disruption_type"] == disruption_type and
            claim["location"] == location):

            time_diff = current_time - claim["time"]

            if time_diff < timedelta(hours=1):
                fraud_score += 3

    # ---------------------------
    # ML model prediction
    # ---------------------------

    input_data = pd.DataFrame([{
        "location_mismatch": location_mismatch,
        "claim_frequency": claim_frequency,
        "weather_match": weather_match,
        "time_anomaly": time_anomaly,
        "gps_speed": gps_speed
    }])

    prediction = model.predict(input_data)

    # ---------------------------
    # Store claim history
    # ---------------------------

    claim_history.append({
        "worker_id": worker_id,
        "disruption_type": disruption_type,
        "location": location,
        "time": current_time
    })

    # ---------------------------
    # Final fraud decision
    # ---------------------------

    if prediction[0] == 1 or fraud_score >= 3:
        return "Fraudulent Claim"

    return "Normal Claim"


# ---------------------------
# Test example
# ---------------------------

if __name__ == "__main__":

    result = detect_fraud(
        location_mismatch=1,
        claim_frequency=5,
        weather_match=0,
        time_anomaly=1,
        gps_speed=120,
        worker_id=101,
        disruption_type="Heavy Rain",
        location="Chennai"
    )

    print("Fraud Detection Result:", result)