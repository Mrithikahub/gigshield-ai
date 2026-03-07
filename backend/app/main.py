"""
GigShield AI — Main Application Entry Point
============================================
Parametric Income Insurance for Zomato/Swiggy Delivery Partners

Run:
    uvicorn app.main:app --reload --port 8000

Docs:
    http://localhost:8000/docs
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.workers  import router as workers_router
from app.routes.premium  import router as premium_router
from app.routes.policies import router as policies_router
from app.routes.claims   import router as claims_router
from app.routes.triggers import router as triggers_router
from app.routes.analytics import router as analytics_router

# ── App setup ─────────────────────────────────────────────────────────────────

app = FastAPI(
    title="GigShield AI",
    description="""
## Parametric Income Insurance for Gig Workers

Protects Zomato/Swiggy delivery partners from income loss due to:
- 🌧️ Heavy Rain  
- 🔥 Extreme Heat  
- 😷 Pollution Spikes (High AQI)  
- 🌊 Flood Alerts  
- 🚫 Curfews / Lockdowns  

### Flow
1. **Register** worker → get risk profile  
2. **Get Quote** → see premium before buying  
3. **Create Policy** → weekly coverage activated  
4. **Disruption happens** → system auto-triggers claim  
5. **Instant payout** → ₹ sent to worker via UPI  
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS — allow any frontend to connect without errors ───────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten to specific domain in production
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────

app.include_router(workers_router,   prefix="/api/workers",   tags=["👤 Workers"])
app.include_router(premium_router,   prefix="/api/premium",   tags=["💰 Premium"])
app.include_router(policies_router,  prefix="/api/policies",  tags=["📋 Policies"])
app.include_router(claims_router,    prefix="/api/claims",    tags=["📝 Claims"])
app.include_router(triggers_router,  prefix="/api/triggers",  tags=["⚡ Triggers"])
app.include_router(analytics_router, prefix="/api/analytics", tags=["📊 Analytics"])


# ── Health ────────────────────────────────────────────────────────────────────

@app.get("/", tags=["🩺 Health"])
def root():
    return {
        "service": "GigShield AI",
        "version": "1.0.0",
        "status":  "running 🚀",
        "docs":    "/docs",
    }


@app.get("/health", tags=["🩺 Health"])
def health_check():
    from app.utils.database import db
    return {
        "status":         "healthy ✅",
        "workers_count":  len(db["workers"]),
        "policies_count": len(db["policies"]),
        "claims_count":   len(db["claims"]),
    }
