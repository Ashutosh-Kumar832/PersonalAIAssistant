import smtplib
import logging
from email.message import EmailMessage
from utils.smtp_config import read_smtp_config  

# Logging setup
logging.basicConfig(level=logging.INFO)

# Load SMTP Configuration from XML
smtp_config = read_smtp_config()

def send_email_notification(to_email: str, subject: str, body: str):
    """Send an email notification using SMTP details from XML config."""
    try:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = smtp_config["username"]
        msg["To"] = to_email
        msg.set_content(body)

        with smtplib.SMTP(smtp_config["server"], smtp_config["port"]) as server:
            if smtp_config["use_tls"]:
                server.starttls()
            server.login(smtp_config["username"], smtp_config["password"])
            server.send_message(msg)

        logging.info(f"Email notification sent to {to_email}")

    except Exception as e:
        logging.error(f"Failed to send email: {e}")
