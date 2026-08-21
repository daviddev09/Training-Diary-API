import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from celery import Task

from app.core.config import settings
from app.workers.celery_app import app
from app.workers.utils.smtp_util import (
    create_diary_pdf_created_notification_html_message,
    create_verify_register_html_message,
)


def create_message(recipient: str, html_content: str, subject: str) -> MIMEMultipart:
    msg = MIMEMultipart()

    msg["From"] = settings.smtp_email
    msg["To"] = recipient
    msg["Subject"] = subject

    text_content = html_content
    msg.attach(MIMEText(text_content, "html"))
    return msg


@app.task(name="app.workers.smtp_worker.send_confirmation_code")
def send_confirmation_code(
    recipient_email: str, subject: str, name: str, code: str
) -> None:
    html_content = create_verify_register_html_message(name, recipient_email, code)
    msg = create_message(recipient_email, html_content, subject)

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
        server.starttls()
        server.login(settings.smtp_email, settings.smtp_app_password)
        server.send_message(msg)
        print("-----Сообщение отпрвлено-----")


@app.task(bind=True, max_retries=10, default_retry_delay=360)
def send_notification_about_pdf(
    self: Task, recipient_email: str, name: str, pdf_link: str
) -> None:
    try:
        html_content = create_diary_pdf_created_notification_html_message(
            name, pdf_link
        )
        msg = create_message(recipient_email, html_content, subject="Генерация PDF")
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            server.starttls()
            server.login(settings.smtp_email, settings.smtp_app_password)
            server.send_message(msg)
            print("-----Сообщение отпрвлено-----")
    except Exception as exc:
        print(f"\nFail: {exc}")
        self.retry(exc=exc)
