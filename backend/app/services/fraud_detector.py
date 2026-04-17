"""
TriggerPe - Fraud Detector (Phase 3 Upgrade)
Adds: GPS spoof detection, historical weather validation, behavioral IsolationForest (v2)
Preserves: all existing rule-based checks and RandomForest (v1) model intact.
"""
import os
import joblib
import requests
import numpy as np
import pandas as pd
from math import radians, sin, cos, sqrt, atan2
from datetime import datetime, timedelta

# -- Thresholds (env-configurable) ---------------------------------------------
REJECT_THRESHOLD = float(os.getenv("FRAUD_REJECT_THRESHOLD", 0.65))
REVIEW_THRESHOLD = float(os.getenv("FRAUD_REVIEW_THRESHOLD", 0.35))

# -- Model paths ----------------------------------------------------------------
_MODELS_DIR           = os.path.join(os.path.dirname(__file__), "..", "ai_models")
MODEL_PATH            = os.path.join(_MODELS_DIR, "fraud_model.pkl")       # v1 RandomForest
BEHAVIORAL_MODEL_PATH = os.path.join(_MODELS_DIR, "fraud_model_v2.pkl")    # v2 IsolationForest
BEHAVIORAL_DATA_PATH  = os.path.join(_MODELS_DIR, "fraud_training_data.csv")

_model            = None   # v1 RandomForest (lazy-loaded)
_behavioral_model = None   # v2 IsolationForest (lazy-loaded / lazy-trained)

try:
    from sklearn.ensemble import RandomForestClassifier, IsolationForest
except ImportError:
    class RandomForestClassifier:  # type: ignore
        pass
    class IsolationForest:         # type: ignore
        pass

# -- GPS city bounding boxes: (lat_min, lat_max, lng_min, lng_max) --------------
CITY_BOUNDS = {
    "mumbai":    (18.85, 19.35, 72.75, 73.05),
    "delhi":     (28.40, 28.90, 76.85, 77.40),
    "chennai":   (12.85, 13.25, 80.10, 80.35),
    "bangalore": (12.80, 13.15, 77.45, 77.80),
    "hyderabad": (17.25, 17.65, 78.25, 78.65),
    "kolkata":   (22.40, 22.70, 88.20, 88.50),
    "pune":      (18.40, 18.65, 73.75, 74.05),
    "ahmedabad": (22.90, 23.15, 72.45, 72.75),
    "jaipur":    (26.75, 27.05, 75.65, 76.00),
    "surat":     (21.10, 21.35, 72.75, 73.05),
    "lucknow":   (26.75, 27.05, 80.85, 81.10),
    "nagpur":    (21.05, 21.30, 79.00, 79.25),
}

# City centroids derived from CITY_BOUNDS (used for Haversine GPS spoof check)
CITY_COORDS = {
    city: ((b[0] + b[1]) / 2.0, (b[2] + b[3]) / 2.0)
    for city, b in CITY_BOUNDS.items()
}

# Open-Meteo daily variable mapping per trigger type (free API, no key required)
# Delay note: archive data has ~5-day lag; returns gracefully for recent dates
TRIGGER_WEATHER_MAP = {
    "HEAVY_RAIN":   ("precipitation_sum",  50.0),
    "FLOOD_ALERT":  ("precipitation_sum", 100.0),
    "EXTREME_HEAT": ("temperature_2m_max", 42.0),
    "STRONG_WIND":  ("windspeed_10m_max",  45.0),
    "HIGH_AQI":     (None, None),   # AQI not available on Open-Meteo free tier
    "CURFEW":       (None, None),
    "STRIKE":       (None, None),
    "PROTEST":      (None, None),
}

# Behavioral IsolationForest (v2) feature columns - order must remain constant
BEHAVIORAL_FEATURE_COLS = [
    "claims_per_month",
    "avg_payout_requested",
    "trigger_type_diversity",
    "time_between_claims_hours",
    "zone_risk_score",
    "platform_tenure_months",
    "gps_mismatch_count",
    "ip_city_mismatch_count",
]


# ============ EXISTING HELPERS (UNCHANGED) ============--------

