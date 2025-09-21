import smtplib, ssl
import random
import os
from db import alerts, found_items, logs
from bson import ObjectId
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
import traceback

 # Change if using another provider

SENDER_EMAIL ="pythonsendsmail8@gmail.com"
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")

def send_otp_email(item_id: str, item_name: str, email: str, founder_email: str):
    sslcontext = ssl.create_default_context()
    ot = str(random.randint(100000, 999999))
    msg_body = f"Your OTP for Exchange is: {ot}. Item: {item_name} Valid for 10 minutes."
    message = f"""From: Foundry team <{SENDER_EMAIL}>
To: {email}
Subject: OTP for Exchange

{msg_body}
Regards,
Foundry Team
"""

    try:
        try:
            oid = ObjectId(item_id)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid item_id format")

        # Send email
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=sslcontext) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, email, message)

        # Save OTP in DB
        alerts.update_one(
            {"item_id": oid},
            {
                "$set": {
                    "otp": ot,
                    "expires_at": expires_at,
                    "verified": False,
                },
                "$setOnInsert": {
                    "item_name": item_name,
                    "owner_email": email,
                    "item_id": oid,
                    "founder_email": founder_email,
                },
            },
            upsert=True,
        )

        return {"status": "success", "otp": ot}  # you may want to remove otp in prod
    except Exception as e:
        print("Error in send_otp_email:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Email not sent: {str(e)}")


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