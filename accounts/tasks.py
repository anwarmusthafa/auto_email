from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from auto_email import settings
from datetime import timedelta
from django.utils.timezone import now
import logging
from .models import CustomUser

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def send_otp_to_email(self, name, to_email, otp):
    
    mail_subject = "OTP Code from Auto Email"

    
    # HTML content for the email
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>OTP Verification</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                margin: 0;
                padding: 20px;
            }}
            .container {{
                background-color: #ffffff;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
                padding: 20px;
                max-width: 600px;
                margin: auto;
            }}
            h2 {{
                color: #003366; /* Dark blue color */
            }}
            .otp {{
                font-size: 24px;
                font-weight: bold;
                color: #003366; /* Dark blue color */
                background-color: #e7f0ff; /* Light blue background */
                padding: 10px;
                border-radius: 4px;
                text-align: center;
            }}
            .footer {{
                margin-top: 20px;
                font-size: 12px;
                color: #777;
                text-align: center;
            }}
            img.logo {{
                max-width: 150px;
                margin: 0 auto;
                display: block;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>OTP Verification</h2>
            <p>Dear {name},</p>
            <p>Your OTP code is:</p>
            <div class="otp">{otp}</div>
            <p>This code is valid for a limited time. Please do not share it with anyone.</p>
            <div class="footer">
                &copy; Auto Email. All rights reserved.
            </div>
        </div>
    </body>
    </html>
    """
    email = EmailMultiAlternatives(
        subject=mail_subject,
        body=strip_tags(html_content),
        from_email=settings.EMAIL_HOST_USER,
        to=[to_email],
    )
    email.attach_alternative(html_content, "text/html") 

    email.send(fail_silently=False)
    return "Done"

@shared_task(bind=True)
def remove_unverified_users(self):
    current_time = now()
    
    # Filter unverified users who joined more than 7 days ago
    unverified_users = CustomUser.objects.filter(
        is_verified=False, 
        created_at__lte=current_time - timedelta(days=7)
    )
    
    try:
        # Perform a bulk delete for efficiency
        count, _ = unverified_users.delete()
        return f"Successfully deleted {count} unverified users."
    except Exception as e:
        return f"Failed to delete unverified users: {e}"