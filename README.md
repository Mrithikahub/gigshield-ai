# GigShield AI

AI-Powered Parametric Insurance for Gig Workers

---

## Problem Statement

India’s gig economy relies heavily on delivery workers from platforms such as Swiggy, Zomato, Zepto, and Amazon. These workers depend on daily earnings for their livelihood.

However, external disruptions such as heavy rainfall, extreme heat, severe pollution, and city restrictions can significantly reduce or completely stop their ability to work. During such situations, workers experience direct income loss without any financial protection.

Currently, there is no simple and automated system that provides compensation for such disruption-based income loss.

---

## Solution

GigShield AI is an AI-powered parametric insurance platform designed to protect gig workers from income loss.

The system continuously monitors environmental conditions such as weather and pollution. When a predefined disruption is detected, it automatically triggers an insurance claim and processes compensation without requiring manual claim filing.

The platform also includes a dynamic premium calculation system that adjusts weekly pricing based on environmental risk factors.

---

## Target Users

* Food delivery partners (Swiggy, Zomato, Zepto)
* Logistics and e-commerce delivery workers
* Urban gig workers dependent on daily earnings

---

## Workflow

1. Worker registers on the platform
2. System performs AI-based risk assessment
3. Weekly insurance premium is calculated
4. Worker purchases the policy
5. System continuously monitors environmental data
6. Disruption is detected (rain, heat, pollution)
7. Claim is triggered automatically
8. Fraud detection validates the claim
9. Payout is processed

---

## AI Integration

### Risk Prediction

AI models analyze environmental factors such as rainfall, air quality, and temperature to estimate disruption risk.

### Dynamic Pricing

Premiums are adjusted dynamically based on calculated risk levels and environmental conditions.

### Fraud Detection

The system identifies suspicious claims using anomaly detection techniques, such as duplicate claims or inconsistent data.

---

## Pricing Model

The platform uses a weekly subscription model aligned with gig workers’ earning cycles.

Premium is calculated based on:

* Environmental conditions
* Risk level
* Location factors

---

## Tech Stack

| Layer    | Technology                   |
| -------- | ---------------------------- |
| Frontend | React                        |
| Backend  | Node.js / Python             |
| AI/ML    | Python (Scikit-learn)        |
| Database | MongoDB                      |
| APIs     | Weather and Air Quality APIs |
| Payments | Razorpay / Simulation        |

---

## Architecture Diagram
<img width="1600" height="854" alt="image" src="https://github.com/user-attachments/assets/c95062f1-7afd-42b8-9398-8d162c040dc0" />


C:\Users\mrith\gigshield-ai\docs\architecture.jpeg

## Workflow Diagram

![Workflow](docs/workflow.jpeg)

---

## Integration Flow

Weather API → Disruption Detection → Claim Trigger → Fraud Check → Payment

---

## Future Scope

* Integration with delivery platforms (Swiggy, Zomato)
* Mobile application for workers
* Advanced AI prediction models
* Real-time analytics dashboard

---

## Demo Video

(Add link here)

---

## Conclusion

GigShield AI provides a structured and automated financial safety mechanism for gig workers, improving income stability during external disruptions.
