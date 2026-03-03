import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 6. Generate and Send Verification OTP — Email Delivery
def send_otp_email(to_email: str, otp: str) -> bool:
    """
    Sends an OTP code to the given email address using Gmail SMTP.
    Returns True if successful, False otherwise.
    """
    sender_email    = os.getenv("EMAIL_ADDRESS")
    sender_password = os.getenv("EMAIL_APP_PASSWORD")

    if not sender_email or not sender_password:
        print("WARNING: EMAIL_ADDRESS or EMAIL_APP_PASSWORD not set in .env")
        return False

    # Build the email
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Your Zynergy AI Verification Code"
    msg["From"]    = f"Zynergy AI <{sender_email}>"
    msg["To"]      = to_email

    # Plain text fallback
    text_body = f"""
Your Zynergy AI verification code is:

    {otp}

This code expires in 10 minutes.
If you did not request this, please ignore this email.

– The Zynergy AI Team
"""

    # HTML body
    html_body = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <style>
    body {{ font-family: Arial, sans-serif; background: #0f172a; color: #e2e8f0; margin: 0; padding: 0; }}
    .container {{ max-width: 480px; margin: 40px auto; background: #1e293b; border-radius: 16px; overflow: hidden; border: 1px solid #334155; }}
    .header {{ background: linear-gradient(135deg, #2563eb, #1d4ed8); padding: 32px; text-align: center; }}
    .header h1 {{ margin: 0; font-size: 28px; font-weight: 900; color: #fff; letter-spacing: -1px; }}
    .header p  {{ margin: 6px 0 0; color: #bfdbfe; font-size: 13px; }}
    .body  {{ padding: 36px 32px; text-align: center; }}
    .body p {{ color: #94a3b8; font-size: 14px; margin-bottom: 24px; }}
    .otp-box {{ display: inline-block; background: #0f172a; border: 2px solid #2563eb; border-radius: 12px; padding: 20px 40px; margin-bottom: 24px; }}
    .otp-code {{ font-size: 42px; font-weight: 900; letter-spacing: 12px; color: #3b82f6; }}
    .note {{ color: #475569; font-size: 12px; margin-top: 24px; }}
    .footer {{ background: #0f172a; padding: 20px; text-align: center; color: #475569; font-size: 12px; border-top: 1px solid #1e293b; }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>Zynergy AI</h1>
      <p>AI-Powered Interview System</p>
    </div>
    <div class="body">
      <p>Use the verification code below to reset your password.<br>This code is valid for <strong>10 minutes</strong>.</p>
      <div class="otp-box">
        <div class="otp-code">{otp}</div>
      </div>
      <p class="note">If you did not request a password reset, you can safely ignore this email.</p>
    </div>
    <div class="footer">
      &copy; 2025 Zynergy AI &nbsp;·&nbsp; AI Interview System
    </div>
  </div>
</body>
</html>
"""

    msg.attach(MIMEText(text_body, "plain"))
    msg.attach(MIMEText(html_body,  "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, to_email, msg.as_string())
        print(f"✅ OTP email sent to {to_email}")
        return True
    except Exception as e:
        print(f"❌ Failed to send OTP email: {e}")
        return False
