"""
ai_service.py
-------------
GigShield AI — AI Model Integration Layer
Bridges weather/disruption data with the risk and fraud ML models.
"""

import os
import joblib
import numpy as np
from dataclasses import dataclass
from typing import Optional

from disruption_detector import DisruptionReport, detect_disruptions_by_city
from weather_service import WeatherData


# ── Model Paths ───────────────────────────────────────────────────────────────

MODEL_DIR   = os.path.join(os.path.dirname(__file__), "..", "ai_models")
RISK_MODEL_PATH  = os.path.join(MODEL_DIR, "risk_model.pkl")
FRAUD_MODEL_PATH = os.path.join(MODEL_DIR, "fraud_model.pkl")


# ── Data Models ───────────────────────────────────────────────────────────────

@dataclass
class RiskAssessment:
    risk_level:    str    # "low" | "medium" | "high" | "critical"
    risk_score:    float  # 0.0 – 1.0
    base_premium:  float  # INR per day
    final_premium: float  # INR per day (after multipliers)
    multiplier:    float  # premium loading factor
    rationale:     str

    def to_dict(self) -> dict:
        return {
            "risk_level":    self.risk_level,
            "risk_score":    round(self.risk_score, 3),
            "base_premium":  round(self.base_premium, 2),
            "final_premium": round(self.final_premium, 2),
            "multiplier":    round(self.multiplier, 2),
            "rationale":     self.rationale,
        }


@dataclass
class ClaimValidation:
    claim_id:      str
    is_valid:      bool
    fraud_score:   float  # 0.0 = clean, 1.0 = likely fraud
    confidence:    float  # model confidence
    decision:      str    # "approved" | "review" | "rejected"
    reason:        str

    def to_dict(self) -> dict:
        return {
            "claim_id":    self.claim_id,
            "is_valid":    self.is_valid,
            "fraud_score": round(self.fraud_score, 3),
            "confidence":  round(self.confidence, 3),
            "decision":    self.decision,
            "reason":      self.reason,
        }


@dataclass
class AIServiceResponse:
    worker_id:   str
    city:        str
    assessment:  RiskAssessment
    disruption:  Optional[DisruptionReport] = None

    def to_dict(self) -> dict:
        return {
            "worker_id":  self.worker_id,
            "city":       self.city,
            "assessment": self.assessment.to_dict(),
            "disruption": self.disruption.to_dict() if self.disruption else None,
        }


# ── Model Loader ──────────────────────────────────────────────────────────────

class _ModelCache:
    """Lazy singleton — loads models once, reuses across calls."""
    _risk_model  = None
    _fraud_model = None

    @classmethod
    def risk_model(cls):
        if cls._risk_model is None:
            cls._risk_model = _load_model(RISK_MODEL_PATH, "risk")
        return cls._risk_model

    @classmethod
    def fraud_model(cls):
        if cls._fraud_model is None:
            cls._fraud_model = _load_model(FRAUD_MODEL_PATH, "fraud")
        return cls._fraud_model


def _load_model(path: str, name: str):
    """Load a trained ML model safely."""
    if not os.path.exists(path):
        print(f"[AIService] ⚠️ {name} model not found at {path}. Using heuristic fallback.")
        return None

    try:
        model = joblib.load(path)
        print(f"[AIService] ✅ {name} model loaded.")
        return model
    except Exception as exc:
        print(f"[AIService] ❌ Failed to load {name} model: {exc}")
        return None


# ── Feature Engineering ───────────────────────────────────────────────────────

def _build_risk_features(weather: WeatherData, disruption: DisruptionReport) -> np.ndarray:
    """
    Convert raw weather + disruption data into a flat feature vector
    matching the expected input of risk_model.pkl.

    Feature order (8 features):
        [temperature, rainfall_1h, wind_speed, humidity,
         aqi, disruption_count, risk_score, is_disrupted]
    """
    return np.array([[
        weather.temperature,
        weather.rainfall_1h,
        weather.wind_speed,
        weather.humidity,
        weather.aqi,
        len(disruption.events),
        disruption.risk_score,
        float(disruption.disrupted),
    ]])


def _build_fraud_features(
    claim_amount: float,
    disruption: DisruptionReport,
    worker_history: dict,
) -> np.ndarray:
    """
    Feature vector for fraud detection (6 features):
        [claim_amount, risk_score, disruption_count,
         past_claims_count, avg_past_claim, days_since_last_claim]
    """
    return np.array([[
        claim_amount,
        disruption.risk_score,
        len(disruption.events),
        worker_history.get("past_claims_count", 0),
        worker_history.get("avg_past_claim", 0.0),
        worker_history.get("days_since_last_claim", 999),
    ]])


