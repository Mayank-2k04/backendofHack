import smtplib, ssl
import random
import os
from db import alerts, lost_items, found_items, logs
from bson import ObjectId
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException

host = "smtp.gmail.com"  # Change if using another provider
port = 465
SENDER_EMAIL ="pythonsendsmail8@gmail.com"
SENDER_PASSWORD = os.getenv("PYTHONEMAILPASS")

def send_otp_email(item_id: str,item_name: str,email: str, founder_email: str):
    sslcontext = ssl.create_default_context()
    ot = str(random.randint(100000, 999999))
    m = f"Your OTP for Exchange is: {ot}. Item : {item_name} Valid for 5 minutes."
    message = f"""From: Foundry team <{SENDER_EMAIL}>
To: {email}
Subject: OTP for Exchange

{m}
Regards,
Foundry Team
"""

    try:
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)
        with smtplib.SMTP_SSL(host, port, context=sslcontext) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, email, message)
        alerts.update_one(
            {"item_id": ObjectId(item_id)},
            {"$set": {
                "otp": ot,
                "expires_at": expires_at,
                "verified": False
            },
                "$setOnInsert": {
                    "item_name": item_name,
                    "owner_email": email,
                    "item_id": ObjectId(item_id),
                    "founder_email": founder_email
                }},
            upsert=True
        )

        return {"status" : "Success"}
    except Exception:
        return {"status" : "Not sent"}

def verify_any_otp_and_log(ot: str):

    now = datetime.now(timezone.utc)
    record = alerts.find_one({"otp": ot, "expires_at": {"$gte": now}})
    if not record:
        raise HTTPException(status_code=404, detail="Invalid or expired OTP")

    item_id = record["item_id"]


    found_items.delete_one({"_id": ObjectId(item_id)})

    logs.insert_one({
        "item_id": str(item_id),
        "item_name": record.get("item_name", "Unknown"),  # fallback if item removed
        "founder_email": record.get("founder_email", None),
        "owner_email": record["owner_email"],
        "exchanged_at": now
    })

    alerts.delete_one({"_id": record["_id"]})

    return {"message": "OTP verified, item removed from lost/found collections, and logged successfully!"}

if __name__ == "__main__":
    pass
    # otp = generate_otp()
    # print(send_otp_email("68d0279784c250badf2e388b","flkutdjryhdbgvc ","mayank.kapoor2607@gmail.com",otp))
    # print(verify_any_otp_and_log("751033"))