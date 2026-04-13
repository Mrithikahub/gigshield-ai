# TriggerPe

## Guidewire DEVTrails 2026 — Phase 2 Submission

TriggerPe is a parametric income insurance platform built for food delivery workers in India. The platform is designed specifically for partners working with Swiggy, Zomato, Blinkit, Zepto, Amazon, and similar platforms who lose their daily earnings when external disruptions like heavy rain, extreme heat, or poor air quality make it impossible to work.

The core idea is simple — when a disruption happens, the worker should not have to file a claim, call anyone, or prove anything. The system detects the disruption automatically and processes the payout without any action from the worker.

---

## The Problem

A Swiggy delivery partner in Chennai earns around ₹600 to ₹1000 on a normal working day. When it rains heavily or when AQI shoots above 300, they simply cannot go out. Orders dry up. Earnings drop to zero. There is no backup, no safety net, and no insurance that covers this kind of income loss.

This is not a rare situation. Chennai, Mumbai, Delhi, and Bangalore see multiple such disruption days every month during monsoon season. Across India, millions of delivery workers face this problem every year with zero protection.

Existing insurance products do not cover income loss from weather. They cover health, accidents, and vehicle damage — none of which address the actual problem these workers face.

---

## What We Built

TriggerPe monitors real-time environmental conditions for each worker's city and automatically triggers insurance payouts when predefined thresholds are breached.

The worker registers once, chooses a weekly plan, and is protected from that point forward. No paperwork. No claim forms. No waiting.

When rain crosses 15mm per hour in Chennai, every active worker in Chennai gets a payout automatically. When AQI crosses 300, the same happens. The whole process — from trigger detection to payout initiation — happens without any human involvement.

---

## Persona

We focused on food delivery workers for Swiggy and Zomato operating in Chennai as our primary persona. This group was chosen because Chennai has high monsoon rainfall, one of the largest gig worker populations in South India, and workers here are particularly vulnerable to income loss during the June to November monsoon period.

A typical worker in our target segment:
- Works 8 to 10 hours a day, 6 days a week
- Earns between ₹500 and ₹1200 on a good day
- Has no formal employment contract or employee benefits
- Cannot afford to miss more than 2 working days in a week without financial stress
- Does not have the time, literacy, or trust to navigate complex insurance products

---

## Weekly Premium Model

We structured pricing on a weekly basis because delivery workers get paid weekly or daily by their platforms. Asking them to pay monthly or annually creates a mismatch with their cash flow.

Three tiers are available:

**Basic — ₹49 per week**
Covers rain and heat triggers. Maximum payout ₹800 per qualifying event.

**Standard — ₹79 per week**
Covers all five triggers including AQI, curfew, and platform outage. Maximum payout ₹1400 per event. This is our most popular tier.

**Premium — ₹99 per week**
All triggers covered with priority payout processing. Maximum payout ₹2000 per event.

The premium is calculated dynamically using our ML risk model which factors in the worker's city, zone, delivery platform, historical weather patterns for that area, and the worker's tenure on the platform. A worker operating in a flood-prone zone pays slightly more than one in a historically safe zone.

---

## Parametric Triggers

We defined five trigger conditions for Phase 2. Each one is tied to an objective, verifiable data source. When the threshold is breached, the system fires automatically.

**Heavy Rain** — Rainfall exceeds 15mm per hour. Payout: ₹800. Source: OpenWeatherMap API.

**Extreme Heat** — Temperature exceeds 42 degrees Celsius. Payout: ₹600. Source: OpenWeatherMap API.

**Hazardous AQI** — Air Quality Index exceeds 300. Payout: ₹600. Source: Air quality API.

**Curfew or Strike** — Admin sets a curfew flag for a city, indicating unplanned civic disruption. Payout: ₹800. Source: Admin input via our platform.

**Platform Outage** — Swiggy or Zomato app experiences downtime exceeding 2 hours. Payout: ₹350. Source: Admin input via our platform.

These thresholds were chosen based on publicly available data on weather conditions that make outdoor delivery work dangerous or impossible in Indian cities.

---

## What We Built in Phase 2

Phase 2 focused on making the core protection and claims flow work end to end.

**Registration and Onboarding**

Workers can register in under 2 minutes. The system automatically detects their city using GPS. They select their platform, set their average daily earning, choose a plan, and their policy is live immediately. We added a mandatory exclusions screen during registration so workers clearly understand what is not covered before they pay.

