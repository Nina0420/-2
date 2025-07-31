
from django.core.mail import EmailMessage, EmailMultiAlternatives
from celery import shared_task
from django.conf import settings

@shared_task(bind=True, default_retry_delay=300, max_retries=5)
def send_auto_message(self, mail_subject, message, to_email, html_content=None):


    try:
        if html_content:
            msg = EmailMultiAlternatives(mail_subject, message, settings.EMAIL_HOST_USER, [to_email])
            msg.attach_alternative(html_content, "text/html")
        else:
            msg = EmailMessage(mail_subject, message, settings.EMAIL_HOST_USER, [to_email])

        msg.send()
        print(f"Email '{mail_subject}' sent successfully to {to_email}")
    exce except Exception as exc:
        print(f"Failed to send email '{mail_subject}' to {to_email}: {exc}")

        raise self.retry(exc=exc, countdown=60)