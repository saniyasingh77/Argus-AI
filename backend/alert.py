import smtplib
from twilio.rest import Client


# ---------------- EMAIL ALERT ----------------

def send_email(activity):

    sender_email = "singhsaniya672@gmail.com"

    app_password = "cygl nbaw dqmb osrd"

    receiver_email = [

        "singhsaniya672@gmail.com",

    ]


    subject = "PATIENT EMERGENCY ALERT"

    body = f"""
ALERT: {activity}

Patient needs immediate attention immediately.
"""

    message = f"Subject:{subject}\n\n{body}"


    try:

        server = smtplib.SMTP_SSL("smtp.gmail.com",465)

        server.login(sender_email, app_password)

        server.sendmail(sender_email, receiver_email, message)

        server.quit()

        print("EMAIL SENT to all recipients")

    except Exception as e:

        print("EMAIL ERROR:", e)



# ---------------- WHATSAPP ALERT ----------------

def send_whatsapp(activity):

    account_sid = "AC83c8364977254be840e8c3b916f48930"

    auth_token = "96ee17c5aa442f32098107fe44c49014"


    client = Client(account_sid, auth_token)


    try:

        message = client.messages.create(

            body=f"🚨 EMERGENCY ALERT 🚨\nPatient status: {activity}",

            from_="whatsapp:+14155238886",

            to="whatsapp:+916376166905"

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