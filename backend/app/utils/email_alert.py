import smtplib
from email.mime.text import MIMEText
import os

def send_temperature_alert_email(to_email, subject, body, smtp_user=None, smtp_pass=None):
    smtp_user = smtp_user or os.environ.get('ALERT_SMTP_USER')
    smtp_pass = smtp_pass or os.environ.get('ALERT_SMTP_PASS')
    if not smtp_user or not smtp_pass:
        raise RuntimeError('SMTP credentials not set')
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = smtp_user
    msg['To'] = to_email
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(smtp_user, smtp_pass)
        server.sendmail(smtp_user, [to_email], msg.as_string()) 