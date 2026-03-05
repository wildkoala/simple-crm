import logging
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

logger = logging.getLogger(__name__)

# Email configuration from environment
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", "noreply@pretorin.com")
SMTP_FROM_NAME = os.getenv("SMTP_FROM_NAME", "Pretorin CRM")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:8080")


async def send_email(
    to_email: str,
    subject: str,
    html_content: str,
    text_content: Optional[str] = None
):
    """Send email using SMTP"""

    # Skip if SMTP not configured (development mode)
    if not SMTP_USERNAME or not SMTP_PASSWORD:
        logger.info("[EMAIL] SMTP not configured. Would send email with subject: %s", subject)
        return

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = f"{SMTP_FROM_NAME} <{SMTP_FROM_EMAIL}>"
    msg['To'] = to_email

    # Add text and HTML parts
    if text_content:
        text_part = MIMEText(text_content, 'plain')
        msg.attach(text_part)

    html_part = MIMEText(html_content, 'html')
    msg.attach(html_part)

    # Send email
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        logger.error("Failed to send email: %s", e)
        raise


async def send_password_reset_email(email: str, name: str, reset_token: str):
    """Send password reset email"""
    reset_link = f"{FRONTEND_URL}/reset-password?token={reset_token}"

    subject = "Password Reset Request - Pretorin CRM"

    text_content = f"""
Hello {name},

You requested a password reset for your Pretorin CRM account.

Click the link below to reset your password:
{reset_link}

This link will expire in 24 hours.

If you didn't request this, please ignore this email.

Best regards,
Pretorin CRM Team
"""

    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .button {{
            display: inline-block;
            padding: 12px 24px;
            background-color: #2563eb;
            color: white !important;
            text-decoration: none;
            border-radius: 6px;
            margin: 20px 0;
        }}
        .footer {{ margin-top: 30px; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <h2>Password Reset Request</h2>
        <p>Hello {name},</p>
        <p>You requested a password reset for your Pretorin CRM account.</p>
        <p>Click the button below to reset your password:</p>
        <a href="{reset_link}" class="button">Reset Password</a>
        <p>Or copy and paste this link into your browser:</p>
        <p style="word-break: break-all; color: #2563eb;">{reset_link}</p>
        <p><strong>This link will expire in 24 hours.</strong></p>
        <p>If you didn't request this, please ignore this email.</p>
        <div class="footer">
            <p>Best regards,<br>Pretorin CRM Team</p>
        </div>
    </div>
</body>
</html>
"""

    await send_email(email, subject, html_content, text_content)
