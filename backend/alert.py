"""
Alerting: email (SMTP) + WhatsApp (Twilio).

All credentials come from environment variables (see backend/config.py and
.env.example). Nothing is hard-coded. If credentials are not configured the
alert functions log and no-op instead of crashing, so the app runs safely in
demo / CI environments.
"""

import smtplib

from backend import config


# ---------------- EMAIL ALERT ----------------

def send_email(activity):
    sender_email = config.ALERT_EMAIL_SENDER
    app_password = config.ALERT_EMAIL_PASSWORD
    recipients = config.ALERT_EMAIL_RECIPIENTS

    if not (sender_email and app_password and recipients):
        print("EMAIL SKIPPED: email alerting is not configured")
        return

    subject = "PATIENT EMERGENCY ALERT"
    body = f"""
ALERT: {activity}

Patient needs immediate attention immediately.
"""
    message = f"Subject:{subject}\n\n{body}"

    try:
        server = smtplib.SMTP_SSL(config.SMTP_HOST, config.SMTP_PORT)
        server.login(sender_email, app_password)
        server.sendmail(sender_email, recipients, message)
        server.quit()
        print("EMAIL SENT to all recipients")
    except Exception as e:
        print("EMAIL ERROR:", e)


# ---------------- WHATSAPP ALERT ----------------

def send_whatsapp(activity):
    account_sid = config.TWILIO_ACCOUNT_SID
    auth_token = config.TWILIO_AUTH_TOKEN
    to_number = config.TWILIO_WHATSAPP_TO

    if not (account_sid and auth_token and to_number):
        print("WHATSAPP SKIPPED: Twilio is not configured")
        return

    try:
        from twilio.rest import Client

        client = Client(account_sid, auth_token)
        message = client.messages.create(
            body=f"EMERGENCY ALERT\nPatient status: {activity}",
            from_=config.TWILIO_WHATSAPP_FROM,
            to=to_number,
        )
        print("WHATSAPP SENT")
        print("Message SID:", message.sid)
    except Exception as e:
        print("WHATSAPP ERROR:", e)


# ---------------- MAIN ALERT ----------------

def send_alert(activity):
    print("Sending alert for:", activity)
    send_email(activity)
    send_whatsapp(activity)
