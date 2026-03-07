
from pydantic import BaseModel, Field, field_validator
from typing   import Optional, Literal
from datetime import datetime
from enum     import Enum


# ── Enums ──────────────────────────────────────────────────────────────────────

class Platform(str, Enum):
    zomato = "Zomato"
    swiggy = "Swiggy"

class TriggerType(str, Enum):
    heavy_rain   = "HEAVY_RAIN"
    extreme_heat = "EXTREME_HEAT"
    high_aqi     = "HIGH_AQI"
    flood_alert  = "FLOOD_ALERT"
    curfew       = "CURFEW"

class ClaimStatus(str, Enum):
    pending  = "pending"
    approved = "approved"
    rejected = "rejected"
    paid     = "paid"


# ── Worker ──────────────────────────────────────────────────────────────────────

class WorkerRegister(BaseModel):
    name:              str   = Field(..., min_length=2,  max_length=100, example="Arjun Sharma")
    phone:             str   = Field(..., pattern=r"^\d{10}$",           example="9876543210")
    platform:          Platform                                     = Field(..., example="Zomato")
    city:              str   = Field(..., min_length=2,                  example="Mumbai")
    work_zone:         str   = Field(..., min_length=2,                  example="Bandra")
    avg_daily_earning: float = Field(..., gt=0,                          example=500.0,
                                     description="Average daily earning in INR")

    @field_validator("city", "work_zone")
    @classmethod
    def normalise(cls, v: str) -> str:
        return v.strip().lower()

    @field_validator("name")
    @classmethod
    def title_name(cls, v: str) -> str:
        return v.strip().title()


# ── Premium ──────────────────────────────────────────────────────────────────────

class PremiumQuoteRequest(BaseModel):
    city:              str   = Field(..., example="Mumbai")
    platform:          Platform                    = Field(..., example="Zomato")
    work_zone:         str   = Field(..., example="Bandra")
    avg_daily_earning: float = Field(..., gt=0,    example=500.0)

    @field_validator("city", "work_zone")
    @classmethod
    def normalise(cls, v: str) -> str:
        return v.strip().lower()


# ── Policy ──────────────────────────────────────────────────────────────────────

class PolicyCreate(BaseModel):
    worker_id: str = Field(..., example="A1B2C3D4")
    weeks:     int = Field(1, ge=1, le=52, example=1,
                           description="Number of weeks to insure (1–52)")


# ── Claims ──────────────────────────────────────────────────────────────────────

class ClaimSubmit(BaseModel):
    worker_id:    str         = Field(..., example="A1B2C3D4")
    trigger_type: TriggerType = Field(..., example="HEAVY_RAIN")
    event_date:   datetime    = Field(..., example="2026-03-07T10:00:00")
    location:     str         = Field(..., example="Bandra, Mumbai")
    gps_lat:      Optional[float] = Field(None, example=19.0544)
    gps_lng:      Optional[float] = Field(None, example=72.8405)


# ── Trigger Event ──────────────────────────────────────────────────────────────

class TriggerFireRequest(BaseModel):
    city:         str         = Field(..., example="mumbai")
    trigger_type: TriggerType = Field(..., example="HEAVY_RAIN")
    value:        float       = Field(..., example=75.0,
                                      description="Measured value: mm rain / °C temp / AQI index / 1 for alerts")
    timestamp:    datetime    = Field(default_factory=datetime.utcnow)

    @field_validator("city")
    @classmethod
    def lower(cls, v: str) -> str:
        return v.strip().lower()
