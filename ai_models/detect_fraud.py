import joblib
import pandas as pd

# load trained fraud model
model = joblib.load("fraud_model.pkl")


def detect_fraud(location_mismatch,
                 claim_frequency,
                 weather_match,
                 time_anomaly,
                 gps_speed):

    fraud_score = 0

    # Rule-based anomaly checks
    if location_mismatch == 1:
        fraud_score += 2

    if claim_frequency > 3:
        fraud_score += 2

    if weather_match == 0:
        fraud_score += 2

    if time_anomaly == 1:
        fraud_score += 1

    if gps_speed > 100:
        fraud_score += 1

    # ML model prediction
    input_data = pd.DataFrame([{
        "location_mismatch": location_mismatch,
        "claim_frequency": claim_frequency,
        "weather_match": weather_match,
        "time_anomaly": time_anomaly,
        "gps_speed": gps_speed
    }])

    prediction = model.predict(input_data)

    # Combine ML + rule-based detection
    if prediction[0] == 1 or fraud_score >= 3:
        return "Fraudulent Claim"

    return "Normal Claim"


# test example
if __name__ == "__main__":

    result = detect_fraud(
        location_mismatch=1,
        claim_frequency=6,
        weather_match=0,
        time_anomaly=1,
        gps_speed=130
    )

    print("Fraud Detection Result:", result)