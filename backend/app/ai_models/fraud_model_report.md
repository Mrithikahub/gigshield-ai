# TriggerPe — Fraud Model Report

Generated: 2026-04-16 | Environment: Python 3.10, scikit-learn 1.7.2, numpy 1.24.3

---

## Models in Use

| File | Type | Version | Purpose |
|---|---|---|---|
| `fraud_model.pkl` | RandomForestClassifier | v1 (Phase 2) | Rule augmentation — binary fraud flag |
| `fraud_model_v2.pkl` | IsolationForest | v2 (Phase 3) | Behavioral anomaly detection |
| `fraud_training_data.csv` | Synthetic dataset | Phase 3 | IsolationForest training data |

---

## v1 — RandomForestClassifier

### Training Parameters
```
n_estimators   : 200
max_depth      : 8
min_samples_split: 5
class_weight   : balanced
random_state   : 42
Training samples: 1600 (80% of 2000)
Test samples   : 400  (20% of 2000)
Fraud rate     : 55.6%
```

### Performance (Test Set)
```
Accuracy  : 99.5%

              precision  recall  f1-score  support
Legit           0.99      1.00      0.99      159
Fraud           1.00      0.99      1.00      241

macro avg       0.99      1.00      0.99      400
weighted avg    1.00      0.99      1.00      400
```

### Feature Importances
| Feature | Importance |
|---|---|
| velocity_1h | 0.370 |
| amount_deviation | 0.183 |
| disruption_count | 0.146 |
| claim_amount | 0.080 |
| is_auto | 0.077 |
| has_gps | 0.060 |
| avg_claim | 0.035 |
| risk_score | 0.019 |
| days_since | 0.017 |
| past_claims | 0.012 |

### Input Features
| Feature | Source |
|---|---|
| `claim_amount` | Claim body |
| `risk_score` | Worker risk score (hardcoded 0.5 neutral) |
| `disruption_count` | Worker's 7-day claim count |
| `past_claims` | Total historical claims |
| `avg_claim` | Mean historical claim amount |
| `days_since` | Days since last claim |
| `velocity_1h` | Claims in last 1 hour |
| `has_gps` | 1 if GPS provided, else 0 |
| `is_auto` | 1 if auto-triggered, else 0 |
| `amount_deviation` | abs(amount - avg_claim) / avg_claim |

### Integration
- Loaded lazily on first request, cached globally
- Contributes `+0.40` to fraud score when `predict() == 1`
- Appends `ML_FRAUD_DETECTED` flag

---

## v2 — IsolationForest (Behavioral Anomaly)

### Training Parameters
```
n_estimators  : 100
contamination : 0.15   (15% fraud rate in synthetic data)
random_state  : 42
Training rows : 5000 (synthetic)
Fraud rows    : 750  (15%)
Legit rows    : 4250 (85%)
```

### Dataset: fraud_training_data.csv
```
Total rows : 5000
Fraud rows : 750  (15.0%)
Legit rows : 4250 (85.0%)
Features   : 8
```

### Feature Columns (order fixed — do not change)
| # | Feature | Description |
|---|---|---|
| 1 | `claims_per_month` | Approximate monthly claim rate (7d count × 4) |
| 2 | `avg_payout_requested` | Mean historical claim amount |
| 3 | `trigger_type_diversity` | Unique trigger types seen across all claims |
| 4 | `time_between_claims_hours` | Hours since last claim (999 if first claim) |
| 5 | `zone_risk_score` | City risk zone score (0–100) |
| 6 | `platform_tenure_months` | Platform tenure in months (default: 12) |
| 7 | `gps_mismatch_count` | Number of GPS mismatches detected |
| 8 | `ip_city_mismatch_count` | Number of IP/city contradictions (default: 0) |

### Output
- `score_behavior()` returns a float in **[0.0, 1.0]**
- Score derived from IsolationForest `decision_function` normalized to [0,1]
- Score > 0.6 triggers behavioral anomaly boost: `+behavioral_score × 0.30`
- Appends flag: `BEHAVIORAL_ANOMALY_{score:.2f}`

### Fraud Profile (high-risk behavioral pattern)
```
claims_per_month          >= 8
avg_payout_requested      >= 1500
trigger_type_diversity    <= 1  (single-type spamming)
time_between_claims_hours <= 6
zone_risk_score           <= 20
platform_tenure_months    <= 2
gps_mismatch_count        >= 2
ip_city_mismatch_count    >= 1
```

### Reason Codes Generated
The behavioral model contributes to the following audit reason codes:
- `BEHAVIORAL_ANOMALY_{score}` — when score > 0.6
- `HIGH_FREQUENCY_{N}_IN_7D` — from Rule 2 (claim frequency)
- `VELOCITY_SPIKE_{N}_IN_1H` — from Rule 3 (velocity)
- `GPS_SPOOF_DETECTED` — when Haversine deviation > 5km
- `GPS_LOCATION_MISMATCH` — when GPS outside city bounding box
- `HISTORICAL_WEATHER_MISMATCH` — when archive data contradicts trigger claim
- `ML_FRAUD_DETECTED` — when v1 RandomForest predicts fraud (class=1)

---

## Fraud Scoring Pipeline

```
score = 0.0

Rule 1: DUPLICATE_CLAIM_TODAY       +0.50
Rule 2: HIGH_FREQUENCY_N_IN_7D      +0.25  (if >= 4 claims in 7 days)
Rule 3: VELOCITY_SPIKE_N_IN_1H      +0.30  (if >= 2 claims in 1 hour)
Rule 4: GPS_LOCATION_MISMATCH       +0.40  (bounding box check)
Rule 4b: GPS_SPOOF_DETECTED         +0.40  (Haversine > 5km)
Rule 5: ABNORMAL_AMOUNT             +0.20  (amount > 500)
Rule 6: WEATHER_NOT_VERIFIED        +0.45  (live weather check, manual only)
Rule 6b: HISTORICAL_WEATHER_MISMATCH +0.35 (archive check, manual only)
Rule 7: AMOUNT_DEVIATION_HIGH       +0.15  (>50% deviation from history)
ML v1:  ML_FRAUD_DETECTED           +0.40  (RandomForest predict==1)
ML v2:  BEHAVIORAL_ANOMALY          +behavioral_score × 0.30 (if score > 0.6)

Final = min(score, 1.0)

Decision:
  >= 0.65  -> rejected
  >= 0.35  -> review
  <  0.35  -> approved
```

---

## Known Limitations

| # | Limitation | Impact | Mitigation |
|---|---|---|---|
| 1 | `risk_score` hardcoded to 0.5 in `detect_fraud()` | Neutral, not worker-specific | Worker risk_score available in DB; future enhancement |
| 2 | `platform_tenure_months` hardcoded to 12 | Neutral default | Not stored in DB; requires platform API integration |
| 3 | `ip_city_mismatch_count` hardcoded to 0 | IP enrichment not yet live | Architecture ready; plug in IP-to-city API |
| 4 | HIGH_AQI, CURFEW, STRIKE, PROTEST not in Open-Meteo | No weather historical boost for these triggers | By design — social events not weather-measurable |
| 5 | Open-Meteo archive ~5-day lag | Recent same-day claims return valid=None | Graceful skip, no false fraud signal |
| 6 | v1 model fraud rate 55.6% (synthetic) | May over-flag in low-fraud environments | Retrain with real production data when available |
