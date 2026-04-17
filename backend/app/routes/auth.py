"""
OTP Authentication via Fast2SMS + Email SMTP
POST /auth/send-otp   — generates OTP, sends SMS/Email, stores in memory
POST /auth/verify-otp — verifies OTP, returns worker_id
"""
import random
import time
import smtplib
from email.mime.text import MIMEText
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.notification_service import send_sms
from app.utils.database import get_all_workers

router = APIRouter()

# In-memory OTP store: { phone/email: { otp, expires_at, type } }
_otp_store: dict = {}
OTP_EXPIRY_SECONDS = 300  # 5 minutes


class SendOtpRequest(BaseModel):
    phone: str = ""
    email: str = ""


class VerifyOtpRequest(BaseModel):
    phone: str = ""
    email: str = ""
    otp: str


def send_email_otp(to_email: str, otp: str):
    """Send OTP via Gmail SMTP"""
    try:
        # Gmail App Password (NOT regular password)
        sender_email = "your_email@gmail.com"
        sender_password = "your_app_password"
        
        msg = MIMEText(f"Your TriggerPe OTP is {otp}. This code will expire in 5 minutes. Do not share this with anyone.")
        msg['Subject'] = "TriggerPe OTP Verification"
        msg['From'] = sender_email
        msg['To'] = to_email
        
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
        
        print(f"OTP sent to {to_email}")
        return True
    except Exception as e:
        print(f"Email sending failed: {e}")
        return False


@router.post("/send-otp")
def send_otp(body: SendOtpRequest):
    otp = str(random.randint(100000, 999999))
    
    # Determine delivery method and key
    if body.email:
        # Email OTP
        key = f"email:{body.email.lower()}"
        _otp_store[key] = {"otp": otp, "expires_at": time.time() + OTP_EXPIRY_SECONDS, "type": "email"}
        
        sent = send_email_otp(body.email, otp)
        
        return {
            "success": True,
            "message": "OTP sent successfully via email" if sent else "OTP generated (email mock mode)",
            "email": f"***{body.email.split('@')[0][-2:]}@{body.email.split('@')[1]}" if '@' in body.email else "***@***.com",
        }
    elif body.phone:
        # Phone OTP (existing logic)
        phone = body.phone.strip().replace(" ", "").replace("-", "")
        digits_only = "".join(c for c in phone if c.isdigit())
        if len(digits_only) >= 10:
            digits_only = digits_only[-10:]
        else:
            raise HTTPException(400, "Invalid phone number. Need at least 10 digits.")
        
        key = f"phone:{digits_only}"
        _otp_store[key] = {"otp": otp, "expires_at": time.time() + OTP_EXPIRY_SECONDS, "type": "phone"}
        
        msg = (
            f"TriggerPe OTP: {otp}. "
            f"Your one-time password for login. Valid for 5 minutes. "
            f"Do not share with anyone. - TriggerPe"
        )
        sent = send_sms(digits_only, msg)
        print(f"OTP sent to phone {digits_only}")
        
        return {
            "success": True,
            "message": "OTP sent successfully" if sent else "OTP generated (SMS mock mode)",
            "phone": f"****{digits_only[-4:]}",
        }
    else:
        raise HTTPException(400, "Either phone or email is required.")


@router.post("/verify-otp")
def verify_otp(body: VerifyOtpRequest):
    record = None
    key = None
    worker_id = None
    
    if body.email:
        # Email verification
        key = f"email:{body.email.lower()}"
        record = _otp_store.get(key)
        if not record:
            raise HTTPException(400, "No OTP found for this email. Please request a new OTP.")
    elif body.phone:
        # Phone verification (existing logic)
        phone = body.phone.strip().replace(" ", "").replace("-", "")
        digits_only = "".join(c for c in phone if c.isdigit())
        if len(digits_only) >= 10:
            digits_only = digits_only[-10:]
        
        key = f"phone:{digits_only}"
        record = _otp_store.get(key)
        if not record:
            raise HTTPException(400, "No OTP found for this number. Please request a new OTP.")
    else:
        raise HTTPException(400, "Either phone or email is required.")
    
    # Validate OTP
    if time.time() > record["expires_at"]:
        del _otp_store[key]
        raise HTTPException(400, "OTP expired. Please request a new one.")
    if record["otp"] != body.otp.strip():
        raise HTTPException(400, "Incorrect OTP. Please try again.")
    
    # OTP verified — clean up
    del _otp_store[key]
    
    # Try to find worker in DB
    all_workers = get_all_workers()
    for w in all_workers:
        if body.email and w.get("email", "").lower() == body.email.lower():
            worker_id = w["worker_id"]
            break
        elif body.phone:
            w_phone = (w.get("phone") or "").replace(" ", "").replace("-", "")
            w_digits = "".join(c for c in w_phone if c.isdigit())
            if w_digits.endswith(body.phone.replace(" ", "").replace("-", "")[-10:]):
                worker_id = w["worker_id"]
                break
    
    return {
        "success": True,
        "message": "OTP verified successfully",
        "worker_id": worker_id,  # None if no matching worker — frontend handles
        "authenticated": True,
    }