# ── Heuristic Fallbacks (when models aren't loaded) ───────────────────────────

def _heuristic_risk(disruption: DisruptionReport, weather: WeatherData) -> RiskAssessment:
    """Rule-based risk scoring when the ML model is unavailable."""
    score = disruption.risk_score

    # Bump score for compound events
    if len(disruption.events) > 1:
        score = min(score * 1.3, 1.0)

    if score < 0.25:
        level, base, mult = "low",      50.0, 1.0
    elif score < 0.50:
        level, base, mult = "medium",   50.0, 1.5
    elif score < 0.75:
        level, base, mult = "high",     50.0, 2.2
    else:
        level, base, mult = "critical", 50.0, 3.5

    return RiskAssessment(
        risk_level    = level,
        risk_score    = score,
        base_premium  = base,
        final_premium = base * mult,
        multiplier    = mult,
        rationale     = (
            f"Heuristic assessment: {len(disruption.events)} disruption event(s) "
            f"detected. Risk score {score:.2f}."
        ),
    )


def _heuristic_fraud(
    claim_id: str,
    claim_amount: float,
    disruption: DisruptionReport,
    worker_history: dict,
) -> ClaimValidation:
    """Simple rule-based fraud check when ML model is unavailable."""
    fraud_score = 0.0
    reasons = []

    # Red flag: claim with no disruption
    if not disruption.disrupted:
        fraud_score += 0.6
        reasons.append("No disruption event on record for claim date/location.")

    # Red flag: claim amount suspiciously high
    avg = worker_history.get("avg_past_claim", 500.0)
    if claim_amount > avg * 3:
        fraud_score += 0.3
        reasons.append(f"Claim ₹{claim_amount:.0f} is >3× worker's average ₹{avg:.0f}.")

    # Red flag: very recent previous claim
    if worker_history.get("days_since_last_claim", 999) < 5:
        fraud_score += 0.2
        reasons.append("Previous claim filed fewer than 5 days ago.")

    fraud_score = min(fraud_score, 1.0)

    if fraud_score < 0.3:
        decision, valid = "approved", True
        reason = "Claim passes automated checks."
    elif fraud_score < 0.6:
        decision, valid = "review", False
        reason = "Flagged for manual review. " + " ".join(reasons)
    else:
        decision, valid = "rejected", False
        reason = "High fraud probability. " + " ".join(reasons)

    return ClaimValidation(
        claim_id    = claim_id,
        is_valid    = valid,
        fraud_score = fraud_score,
        confidence  = 0.75,
        decision    = decision,
        reason      = reason,
    )


# ── Public API ────────────────────────────────────────────────────────────────

def calculate_risk_and_premium(
    worker_id: str,
    city: str,
    weather: Optional[WeatherData] = None,
) -> AIServiceResponse:
    """
    Calculate risk level and daily insurance premium for a gig worker.

    Args:
        worker_id: Unique worker identifier.
        city:      City where the worker is operating (e.g. "Mumbai,IN").
        weather:   Pre-fetched WeatherData (optional — fetches live if None).

    Returns:
        AIServiceResponse with full risk assessment and disruption report.
    """
    # 1. Get disruption context
    if weather:
        from disruption_detector import detect_disruptions
        disruption = detect_disruptions(weather)
    else:
        disruption = detect_disruptions_by_city(city)
        # Reconstruct a minimal WeatherData for feature building if needed
        weather = WeatherData(
            city=city, temperature=30.0, rainfall_1h=0.0,
            wind_speed=4.0, humidity=60, description="",
            aqi=80, lat=0.0, lon=0.0,
        )

    # 2. Try ML model, fall back to heuristics
    model = _ModelCache.risk_model()
    if model:
        features = _build_risk_features(weather, disruption)
        try:
            prediction  = model.predict(features)[0]
            probability = model.predict_proba(features)[0]
            risk_score  = float(max(probability))

            level_map   = {0: "low", 1: "medium", 2: "high", 3: "critical"}
            level       = level_map.get(int(prediction), "medium")
            mult_map    = {"low": 1.0, "medium": 1.5, "high": 2.2, "critical": 3.5}
            mult        = mult_map[level]

            assessment = RiskAssessment(
                risk_level    = level,
                risk_score    = risk_score,
                base_premium  = 50.0,
                final_premium = 50.0 * mult,
                multiplier    = mult,
                rationale     = f"ML model prediction: {level} (confidence {risk_score:.0%}).",
            )
        except Exception as exc:
            print(f"[AIService] Model inference failed: {exc}. Falling back to heuristic.")
            assessment = _heuristic_risk(disruption, weather)
    else:
        assessment = _heuristic_risk(disruption, weather)

    return AIServiceResponse(
        worker_id  = worker_id,
        city       = city,
        assessment = assessment,
        disruption = disruption,
    )