def _gps_valid(city: str, lat: float, lng: float) -> bool:
    """Bounding-box GPS city check (original Phase 2 implementation)."""
    bounds = CITY_BOUNDS.get(city.strip().lower())
    if not bounds:
        return True
    return bounds[0] <= lat <= bounds[1] and bounds[2] <= lng <= bounds[3]


def _load_model():
    """Lazy-load v1 RandomForest fraud model."""
    global _model
    if _model is None:
        try:
            if os.path.exists(MODEL_PATH):
                _model = joblib.load(MODEL_PATH)
                print(f"[FraudDetector] v1 model loaded: {MODEL_PATH}")
        except Exception as e:
            print(f"[FraudDetector] Failed to load v1 model: {e}")
            _model = None
    return _model


def _weather_validates_claim(city: str, trigger_type: str) -> bool:
    """Live weather cross-validation (original Phase 2 implementation)."""
    try:
        from app.services.trigger_engine import fetch_live_weather, THRESHOLDS
        weather = fetch_live_weather(city)
        if not weather:
            return True

        rule = THRESHOLDS.get(trigger_type)
        if not rule:
            return True

        field_map = {
            "rainfall":    weather.get("rainfall", 0),
            "temperature": weather.get("temperature", 30),
            "aqi":         weather.get("aqi", 50),
            "wind_speed":  weather.get("wind_speed", 0),
        }
        actual = field_map.get(rule["field"], 0)
        return actual >= (rule["value"] * 0.7)
    except Exception:
        return True


# ============ PHASE 3: NEW FUNCTIONS ===================--------------

