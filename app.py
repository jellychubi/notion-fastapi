# app.py
from fastapi import FastAPI, Request
from datetime import datetime
import os
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText

load_dotenv()

app = FastAPI()

# Email config from .env (optional)
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT") or 465)
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
TO_EMAIL = os.getenv("TO_EMAIL", SMTP_USER)

def send_email(subject: str, body: str):
    if not (SMTP_HOST and SMTP_USER and SMTP_PASS):
        print("Email not configured — skipping send.")
        print(subject, body)
        return
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = SMTP_USER
    msg["To"] = TO_EMAIL
    try:
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        print("✅ Email sent.")
    except Exception as e:
        print("❌ Failed to send email:", e)

# Root endpoint (test server)
@app.get("/")
async def root():
    return {"status": "FastAPI running", "time": str(datetime.utcnow())}

# Webhook endpoint
@app.api_route("/notion-webhook", methods=["GET", "POST"])
async def notion_webhook(request: Request):
    received_at = datetime.utcnow().isoformat()
    
    print("==== Webhook triggered ====")
    print("Method:", request.method)
    print("Query params:", dict(request.query_params))
    
    # Try to read JSON body
    try:
        data = await request.json()
        print("JSON body:", data)
    except Exception:
        # If JSON fails, read raw body
        body_bytes = await request.body()
        data = body_bytes.decode("utf-8")
        print("Raw body:", data)

    # Optional: send email notification
    subject = f"Notion webhook triggered at {received_at}"
    body = f"Webhook data:\n{data}"
    send_email(subject, body)

    return {"status": "ok", "received_at": received_at}
