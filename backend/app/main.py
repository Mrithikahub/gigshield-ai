import sys
import os

# Add the parent directory to path so 'app' can be found
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.workers import router as workers_router
from app.routes.policies import router as policies_router
from app.routes.premium import router as premium_router
from app.routes.triggers import router as triggers_router
from app.routes.claims import router as claims_router
from app.routes.analytics import router as analytics_router

app = FastAPI(title="GigShield AI", version="2.0.0")

# Environment-based CORS configuration
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

# Include routers
app.include_router(workers_router,   prefix="/workers",   tags=["Workers"])
app.include_router(policies_router,  prefix="/policies",  tags=["Policies"])
app.include_router(premium_router,   prefix="/premium",   tags=["Premium"])
app.include_router(triggers_router,  prefix="/trigger",   tags=["Triggers"])
app.include_router(claims_router,    prefix="/claims",    tags=["Claims"])
app.include_router(analytics_router, prefix="/analytics", tags=["Analytics"])

@app.get("/")
def root():
    return {
        "service": "GigShield AI",
        "status": "running",
        "environment": ENVIRONMENT,
        "docs": "/docs"
    }

# Start weather poller background job
from app.services.weather_poller import start_weather_poller
start_weather_poller()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)