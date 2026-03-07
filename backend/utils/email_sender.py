"""
backend/utils/email_sender.py
Send PDF report via email using SMTP
"""
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from datetime import datetime

try:
    from dotenv import load_dotenv
    load_dotenv(override=True)
except ImportError:
    pass


def send_report_email(to_email: str, pdf_path: str, dataset_name: str, summary: str = "") -> dict:
    """
    Send PDF report as email attachment.
    Configure via .env:
      EMAIL_SENDER=your@gmail.com
      EMAIL_PASSWORD=your_app_password
      EMAIL_SMTP=smtp.gmail.com
      EMAIL_PORT=587
    """
    sender = os.getenv("EMAIL_SENDER", "")
    password = os.getenv("EMAIL_PASSWORD", "")
    smtp_host = os.getenv("EMAIL_SMTP", "smtp.gmail.com")
    smtp_port = int(os.getenv("EMAIL_PORT", "587"))

    if not sender or not password:
        return {"success": False, "error": "EMAIL_SENDER aur EMAIL_PASSWORD .env mein set karo"}

    try:
        msg = MIMEMultipart()
        msg["From"] = sender
        msg["To"] = to_email
        msg["Subject"] = f"DataMind Pro — Analysis Report: {dataset_name}"

        body = f"""
Namaste!

Aapka DataMind Pro analysis report attached hai.

Dataset: {dataset_name}
Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}

{summary if summary else 'Full analysis report PDF mein hai.'}

---
DataMind Pro — AI-Powered Data Analysis Platform
        """.strip()

        msg.attach(MIMEText(body, "plain"))

        # Attach PDF
        with open(pdf_path, "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename=datamind-report.pdf")
            msg.attach(part)

        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(sender, password)
            server.sendmail(sender, to_email, msg.as_string())

        return {"success": True, "message": f"Report sent to {to_email}!"}

    except Exception as e:
        return {"success": False, "error": str(e)}
