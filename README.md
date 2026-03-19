**GigShield AI**

**AI-Powered Parametric Insurance for Gig Workers**

**Problem Statement**

India’s gig economy relies heavily on delivery workers from platforms such as Swiggy, Zomato, Zepto, and Amazon. These workers depend on daily earnings for their livelihood.

However, external disruptions such as heavy rainfall, extreme heat, severe pollution, and city restrictions can significantly reduce or completely stop their ability to work. During such situations, workers experience direct income loss without any financial protection.

Currently, there is no simple and automated system that provides compensation for such disruption-based income loss.

**Target Users**

Food delivery partners (Swiggy, Zomato, Zepto)

Logistics and e-commerce delivery workers

Urban gig workers dependent on daily earnings

**Example persona:**
A delivery partner earning ₹500–₹1000 per day loses income completely during heavy rain or pollution spikes, with no backup or insurance support.

**Solution**

GigShield AI is an AI-powered parametric insurance platform designed to protect gig workers from income loss.

The system continuously monitors environmental conditions such as weather and pollution. When a predefined disruption is detected, it automatically triggers an insurance claim and processes compensation without requiring manual claim filing.

The platform also includes a dynamic premium calculation system that adjusts weekly pricing based on environmental risk factors.

**Workflow**

Worker registers on the platform (with location detection)

System performs AI-based risk assessment

Weekly insurance premium is calculated

Worker purchases the policy

System continuously monitors environmental data

Disruption is detected (rain, heat, pollution)

Claim is triggered automatically

Fraud detection validates the claim

Payout is processed

Workflow Diagram

Worker Registration → Risk Assessment → Premium Calculation → Policy Purchase → Environmental Monitoring → Trigger Detection → Claim Generation → Fraud Check → Payout Processing

<img width="481" height="928" alt="image" src="https://github.com/user-attachments/assets/cd0b2748-598e-47e5-b12a-ffe247972535" />


**Weekly Premium Model
**
The platform uses a weekly subscription model aligned with gig workers’ earning cycles.

Premium is calculated based on:

Environmental conditions

Risk level

Location factors

This ensures affordability while maintaining risk-based pricing.

**Parametric Triggers
**
The system uses predefined thresholds to trigger claims automatically:

Rainfall above threshold

Temperature above extreme levels

AQI crossing hazardous limits

When a trigger condition is met, claims are processed instantly without manual verification.

**AI Integration
**
**Risk Prediction
**
AI models analyze environmental factors such as rainfall, air quality, and temperature to estimate disruption risk.

**Dynamic Pricing
**
Premiums are adjusted dynamically based on calculated risk levels and environmental conditions.

**Fraud Detection
**
The system identifies suspicious claims using anomaly detection techniques such as duplicate claims, inconsistent data, and unusual activity patterns.

**Tech Stack
**
Layer	Technology
Frontend	React / Next.js
Backend	Python (FastAPI)
AI/ML	Scikit-learn
Database	SQLite / MongoDB
APIs	Weather and Air Quality APIs
Payments	Razorpay / Simulation
System Architecture

Frontend (React/Next.js)
↓
Backend API (FastAPI)
↓
Risk Engine | Premium Calculator | Trigger Engine | Fraud Detection Module
↓
Database (SQLite/MongoDB)
↓
External APIs (Weather + AQI)
↓
Payment System

The system follows a modular architecture where each component operates independently, enabling scalability and maintainability.

<img width="1600" height="854" alt="image" src="https://github.com/user-attachments/assets/701d6e93-35af-4cb3-8210-42a0b48affb7" />


**Market** **Crash** **Handling**

In scenarios where a large number of claims are triggered simultaneously due to widespread disruptions:

Risk-based pricing helps balance payouts

Predefined payout structures limit over-exposure

Geographic diversification reduces concentrated risk

AI continuously adjusts pricing based on real-time risk

This ensures the system remains financially sustainable even during high-volume claim events.

**Adversarial** **Defense** **&** **Anti-Spoofing** **Strategy**
**Differentiation**

The system differentiates between genuine users and spoofing actors using multi-layer validation rather than relying solely on GPS.

Legitimate users show consistent movement patterns, behavioral signals, and alignment with real disruption conditions. Spoofed users exhibit anomalies such as unrealistic location changes, static behavior, or lack of activity correlation.

AI models analyze these patterns to assign a fraud score to each claim.

Data Signals Used Beyond GPS

Historical movement patterns

Device-level consistency

IP location versus GPS mismatch

Application usage and activity patterns

Claim timing and clustering behavior

Correlation with real environmental conditions

These signals help identify spoofing and coordinated fraud activity.

UX Balance for Flagged Claims

Low-risk claims are processed instantly

Medium-risk claims undergo additional validation

High-risk claims are flagged for review

Fallback logic ensures that users affected by poor network or real disruptions are not unfairly penalized.

Implementation Scope

Core workflow implementation

Location-based validation

Risk assessment and premium calculation

Parametric trigger simulation

Basic fraud detection logic

Integration Flow

Weather API → Disruption Detection → Claim Trigger → Fraud Check → Payment

Demo Video

[Add Video Link Here]

Future Scope

Integration with delivery platforms

Mobile application for workers

Advanced AI prediction models

Real-time analytics dashboard

Conclusion

GigShield AI provides a structured and automated financial safety mechanism for gig workers, improving income stability during external disruptions.
