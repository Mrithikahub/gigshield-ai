GigShield AI – Backend

This repository contains the backend for GigShield AI, a parametric insurance system designed for food delivery workers on platforms like Zomato and Swiggy.

The backend is built using FastAPI and handles worker registration, policy creation, premium calculation, claim processing, and disruption triggers such as heavy rain or extreme heat. When certain environmental conditions are met, the system automatically generates claims and payouts.

The goal of the project is to simulate a system where gig workers can receive instant insurance payouts when their ability to work is affected by external disruptions.

Running the Backend

First install the required dependencies.

pip install -r requirements.txt

Then start the server.

python -m uvicorn app.main:app --reload

Once the server is running, you can access the API documentation here:

http://localhost:8000/docs

FastAPI automatically provides an interactive interface where all endpoints can be tested.

Models

The models define request and response structures using Pydantic.

Utils

Utility files such as the temporary in-memory database.

Main API Areas

The backend exposes several groups of endpoints.

Workers

Handles delivery partner registration and profile information.

Example functionality:

register a worker

retrieve worker details

estimate potential income loss during disruptions

show disruption forecasts

Premium

Responsible for calculating insurance premiums.

Premiums depend on factors such as:

city risk level

worker earnings

risk score

Policies

Workers can purchase weekly policies which make them eligible for payouts during disruptions.

Endpoints include:

create a policy

view active policies

check policy history

Triggers

Triggers represent real-world disruptions such as weather events.

Examples:

heavy rain

extreme heat

high AQI

flood alerts

curfew

When a trigger fires, the system automatically generates payouts for eligible workers.

Claims

Workers can submit claims manually if needed. Each claim passes through a fraud detection system before approval.

Analytics

Analytics endpoints provide dashboards and summaries such as:

total claims

payout amounts

fraud statistics

city-level disruption patterns

Trigger Conditions

Some examples of disruption conditions used in the system:

Trigger	Condition
Heavy Rain	Rainfall ≥ 50 mm
Extreme Heat	Temperature ≥ 42°C
High AQI	AQI ≥ 400
Flood Alert	Government alert issued
Curfew	Movement restrictions

When these thresholds are crossed, the system calculates payouts automatically.

Premium Calculation

The weekly premium is calculated using a base amount plus additional adjustments depending on worker risk.

Example structure:

weekly_premium = base_price + zone_surcharge + risk_loading

Coverage per disruption event is capped to ensure sustainability of the system.

AI Components

The project includes simple rule-based AI modules.

Risk Engine

Calculates a risk score between 0 and 1 for each worker based on:

city

work zone

average daily earnings

platform

This score affects the insurance premium.

Fraud Detection

Manual claims are evaluated using several rules such as:

duplicate claims on the same day

unusually high claim frequency

late submissions

missing GPS data

claims from outside the registered city

Based on the final fraud score, the claim may be:

automatically approved

sent for manual review

rejected

Future Improvements

Planned improvements include:

replacing rule-based logic with machine learning models

integrating live weather and AQI APIs

adding Razorpay payouts

migrating the database to PostgreSQL

Tech Stack

The backend uses:

Python

FastAPI

Uvicorn

Pydantic

These tools were chosen for their simplicity and performance when building REST APIs.

Testing the System

Once the backend is running, open the API documentation page:

http://localhost:8000/docs

From there you can test the full flow:

Register a worker

Generate a premium quote

Create a policy

Trigger a disruption event

Observe the generated claims and payouts