What is explicitly excluded from coverage: vehicle repairs, health and accident costs, war, government declared pandemic, terrorism, platform account suspension, and pre-existing disputes with delivery platforms.

**Dynamic Premium Calculation**

Premiums are calculated by our ML model using a Random Forest classifier trained on synthetic worker data. The model considers zone flood risk score, average daily orders in the zone, peak hour delivery density, the worker's platform, and their tenure. The output is a risk score that adjusts the base premium up or down within the tier range.

**Automatic Claims Pipeline**

When a trigger fires, the system creates a claim record, runs it through fraud detection, and if it passes, marks it as approved and queued for payout. The entire pipeline runs without any manual action from the worker or an agent.

**Fraud Detection**

We built four fraud checks. First, we verify that the worker's last known location matches the city where the claim was triggered. Second, we check for duplicate claims — if the same worker already has a claim for the same trigger type within 12 hours, the new one is rejected. Third, we use an IsolationForest model to flag workers whose claim frequency is significantly higher than the zone average. Fourth, we cross-reference every claim against our weather log to confirm that the trigger event actually occurred in that city within a two-hour window of the claim.

Claims that score below 0.4 on our fraud score are auto-approved. Claims between 0.4 and 0.7 are flagged for manual review. Claims above 0.7 are auto-rejected.

**Payout Simulation**

We integrated Razorpay in test mode to simulate payouts. When a claim is approved, the system initiates a payout to the worker's registered bank account and sends a notification. For the demo, we use test bank credentials.

**Admin Dashboard**

The admin panel shows total active policies, premiums collected, claims triggered, total payouts disbursed, and the current loss ratio. Admins can simulate a trigger for any city to demonstrate the auto-claim pipeline in action. They can also manually review flagged claims and approve or reject them.

---

## Actuarial Basis

We estimated our break-even premium based on Chennai weather data. Chennai sees approximately 8 to 10 heavy rain events per month during monsoon season, which translates to roughly 2 to 3 qualifying trigger events per month per worker on average.

At an average payout of ₹300 per event and 2.5 events per month, expected monthly payout per worker is ₹750, or roughly ₹187.50 per week.

Our Standard plan at ₹79 per week does not cover this fully on its own. The model relies on geographic diversification — not all cities trigger simultaneously — and on the fact that most workers are in lower-risk zones. We hold 20 percent of collected premiums as a reserve fund.

This is a simplified actuarial model appropriate for a hackathon prototype. A production system would require licensed actuarial analysis and regulatory approval.

---

## Tech Stack

The frontend is built with Next.js 14 and TypeScript. The backend runs on FastAPI with Python 3.11. Our ML models use scikit-learn. The database is SQLite for this prototype. We use the OpenWeatherMap free tier for weather data. Payments are simulated via Razorpay test mode.

---

## How to Run Locally

Clone the repository:
```
git clone https://github.com/Mrithikahub/gigshield-ai
```

Start the backend:
```
cd backend
py -3.11 -m pip install fastapi uvicorn pandas numpy scikit-learn sqlalchemy python-multipart httpx python-dotenv requests
py -3.11 -m uvicorn app.main:app --reload --port 8000
```

Start the frontend:
```
cd frontend/gigshield-v4
npm install
npm run dev
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /workers/register | Register a new delivery worker |
| GET | /workers/{worker_id} | Get worker profile |
| GET | /workers/ | List all workers |
| POST | /policies/create | Create insurance policy |
| GET | /policies/{worker_id} | Get worker policies |
| GET | /premium/{worker_id} | Get dynamic premium |
| POST | /trigger | Fire a manual trigger |
| POST | /trigger/auto/{city} | Auto trigger for a city |
| GET | /trigger/weather/{city} | Get live weather |
| GET | /claims/all | Get all claims |
| GET | /claims/{worker_id} | Get worker claims |
| PATCH | /claims/{claim_id}/approve | Approve a claim |
| PATCH | /claims/{claim_id}/reject | Reject a claim |
| GET | /analytics | Platform analytics |

---

## Live Demo

Try it out: https://triggerpe-f6ss.vercel.app/

Demo Video: https://youtu.be/Dtrrc_ADifk

---

## Team

Built for Guidewire DEVTrails 2026 University Hackathon.

Five member team — frontend, backend, ML/AI integration, fraud detection, and insurance domain research.
