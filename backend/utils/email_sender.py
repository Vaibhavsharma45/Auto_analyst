"""
Email Sender — Send PDF reports via SMTP
Supports Gmail, Outlook, and any SMTP server
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

    Required env vars:
      EMAIL_SENDER   = your Gmail address
      EMAIL_PASSWORD = Gmail App Password (not regular password)
    """
    sender   = os.getenv("EMAIL_SENDER", "").strip()
    password = os.getenv("EMAIL_PASSWORD", "").strip()
    smtp_host = os.getenv("EMAIL_SMTP", "smtp.gmail.com")
    smtp_port = int(os.getenv("EMAIL_PORT", "587"))

    # Validate config
    if not sender:
        return {"success": False, "error": "EMAIL_SENDER not configured. Add it in Render environment variables."}
    if not password:
        return {"success": False, "error": "EMAIL_PASSWORD not configured. Add Gmail App Password in Render environment variables."}
    if not to_email or "@" not in to_email:
        return {"success": False, "error": "Invalid recipient email address."}

    try:
        msg = MIMEMultipart()
        msg["From"]    = f"DataMind Pro <{sender}>"
        msg["To"]      = to_email
        msg["Subject"] = f"DataMind Pro — Analysis Report: {dataset_name}"

        body = f"""Hello,

Your DataMind Pro analysis report is ready and attached to this email.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 Report Details
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 Dataset   : {dataset_name}
 Generated : {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{summary if summary else 'The full analysis report is attached as a PDF file.'}

You can view the full interactive analysis at:
https://datamind-pro.onrender.com

Best regards,
DataMind Pro — AI-Powered Data Analysis Platform
""".strip()

        msg.attach(MIMEText(body, "plain"))

        # Attach PDF
        if pdf_path and os.path.exists(pdf_path):
            with open(pdf_path, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())
                encoders.encode_base64(part)
                filename = f"datamind-report-{dataset_name.replace(' ', '-')}.pdf"
                part.add_header("Content-Disposition", f'attachment; filename="{filename}"')
                msg.attach(part)
        else:
            return {"success": False, "error": "PDF report file not found. Generate the report first."}

        # Send
        with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(sender, password)
            server.sendmail(sender, to_email, msg.as_string())

        return {
            "success": True,
            "message": f"Report successfully sent to {to_email}",
            "sender": sender
        }

    except smtplib.SMTPAuthenticationError:
        return {
            "success": False,
            "error": "Gmail authentication failed. Make sure you are using an App Password, not your regular Gmail password. Enable 2FA first, then generate an App Password at myaccount.google.com/apppasswords"
        }
    except smtplib.SMTPRecipientsRefused:
        return {"success": False, "error": f"Recipient email address rejected: {to_email}"}
    except smtplib.SMTPException as e:
        return {"success": False, "error": f"SMTP error: {str(e)}"}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}