# app.py
from fastapi import FastAPI, Request, BackgroundTasks
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

    # 👇 add this line to debug what credentials the app sees
    print(f"DEBUG: FROM={SMTP_USER} TO={TO_EMAIL} HOST={SMTP_HOST}:{SMTP_PORT} PASSLEN={len(SMTP_PASS) if SMTP_PASS else 0}")

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = SMTP_USER
    msg["To"] = TO_EMAIL

    try:
        import smtplib
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        print("✅ Email sent.")
    except Exception as e:
        print("❌ Failed to send email:", e)


# Root endpoint (test server)
@app.get("/")
async def root():
    return {"status": "FastAPI running", "time": str(datetime.utcnow())}

# Webhook endpoint (fast response version)
@app.api_route("/notion-webhook", methods=["GET", "POST"])
async def notion_webhook(request: Request, background_tasks: BackgroundTasks):
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

    # Prepare the email message
    subject = f"kacper? unzwar: {received_at}"
    body = f"liebst du mich?"

    # ⚡ send the email *after* replying to Notion
    background_tasks.add_task(send_email, subject, body)

    # ✅ respond immediately so Notion doesn't time out
    return {"status": "ok", "received_at": received_at}

