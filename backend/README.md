🛡️ GigShield AI — Backend
Parametric income insurance for Zomato & Swiggy delivery partners.
Zero manual claims. Instant UPI payouts. Fully automated.
View API Docs
</div>

📖 Overview
GigShield AI backend is built with FastAPI and handles the entire insurance logic — worker registration, premium calculation, policy management, parametric triggers, fraud detection, and instant payouts.
When a disruption crosses its threshold, the system automatically creates claims for all covered workers and fires UPI payouts with zero manual steps.
Disruption Detected  →  Threshold Check  →  Claims Auto-Created  →  Instant UPI Payout

🚀 Quickstart
bash# 1. Install dependencies
pip install -r requirements.txt

# 2. Start the server
python -m uvicorn app.main:app --reload

# 3. Open interactive API docs
http://localhost:8000/docs

 API Reference
 Workers
MethodEndpointDescriptionPOST/api/workers/registerRegister a delivery partnerGET/api/workers/{worker_id}Get worker profileGET/api/workers/{worker_id}/income-estimateShow ₹ loss per disruption typeGET/api/workers/{worker_id}/forecastWeekly disruption forecast
 Premium
MethodEndpointDescriptionPOST/api/premium/quotePreview premium before registeringGET/api/premium/calculate?worker_id=XPremium for a registered workerGET/api/premium/thresholdsAll trigger definitions
 Policies
MethodEndpointDescriptionPOST/api/policies/createPurchase weekly coverageGET/api/policies/active/{worker_id}Check if worker is currently coveredGET/api/policies/worker/{worker_id}Full policy history
 Triggers
MethodEndpointDescriptionPOST/api/triggers/fireFire disruption → auto-creates claims + payoutsPOST/api/triggers/simulateDemo simulationGET/api/triggers/thresholdsAll trigger definitionsGET/api/triggers/forecast/{city}Weekly risk forecast for a city
 Claims
MethodEndpointDescriptionPOST/api/claims/submitManual claim with fraud detectionGET/api/claims/worker/{worker_id}Worker claim historyGET/api/claims/{claim_id}Single claim detailPATCH/api/claims/{claim_id}/approveAdmin: approve + fire payoutPATCH/api/claims/{claim_id}/rejectAdmin: reject claim
 Analytics
MethodEndpointDescriptionGET/api/analytics/admin/summaryLoss ratio, fraud rate, payout trendsGET/api/analytics/worker/{worker_id}/dashboardWorker earnings and coverage status

 Trigger Thresholds
TriggerConditionPayoutHours LostHEAVY_RAINRainfall ≥ 50 mm1.00× coverage4 hrsEXTREME_HEATTemperature ≥ 42 °C0.75× coverage3 hrsHIGH_AQIAQI index ≥ 4000.75× coverage3 hrsFLOOD_ALERTAlert active1.25× coverage8 hrsCURFEWMovement restricted1.00× coverage8 hrs

 Premium Formula
weekly_premium = ₹30 base
               + zone_surcharge   →  ₹0 / ₹10 / ₹20  (low / medium / high city)
               + risk_loading     →  risk_score × ₹15

coverage_per_event = min(avg_daily_earning × 80%, ₹400)
City Risk Zones
🔴 High🟡 Medium🟢 LowMumbai, Delhi, Chennai, KolkataBangalore, Hyderabad, Pune, AhmedabadAll other cities

🤖 AI Services
Risk Engine — services/risk_engine.py
Calculates a risk score 0.0 – 1.0 per worker based on city, work zone, daily earnings, and platform. This score directly affects the weekly premium.
Fraud Detector — services/fraud_detector.py
Every manual claim is scored against 6 rules:
RuleFlagScoreSame claim filed twice todayDUPLICATE_CLAIM_SAME_DAY+0.504+ claims in 7 daysHIGH_VELOCITY+0.25Submitted 24+ hrs after eventLATE_SUBMISSION+0.20No GPS providedNO_GPS_PROVIDED+0.10GPS outside registered cityGPS_OUTSIDE_CITY_BOUNDS+0.403+ trigger types this weekMULTI_TRIGGER_STACKING+0.20
score ≥ 0.60  →  rejected
score ≥ 0.30  →  pending review
score  < 0.30  →  approved + instant payout

🛠️ Tech Stack
TechnologyPurposeFastAPIREST API frameworkUvicornASGI serverPydantic v2Request validationPython 3.10+Core language
