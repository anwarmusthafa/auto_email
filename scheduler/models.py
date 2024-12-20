from django.db import models
from accounts.models import CustomUser

class Emails(models.Model):
    PENDING = 0
    SENT = 1
    STATUS_CHOICES = (
        (PENDING, 'Pending'),
        (SENT, 'Sent')
    )

    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  # Consider cascade deletion
    reciever_email = models.EmailField()
    subject = models.CharField(max_length=100)
    content = models.TextField()
    scheduled_time = models.DateTimeField()
    status = models.IntegerField(choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['scheduled_time', 'status']),
        ]

    def __str__(self):
        return f"Email from {self.sender}'s email"
