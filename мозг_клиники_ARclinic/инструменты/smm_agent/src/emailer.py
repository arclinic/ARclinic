import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_email_report(html_content: str, subject: str, to_email: str) -> bool:
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_email = os.getenv("SMTP_EMAIL", "")
    smtp_password = os.getenv("SMTP_PASSWORD", "")

    if not smtp_email or not smtp_password or smtp_password.startswith("your_"):
        print("[EMAIL] Ошибка: не настроены SMTP_EMAIL / SMTP_PASSWORD в .env")
        print("[EMAIL] Для Gmail нужен пароль приложения: https://myaccount.google.com/apppasswords")
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = smtp_email
    msg["To"] = to_email

    msg.attach(MIMEText(html_content, "html", "utf-8"))

    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as server:
            server.starttls()
            server.login(smtp_email, smtp_password)
            server.sendmail(smtp_email, [to_email], msg.as_string())
        print(f"[EMAIL] Отчёт отправлен на {to_email}")
        return True
    except Exception as e:
        print(f"[EMAIL] Ошибка отправки: {e}")
        return False
