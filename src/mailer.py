import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email(subject: str, html_content: str, to_email: str):
    """Sends an email with HTML content."""
    email_user = os.environ.get("EMAIL_USER")
    email_pass = os.environ.get("EMAIL_PASS")

    if not all([email_user, email_pass, to_email]):
        print("Email credentials or recipient not set. Skipping email.")
        return

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = email_user
    msg['To'] = to_email

    msg.attach(MIMEText(html_content, 'html'))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
            smtp_server.login(email_user, email_pass)
            smtp_server.sendmail(email_user, to_email, msg.as_string())
        print(f"Email sent successfully to {to_email}.")
    except Exception as e:
        print(f"Failed to send email: {e}")