# -- 1. Haversine GPS Spoof Detection -----------------------------------------

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Compute great-circle distance in kilometres between two GPS coordinates."""
    R    = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a    = (sin(dlat / 2) ** 2
            + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2)
    return R * 2 * atan2(sqrt(a), sqrt(1.0 - a))


def check_gps_spoof(
    worker_city: str,
    current_lat: float,
    current_lon: float,
    ip_city: str = None,
) -> dict:
    """
    Detect GPS spoofing by comparing claimed GPS against the registered city centroid.

    Args:
        worker_city:  City stored in worker profile (registered location)
        current_lat:  GPS latitude submitted with the claim
        current_lon:  GPS longitude submitted with the claim
        ip_city:      Optional - city resolved from request IP (future enrichment)

    Returns:
        dict with keys: score_boost, reasons, distance_km, city_checked
    """
    city_key    = (worker_city or "").strip().lower()
    score_boost = 0.0
    reasons     = []
    distance_km = None

    city_center = CITY_COORDS.get(city_key)
    if city_center:
        lat_c, lon_c = city_center
        distance_km  = haversine_distance(lat_c, lon_c, current_lat, current_lon)
        if distance_km > 5.0:
            score_boost += 0.40
            reasons.append(
                f"GPS deviation {distance_km:.1f}km exceeds 5km city-centre threshold"
            )
    else:
        reasons.append(f"City '{worker_city}' not in GPS reference database - check skipped")

    if ip_city and (ip_city.strip().lower() != city_key):
        score_boost += 0.30
        reasons.append(
            f"IP city ({ip_city}) contradicts registered GPS city ({worker_city})"
        )

    return {
        "score_boost":  round(score_boost, 2),
        "reasons":      reasons,
        "distance_km":  round(distance_km, 2) if distance_km is not None else None,
        "city_checked": city_key,
    }


# -- 2. Historical Weather Validation (Open-Meteo, free, no API key) -----------

def validate_weather_history(city: str, date: str, trigger_type: str) -> dict:
    """
    Cross-check a trigger claim against Open-Meteo historical weather archive.

    Args:
        city:         City in which the disruption was claimed
        date:         Date of the claim in 'YYYY-MM-DD' format
        trigger_type: One of the parametric trigger keys (HEAVY_RAIN, EXTREME_HEAT, -)

    Returns:
        dict with keys: valid (bool|None), actual_value, threshold, variable, reason, score_boost
        score_boost is 0.35 when data is available and trigger threshold was NOT met.
        score_boost is 0.0  when data is unavailable or trigger was confirmed.
    """
    city_key = (city or "").strip().lower()
    coords   = CITY_COORDS.get(city_key)

    if not coords:
        return {
            "valid":       None,
            "reason":      f"City '{city}' not in historical weather reference list",
            "score_boost": 0.0,
        }

    variable, threshold = TRIGGER_WEATHER_MAP.get(trigger_type, (None, None))
    if not variable:
        return {
            "valid":       None,
            "reason":      f"Trigger '{trigger_type}' has no historical weather mapping (social/AQI triggers excluded)",
            "score_boost": 0.0,
        }

    lat, lon = coords
    url = (
        f"https://archive-api.open-meteo.com/v1/archive"
        f"?latitude={lat}&longitude={lon}"
        f"&start_date={date}&end_date={date}"
        f"&daily={variable}&timezone=Asia%2FKolkata"
    )

    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data  = resp.json()
        value = data.get("daily", {}).get(variable, [None])[0]
    except Exception as e:
        print(f"[WeatherHistory] API error for {city}/{date}: {e}")
        return {
            "valid":       None,
            "reason":      f"Historical weather API unavailable: {e}",
            "score_boost": 0.0,
        }

    if value is None:
        return {
            "valid":       None,
            "reason":      "No historical data returned - archive may have <5-day lag for recent dates",
            "score_boost": 0.0,
        }

    triggered   = bool(value >= threshold)
    score_boost = 0.0 if triggered else 0.35

    return {
        "valid":        triggered,
        "actual_value": round(float(value), 2),
        "threshold":    threshold,
        "variable":     variable,
        "reason":       (
            f"Historical {variable}={value:.2f} vs threshold={threshold} "
            f"({'CONFIRMED' if triggered else 'NOT MET - fraud signal'})"
        ),
        "score_boost":  score_boost,
    }


# -- 3. Behavioral IsolationForest (v2) ----------------------------------------

def _generate_behavioral_training_data(n: int = 5000) -> pd.DataFrame:
    """
    Generate 5 000-row synthetic training set for the IsolationForest model.
    85% legitimate workers, 15% fraud-like workers.
    CSV saved to ai_models/fraud_training_data.csv.
    """
    np.random.seed(42)
    n_legit = int(n * 0.85)  # 4250
    n_fraud = n - n_legit    # 750

    legit = pd.DataFrame({
        "claims_per_month":          np.random.poisson(2, n_legit),
        "avg_payout_requested":      np.random.normal(800, 200, n_legit).clip(100, 2000),
        "trigger_type_diversity":    np.random.randint(1, 5, n_legit),
        "time_between_claims_hours": np.random.exponential(72, n_legit).clip(1, 999),
        "zone_risk_score":           np.random.uniform(20, 80, n_legit),
        "platform_tenure_months":    np.random.randint(3, 36, n_legit),
        "gps_mismatch_count":        np.random.poisson(0.10, n_legit),
        "ip_city_mismatch_count":    np.random.poisson(0.05, n_legit),
        "label": 0,
    })

    fraud = pd.DataFrame({
        "claims_per_month":          np.random.poisson(8, n_fraud).clip(3),
        "avg_payout_requested":      np.random.normal(1800, 100, n_fraud).clip(1200, 2500),
        "trigger_type_diversity":    np.random.randint(1, 2, n_fraud),
        "time_between_claims_hours": np.random.exponential(5, n_fraud).clip(0.1, 48),
        "zone_risk_score":           np.random.uniform(10, 30, n_fraud),
        "platform_tenure_months":    np.random.randint(0, 3, n_fraud),
        "gps_mismatch_count":        np.random.poisson(3, n_fraud),
        "ip_city_mismatch_count":    np.random.poisson(2, n_fraud),
        "label": 1,
    })

    df = pd.concat([legit, fraud]).sample(frac=1, random_state=42).reset_index(drop=True)
    os.makedirs(os.path.dirname(BEHAVIORAL_DATA_PATH), exist_ok=True)
    df.to_csv(BEHAVIORAL_DATA_PATH, index=False)
    fraud_count = int(df["label"].sum())
    print(
        "[BehavioralModel] Training data saved: %d rows "
        "(%d fraud / %d legit) -> %s" % (len(df), fraud_count, len(df)-fraud_count, BEHAVIORAL_DATA_PATH)
    )
    return df


def _load_behavioral_model():
    """
    Load IsolationForest v2 from disk; trains and saves if not present.
    Never overwrites fraud_model.pkl (v1).
    """
    global _behavioral_model
    if _behavioral_model is not None:
        return _behavioral_model

    if os.path.exists(BEHAVIORAL_MODEL_PATH):
        try:
            _behavioral_model = joblib.load(BEHAVIORAL_MODEL_PATH)
            print(f"[BehavioralModel] Loaded from: {BEHAVIORAL_MODEL_PATH}")
            return _behavioral_model
        except Exception as e:
            print(f"[BehavioralModel] Load error (will retrain): {e}")

    print("[BehavioralModel] Training new IsolationForest -> fraud_model_v2.pkl ...")
    df    = _generate_behavioral_training_data()
    X     = df[BEHAVIORAL_FEATURE_COLS]
    model = IsolationForest(contamination=0.15, random_state=42, n_estimators=100)
    model.fit(X)
    os.makedirs(os.path.dirname(BEHAVIORAL_MODEL_PATH), exist_ok=True)
    joblib.dump(model, BEHAVIORAL_MODEL_PATH)
    print(f"[BehavioralModel] Saved to: {BEHAVIORAL_MODEL_PATH}")
    _behavioral_model = model
    return _behavioral_model


def score_behavior(worker_features: dict) -> float:
    """
    Run behavioral IsolationForest anomaly scoring.
    Returns float in [0.0, 1.0] - higher means more anomalous (fraud-like).
    """
    model = _load_behavioral_model()
    if model is None:
        return 0.0
    try:
        X         = pd.DataFrame([{col: worker_features.get(col, 0) for col in BEHAVIORAL_FEATURE_COLS}])
        raw_score = model.decision_function(X)[0]
        # IsolationForest: more-negative raw_score - more anomalous
        # Shift and clip to [0, 1]: raw ≈ +0.5 (normal) - 0.0; raw ≈ -0.5 (anomaly) - 1.0
        fraud_prob = float(np.clip(-raw_score + 0.5, 0.0, 1.0))
        return round(fraud_prob, 4)
    except Exception as e:
        print(f"[BehavioralModel] Scoring error: {e}")
        return 0.0


# ============ MAIN FRAUD DETECTION ====================----------------

def detect_fraud(
    worker_id:    str,
    trigger_type: str,
    amount:       float,
    location:     str,
    gps_lat:      float = None,
    gps_lng:      float = None,
    is_auto:      bool  = False,
):
    """
    Unified fraud scoring pipeline (Phase 3).
    Signature is UNCHANGED from Phase 2 - all callers remain compatible.

    Returns: (fraud_score: float, fraud_flags: list[str], status: str)
    """
    from app.utils.database import get_worker_claims, duplicate_exists, get_worker

    score = 0.0
    flags = []

    all_claims  = get_worker_claims(worker_id)
    now         = datetime.utcnow()
    recent_7d   = [c for c in all_claims if c["created_at"] >= now - timedelta(days=7)]
    recent_1h   = [c for c in all_claims if c["created_at"] >= now - timedelta(hours=1)]
    past_claims = len(all_claims)
    claim_freq  = len(recent_7d)
    avg_claim   = sum(c["amount"] for c in all_claims) / max(len(all_claims), 1)
    days_since  = (now - all_claims[-1]["created_at"]).days if all_claims else 999

    # -- Rule 1 - Duplicate claim today ----------------------------------------
    if duplicate_exists(worker_id, trigger_type):
        score += 0.50
        flags.append("DUPLICATE_CLAIM_TODAY")

    # -- Rule 2 - High frequency in 7 days -------------------------------------
    if claim_freq >= 4:
        score += 0.25
        flags.append(f"HIGH_FREQUENCY_{claim_freq}_IN_7D")

    # -- Rule 3 - Velocity spike: multiple claims in 1 hour --------------------
    if len(recent_1h) >= 2:
        score += 0.30
        flags.append(f"VELOCITY_SPIKE_{len(recent_1h)}_IN_1H")

    # -- Rule 4 - GPS bbox validation (original Phase 2) -----------------------
    gps_mismatch_count = 0
    if gps_lat and gps_lng:
        if not _gps_valid(location, gps_lat, gps_lng):
            score += 0.40
            flags.append("GPS_LOCATION_MISMATCH")
            gps_mismatch_count = 1
    elif not is_auto:
        score += 0.10
        flags.append("NO_GPS")

    # -- Rule 4b - GPS Spoof Detection via Haversine distance (Phase 3) --------
    gps_spoof_result = {"score_boost": 0.0, "reasons": [], "distance_km": None}
    if gps_lat and gps_lng and not is_auto:
        worker      = get_worker(worker_id)
        worker_city = (worker or {}).get("city", location)
        gps_spoof_result = check_gps_spoof(worker_city, gps_lat, gps_lng)
        if gps_spoof_result["score_boost"] > 0:
            score += gps_spoof_result["score_boost"]
            flags.append("GPS_SPOOF_DETECTED")
            gps_mismatch_count = max(gps_mismatch_count, 1)
            for reason in gps_spoof_result["reasons"]:
                flags.append(f"GPS_SPOOF: {reason}")

    # -- Rule 5 - Abnormal amount -----------------------------------------------
    if amount > 500:
        score += 0.20
        flags.append("ABNORMAL_AMOUNT")

    # -- Rule 6 - Live weather cross-validation (manual claims only, Phase 2) --
    if not is_auto:
        if not _weather_validates_claim(location, trigger_type):
            score += 0.45
            flags.append("WEATHER_NOT_VERIFIED")

    # -- Rule 6b - Historical weather validation (Phase 3, manual only) --------
    history_result = {"valid": None, "score_boost": 0.0, "reason": "not_checked"}
    if not is_auto:
        claim_date     = now.date().isoformat()
        history_result = validate_weather_history(location, claim_date, trigger_type)
        if history_result.get("score_boost", 0.0) > 0:
            score += history_result["score_boost"]
            flags.append("HISTORICAL_WEATHER_MISMATCH")

    # -- Rule 7 - Amount deviation from personal history -----------------------
    if past_claims >= 3 and avg_claim > 0:
        if abs(amount - avg_claim) / avg_claim > 0.5:
            score += 0.15
            flags.append("AMOUNT_DEVIATION_HIGH")

    # -- ML v1 - RandomForest (original Phase 2 model, preserved) -------------
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
                "velocity_1h":      len(recent_1h),
                "has_gps":          1 if gps_lat else 0,
                "is_auto":          1 if is_auto else 0,
                "amount_deviation": abs(amount - avg_claim) / max(avg_claim, 1),
            }])
            pred = model.predict(input_df)[0]
            if pred == 1:
                score = min(score + 0.40, 1.0)
                flags.append("ML_FRAUD_DETECTED")
        except Exception as e:
            print(f"[FraudDetector] v1 ML prediction error: {e}")

    # -- ML v2 - Behavioral IsolationForest (Phase 3) -------------------------
    trigger_types_seen  = list(set(c["trigger_type"] for c in all_claims))
    time_gap_hours      = (days_since * 24) if days_since < 999 else 999.0
    behavioral_features = {
        "claims_per_month":          claim_freq * 4,                  # approximate monthly rate
        "avg_payout_requested":      avg_claim,
        "trigger_type_diversity":    len(trigger_types_seen),
        "time_between_claims_hours": time_gap_hours,
        "zone_risk_score":           50.0,                            # neutral; enriched in audit
        "platform_tenure_months":    12,                              # not stored; neutral default
        "gps_mismatch_count":        gps_mismatch_count,
        "ip_city_mismatch_count":    0,                               # not yet tracked at request level
    }
    behavioral_score = score_behavior(behavioral_features)
    if behavioral_score > 0.6:
        behavior_boost = round(behavioral_score * 0.30, 2)
        score = min(score + behavior_boost, 1.0)
        flags.append(f"BEHAVIORAL_ANOMALY_{behavioral_score:.2f}")

    # -- Final decision ---------------------------------------------------------
    score  = round(min(score, 1.0), 2)
    status = (
        "rejected" if score >= REJECT_THRESHOLD
        else "review" if score >= REVIEW_THRESHOLD
        else "approved"
    )
    return score, flags, status
