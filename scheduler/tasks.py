from celery import shared_task
from django.core.mail import send_mail
from .models import Emails
from django.utils import timezone
from auto_email import settings

@shared_task(bind=True)
def send_scheduled_email(self,email_id):
    try:
        email = Emails.objects.get(id=email_id)
        send_mail(
            email.subject,
            email.content,
            settings.EMAIL_HOST_USER,
            [email.reciever_email],
            fail_silently=False,
        )

        email.status = Emails.SENT
        email.save()
        return f"Email {email_id} sent successfully."
    except Exception as e:
        return f"Failed to send email {email_id}. Error: {str(e)}"
    
@shared_task(bind=True)
def trigger_scheduled_emails(self):
    now = timezone.now()
    scheduled_emails = Emails.objects.filter(scheduled_time__lte=now, status=Emails.PENDING)

    for email in scheduled_emails:
        send_scheduled_email.delay(email.id)
