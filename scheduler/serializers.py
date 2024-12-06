from rest_framework import serializers
from .models import Emails

class EmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Emails
        fields = ['id', 'sender', 'reciever_email', 'subject', 'content', 'scheduled_time', 'status']
        read_only_fields = ['id', 'status']
