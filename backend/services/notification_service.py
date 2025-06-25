# services/notification_service.py - Placeholder content for RL-enhanced Yantra X
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

def send_notification(subject, message, to_email):
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")

    if not smtp_user or not smtp_pass:
        print("[❌ Notification] SMTP credentials not found.")
        return False

    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(message, 'plain'))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.sendmail(smtp_user, to_email, msg.as_string())
        server.quit()
        print(f"[📨 Notification] Sent to {to_email}")
        return True
    except Exception as e:
        print(f"[❌ Notification Error] {e}")
        return False

send_notification(
    subject="Yantra X Alert",
    message="The Ghost detected extreme volatility in BTC/USDT.",
    to_email="bhatiaditya80@gmail.com"
)