def validate_claim(
    claim_id: str,
    worker_id: str,
    city: str,
    claim_amount: float,
    worker_history: Optional[dict] = None,
) -> ClaimValidation:
    """
    Validate an insurance claim using the fraud detection model.

    Args:
        claim_id:       Unique claim ID.
        worker_id:      Worker filing the claim.
        city:           City of the claim event.
        claim_amount:   Claimed payout amount in INR.
        worker_history: Dict with keys: past_claims_count, avg_past_claim,
                        days_since_last_claim. Defaults to clean history.

    Returns:
        ClaimValidation with decision and fraud score.
    """
    worker_history = worker_history or {
        "past_claims_count": 0,
        "avg_past_claim": 500.0,
        "days_since_last_claim": 999,
    }

    disruption = detect_disruptions_by_city(city)

    model = _ModelCache.fraud_model()
    if model:
        features = _build_fraud_features(claim_amount, disruption, worker_history)
        try:
            prediction  = model.predict(features)[0]
            probability = model.predict_proba(features)[0]
            fraud_score = float(probability[1]) if len(probability) > 1 else float(probability[0])
            confidence  = float(max(probability))
            is_fraud    = bool(prediction)

            if fraud_score < 0.3:
                decision, valid = "approved", True
                reason = f"ML model approved. Fraud score: {fraud_score:.2f}."
            elif fraud_score < 0.6:
                decision, valid = "review", False
                reason = f"ML model flagged for review. Fraud score: {fraud_score:.2f}."
            else:
                decision, valid = "rejected", False
                reason = f"ML model rejected claim. Fraud score: {fraud_score:.2f}."

            return ClaimValidation(
                claim_id    = claim_id,
                is_valid    = valid,
                fraud_score = fraud_score,
                confidence  = confidence,
                decision    = decision,
                reason      = reason,
            )
        except Exception as exc:
            print(f"[AIService] Fraud model inference failed: {exc}. Using heuristic.")

    return _heuristic_fraud(claim_id, claim_amount, disruption, worker_history)


# ── Test ──────────────────────────────────────────────────────────────────────

def test_ai_service():
    """
    Integration test using synthetic WeatherData — no live API or model files needed.
    """
    import json
    from weather_service import WeatherData
    from disruption_detector import detect_disruptions

    print("\n" + "═"*60)
    print("  GigShield AI — AI Service Test Suite")
    print("═"*60)

    # --- Test 1: Risk assessment (heavy rain scenario) ---
    print("\n[1] Risk Assessment — Heavy monsoon worker in Mumbai")
    rain_weather = WeatherData("Mumbai", 30.0, 85.0, 14.0, 90, "Heavy Rain", 160, 19.07, 72.88)
    response = calculate_risk_and_premium("W-1042", "Mumbai,IN", weather=rain_weather)
    print(json.dumps(response.to_dict(), indent=2))

    # --- Test 2: Risk assessment (normal day) ---
    print("\n[2] Risk Assessment — Clear day in Pune")
    clear_weather = WeatherData("Pune", 26.0, 0.0, 3.0, 50, "Clear", 60, 18.52, 73.85)
    response = calculate_risk_and_premium("W-2201", "Pune,IN", weather=clear_weather)
    print(json.dumps(response.to_dict(), indent=2))

    # --- Test 3: Claim validation — legitimate claim ---
    print("\n[3] Claim Validation — Legitimate claim during disruption")
    result = validate_claim(
        claim_id       = "CLM-9001",
        worker_id      = "W-1042",
        city           = "Mumbai,IN",
        claim_amount   = 350.0,
        worker_history = {"past_claims_count": 2, "avg_past_claim": 400.0, "days_since_last_claim": 30},
    )
    print(json.dumps(result.to_dict(), indent=2))

    # --- Test 4: Claim validation — suspicious claim ---
    print("\n[4] Claim Validation — Suspicious high-value claim, no disruption")
    result = validate_claim(
        claim_id       = "CLM-9002",
        worker_id      = "W-3399",
        city           = "Pune,IN",         # clear weather
        claim_amount   = 5000.0,
        worker_history = {"past_claims_count": 7, "avg_past_claim": 300.0, "days_since_last_claim": 3},
    )
    print(json.dumps(result.to_dict(), indent=2))


if __name__ == "__main__":
    test_ai_service()