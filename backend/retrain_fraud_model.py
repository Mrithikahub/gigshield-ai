"""
TriggerPe — Fraud Model Retraining Script (Phase 2)
Run this from the backend folder:
    python retrain_fraud_model.py
"""
import os
import joblib
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

MODEL_PATH = os.path.join("app", "ai_models", "fraud_model.pkl")
os.makedirs(os.path.join("app", "ai_models"), exist_ok=True)

np.random.seed(42)
N = 2000

# ── Synthetic training data ───────────────────────────────────────────────────
claim_amount     = np.random.uniform(100, 800, N)
risk_score       = np.random.uniform(0.1, 0.9, N)
disruption_count = np.random.randint(0, 8, N)
past_claims      = np.random.randint(0, 20, N)
avg_claim        = np.random.uniform(100, 600, N)
days_since       = np.random.randint(0, 365, N)
velocity_1h      = np.random.randint(0, 4, N)
has_gps          = np.random.choice([0, 1], N, p=[0.25, 0.75])
is_auto          = np.random.choice([0, 1], N, p=[0.30, 0.70])
amount_deviation = np.abs(claim_amount - avg_claim) / np.maximum(avg_claim, 1)

# Fraud label logic (realistic rules)
fraud = (
    (disruption_count >= 5).astype(int) * 2 +
    (velocity_1h >= 2).astype(int) * 3 +
    (has_gps == 0).astype(int) * 1 +
    (claim_amount > 600).astype(int) * 1 +
    (amount_deviation > 0.6).astype(int) * 2 +
    (is_auto == 0).astype(int) * 1
)
# Binary: 1 = fraud if score >= 4
y = (fraud >= 4).astype(int)

print(f"Dataset: {N} samples | Fraud rate: {y.mean()*100:.1f}%")

X = pd.DataFrame({
    "claim_amount":     claim_amount,
    "risk_score":       risk_score,
    "disruption_count": disruption_count,
    "past_claims":      past_claims,
    "avg_claim":        avg_claim,
    "days_since":       days_since,
    "velocity_1h":      velocity_1h,
    "has_gps":          has_gps,
    "is_auto":          is_auto,
    "amount_deviation": amount_deviation,
})

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestClassifier(
    n_estimators=200,
    max_depth=8,
    min_samples_split=5,
    class_weight="balanced",
    random_state=42,
)
model.fit(X_train, y_train)

y_pred   = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print(f"\nModel accuracy: {accuracy*100:.1f}%")
print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=["Legit", "Fraud"]))

print("\nFeature Importances:")
for feat, imp in sorted(zip(X.columns, model.feature_importances_), key=lambda x: -x[1]):
    print(f"  {feat:<22} {imp:.3f}")

joblib.dump(model, MODEL_PATH)
print(f"\nModel saved to: {MODEL_PATH}")
