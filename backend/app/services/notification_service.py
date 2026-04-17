import os
import requests

FAST2SMS_KEY = os.getenv("FAST2SMS_API_KEY", "")


def send_sms(phone: str, message: str) -> bool:
    """Send SMS via Fast2SMS. Returns True on success."""
    if not FAST2SMS_KEY:
        # Mock mode — print to terminal
        print(f"[SMS MOCK] To {phone}: {message}")
        return True
    try:
        r = requests.post(
            "https://www.fast2sms.com/dev/bulkV2",
            headers={"authorization": FAST2SMS_KEY},
            json={
                "route":   "q",
                "message": message,
                "numbers": phone,
            },
            timeout=8,
        )
        data = r.json()
        if data.get("return"):
            print(f"[SMS] Sent to {phone}")
            return True
        print(f"[SMS] Failed: {data}")
        return False
    except Exception as e:
        print(f"[SMS] Error: {e}")
        return False


def notify_claim_filed(phone: str, worker_name: str, trigger_type: str, amount: float):
    trigger_labels = {
        "HEAVY_RAIN":   "Heavy Rain",
        "EXTREME_HEAT": "Extreme Heat",
        "HIGH_AQI":     "High AQI",
        "STRONG_WIND":  "Strong Wind",
        "FLOOD_ALERT":  "Flood Alert",
    }
    label = trigger_labels.get(trigger_type, trigger_type)
    msg = (
        f"TriggerPe: Hi {worker_name}, a claim of Rs.{amount:.0f} "
        f"has been auto-filed for {label} disruption. "
        f"Payout will be processed within 24 hours. Stay safe!"
    )
    send_sms(phone, msg)


def notify_claim_approved(phone: str, worker_name: str, amount: float, receipt: str):
    msg = (
        f"TriggerPe: Hi {worker_name}, your claim of Rs.{amount:.0f} "
        f"has been APPROVED and paid. Receipt: {receipt}. "
        f"Your income is protected. Thank you for trusting TriggerPe!"
    )
    send_sms(phone, msg)


def notify_policy_expiring(phone: str, worker_name: str, days_left: int):
    msg = (
        f"TriggerPe: Hi {worker_name}, your policy expires in {days_left} day(s). "
        f"Renew now to stay protected. Visit your dashboard to renew."
    )
    send_sms(phone, msg)
