import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from services.logger_service import log_message

def send_notification(subject, message, to_email):
    """Send email notifications using SMTP (e.g., Gmail)."""
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")

    if not smtp_user or not smtp_pass:
        log_message("[Notification] ❌ SMTP credentials not found in environment.")
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
        log_message(f"[Notification] ✅ Email sent to {to_email}")
        return True
    except Exception as e:
        log_message(f"[Notification Error] {e}")
        return False

# Example test (can be commented out in production)
if __name__ == "__main__":
    send_notification(
        subject="Yantra X Alert",
        message="⚡ The Ghost detected extreme volatility in BTC/USDT.",
        to_email="bhatiaditya80@gmail.com"
    )
