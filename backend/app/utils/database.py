import uuid
import sqlite3
import json
from datetime import datetime
from typing   import Optional
from pathlib  import Path

DB_PATH = Path(__file__).parent.parent / "gigshield.db"


def get_conn():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS workers (
            worker_id         TEXT PRIMARY KEY,
            name              TEXT,
            city              TEXT,
            platform          TEXT,
            avg_daily_earning REAL,
            risk_score        REAL,
            risk_level        TEXT,
            risk_zone         TEXT,
            registered_at     TEXT
        );
        CREATE TABLE IF NOT EXISTS policies (
            policy_id          TEXT PRIMARY KEY,
            worker_id          TEXT,
            weeks              INTEGER,
            weekly_premium     REAL,
            total_premium      REAL,
            coverage_per_event REAL,
            risk_level         TEXT,
            start_date         TEXT,
            end_date           TEXT,
            status             TEXT
        );
        CREATE TABLE IF NOT EXISTS claims (
            claim_id       TEXT PRIMARY KEY,
            worker_id      TEXT,
            policy_id      TEXT,
            trigger_type   TEXT,
            amount         REAL,
            status         TEXT,
            fraud_score    REAL,
            fraud_flags    TEXT,
            location       TEXT,
            is_auto        INTEGER,
            payout_receipt TEXT,
            created_at     TEXT
        );
    """)
    conn.commit()
    conn.close()

init_db()


def new_id(prefix: str) -> str:
    return f"{prefix}-{str(uuid.uuid4())[:6].upper()}"

def now() -> datetime:
    return datetime.utcnow()

def _ts(dt) -> str:
    if isinstance(dt, datetime): return dt.isoformat()
    return str(dt)

def _dt(s) -> datetime:
    if isinstance(s, datetime): return s
    try: return datetime.fromisoformat(str(s))
    except: return datetime.utcnow()

def _worker(row) -> dict:
    return dict(row)

def _policy(row) -> dict:
    d = dict(row)
    d["start_date"] = _dt(d["start_date"])
    d["end_date"]   = _dt(d["end_date"])
    return d

def _claim(row) -> dict:
    d = dict(row)
    d["created_at"]     = _dt(d["created_at"])
    d["fraud_flags"]    = json.loads(d["fraud_flags"] or "[]")
    d["payout_receipt"] = json.loads(d["payout_receipt"] or "null")
    d["is_auto"]        = bool(d["is_auto"])
    return d


def create_worker(data: dict) -> dict:
    wid = new_id("W")
    reg = _ts(now())
    conn = get_conn()
    conn.execute("INSERT INTO workers VALUES (?,?,?,?,?,?,?,?,?)",
        (wid, data["name"], data["city"], data["platform"],
         data["avg_daily_earning"], data["risk_score"],
         data["risk_level"], data["risk_zone"], reg))
    conn.commit(); conn.close()
    return {**data, "worker_id": wid, "registered_at": reg}

def get_worker(worker_id: str) -> Optional[dict]:
    conn = get_conn()
    row  = conn.execute("SELECT * FROM workers WHERE worker_id=?", (worker_id,)).fetchone()
    conn.close()
    return _worker(row) if row else None

def get_all_workers() -> list:
    conn = get_conn()
    rows = conn.execute("SELECT * FROM workers").fetchall()
    conn.close()
    return [_worker(r) for r in rows]


def create_policy(data: dict) -> dict:
    pid = new_id("POL")
    conn = get_conn()
    conn.execute("INSERT INTO policies VALUES (?,?,?,?,?,?,?,?,?,?)",
        (pid, data["worker_id"], data["weeks"],
         data["weekly_premium"], data["total_premium"],
         data["coverage_per_event"], data["risk_level"],
         _ts(data["start_date"]), _ts(data["end_date"]), data["status"]))
    conn.commit(); conn.close()
    return {**data, "policy_id": pid}

def get_worker_policies(worker_id: str) -> list:
    conn = get_conn()
    rows = conn.execute("SELECT * FROM policies WHERE worker_id=?", (worker_id,)).fetchall()
    conn.close()
    return [_policy(r) for r in rows]

def get_active_policy(worker_id: str) -> Optional[dict]:
    conn = get_conn()
    rows = conn.execute("SELECT * FROM policies WHERE worker_id=? AND status='active'", (worker_id,)).fetchall()
    conn.close()
    for row in rows:
        p = _policy(row)
        if p["end_date"] >= now(): return p
    return None

def get_all_policies() -> list:
    conn = get_conn()
    rows = conn.execute("SELECT * FROM policies").fetchall()
    conn.close()
    return [_policy(r) for r in rows]


def create_claim(data: dict) -> dict:
    cid = new_id("CLM")
    created = _ts(now())
    conn = get_conn()
    conn.execute("INSERT INTO claims VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
        (cid, data["worker_id"], data["policy_id"],
         data["trigger_type"], data["amount"], data["status"],
         data["fraud_score"], json.dumps(data.get("fraud_flags", [])),
         data["location"], int(data.get("is_auto", False)),
         json.dumps(data.get("payout_receipt")), created))
    conn.commit(); conn.close()
    return {**data, "claim_id": cid, "created_at": _dt(created)}

def get_worker_claims(worker_id: str) -> list:
    conn = get_conn()
    rows = conn.execute("SELECT * FROM claims WHERE worker_id=?", (worker_id,)).fetchall()
    conn.close()
    return [_claim(r) for r in rows]

def get_all_claims() -> list:
    conn = get_conn()
    rows = conn.execute("SELECT * FROM claims").fetchall()
    conn.close()
    return [_claim(r) for r in rows]

def duplicate_exists(worker_id: str, trigger_type: str) -> bool:
    today = now().date().isoformat()
    conn  = get_conn()
    row   = conn.execute(
        "SELECT 1 FROM claims WHERE worker_id=? AND trigger_type=? AND date(created_at)=date(?)",
        (worker_id, trigger_type, today)).fetchone()
    conn.close()
    return row is not None

db = {"claims": {}}
