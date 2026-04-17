import sys as _sys
import os as _os
# Fix: ensure backend/ is in sys.path when uvicorn is launched from project root
_backend_dir = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
if _backend_dir not in _sys.path:
    _sys.path.insert(0, _backend_dir)

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from app.routes.workers   import router as workers_router
from app.routes.policies  import router as policies_router
from app.routes.premium   import router as premium_router
from app.routes.triggers  import router as triggers_router
from app.routes.claims    import router as claims_router
from app.routes.analytics import router as analytics_router
from app.routes.payments  import router as payments_router
from app.routes.auth      import router as auth_router
from app.routes.fraud     import router as fraud_router

# ── APScheduler: auto-trigger every hour ─────────────────────────────────────
try:
    from apscheduler.schedulers.background import BackgroundScheduler
    from app.services.auto_claim_service import run_auto_claims

    scheduler = BackgroundScheduler()
    scheduler.add_job(run_auto_claims, "interval", hours=1, id="auto_claims_hourly")

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        scheduler.start()
        print("[Scheduler] Auto-claim scheduler started — runs every hour")
        yield
        scheduler.shutdown()
        print("[Scheduler] Scheduler stopped")

except ImportError:
    print("[Scheduler] APScheduler not installed — auto-trigger disabled")

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        yield


# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="TriggerPe",
    version="2.0.0",
    description="AI-Powered Parametric Insurance for India's Gig Economy",
    lifespan=lifespan,
)

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

if ENVIRONMENT == "production":
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["https://your-frontend-domain.com"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(workers_router,   prefix="/workers",   tags=["Workers"])
app.include_router(policies_router,  prefix="/policies",  tags=["Policies"])
app.include_router(premium_router,   prefix="/premium",   tags=["Premium"])
app.include_router(triggers_router,  prefix="/trigger",   tags=["Triggers"])
app.include_router(claims_router,    prefix="/claims",    tags=["Claims"])
app.include_router(analytics_router, prefix="/analytics", tags=["Analytics"])
app.include_router(payments_router,  prefix="/payments",  tags=["Payments"])
app.include_router(auth_router,      prefix="/auth",      tags=["Auth"])
app.include_router(fraud_router,     prefix="/fraud",     tags=["Fraud"])


@app.get("/")
def root():
    return {
        "service":     "TriggerPe",
        "version":     "2.0.0",
        "status":      "running",
        "environment": ENVIRONMENT,
        "triggers":    5,
        "scheduler":   "auto-claims every 1 hour",
        "docs":        "/docs",
    }
