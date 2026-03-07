"""
Database Layer  (Phase 1 — In-Memory)
=======================================
All data stored in module-level dicts.
Phase 2: swap each function body with SQLAlchemy + PostgreSQL.

Schema:
  workers  { id → worker_dict  }
  policies { id → policy_dict  }
  claims   { id → claim_dict   }
"""

import uuid
from datetime import datetime
from typing   import Optional

# ── In-memory store ────────────────────────────────────────────────────────────

db: dict = {
    "workers":  {},
    "policies": {},
    "claims":   {},
}


# ── Helpers ────────────────────────────────────────────────────────────────────

def generate_id() -> str:
    """Short 8-char uppercase ID — readable in demos."""
    return str(uuid.uuid4())[:8].upper()

def now() -> datetime:
    return datetime.utcnow()


# ── Workers ────────────────────────────────────────────────────────────────────

def create_worker(data: dict) -> dict:
    worker = {**data, "id": generate_id(), "registered_at": now()}
    db["workers"][worker["id"]] = worker
    return worker

def get_worker(worker_id: str) -> Optional[dict]:
    return db["workers"].get(worker_id)

def get_all_workers() -> list:
    return list(db["workers"].values())

def phone_exists(phone: str) -> bool:
    return any(w["phone"] == phone for w in db["workers"].values())


# ── Policies ───────────────────────────────────────────────────────────────────

def create_policy(data: dict) -> dict:
    policy = {**data, "id": generate_id()}
    db["policies"][policy["id"]] = policy
    return policy

def get_policy(policy_id: str) -> Optional[dict]:
    return db["policies"].get(policy_id)

def get_worker_policies(worker_id: str) -> list:
    return [p for p in db["policies"].values() if p["worker_id"] == worker_id]

def get_active_policy(worker_id: str) -> Optional[dict]:
    """Returns the worker's current active policy if one exists."""
    current = now()
    for p in db["policies"].values():
        if (p["worker_id"] == worker_id
                and p["status"] == "active"
                and p["start_date"] <= current <= p["end_date"]):
            return p
    return None

def get_active_policies_in_city(city: str) -> list:
    """Used by trigger engine — find all policy holders in a city."""
    current = now()
    result  = []
    for p in db["policies"].values():
        if p["status"] != "active": continue
        if not (p["start_date"] <= current <= p["end_date"]): continue
        worker = get_worker(p["worker_id"])
        if worker and worker.get("city") == city.lower():
            result.append(p)
    return result

def get_all_policies() -> list:
    return list(db["policies"].values())


# ── Claims ─────────────────────────────────────────────────────────────────────

def create_claim(data: dict) -> dict:
    claim = {**data, "id": generate_id(), "created_at": now()}
    db["claims"][claim["id"]] = claim
    return claim

def get_claim(claim_id: str) -> Optional[dict]:
    return db["claims"].get(claim_id)

def get_worker_claims(worker_id: str) -> list:
    return [c for c in db["claims"].values() if c["worker_id"] == worker_id]

def get_all_claims() -> list:
    return list(db["claims"].values())

def duplicate_claim_exists(worker_id: str, trigger_type: str, event_date: datetime) -> bool:
    """Prevent same worker claiming twice for the same event on the same day."""
    for c in db["claims"].values():
        if (c["worker_id"]   == worker_id
                and c["trigger_type"] == trigger_type
                and c["event_date"].date() == event_date.date()):
            return True
    return False
