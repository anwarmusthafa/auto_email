from django.shortcuts import render
from .models import Emails
from .serializers import EmailSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
import re
from datetime import datetime
from django.utils.timezone import make_aware, now


# Create your views here.
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def schedule_email(request):
    user = request.user
    email = request.data.get('email')
    subject = request.data.get('subject')
    content = request.data.get('content')
    scheduled_date = request.data.get('scheduled_date')
    scheduled_time = request.data.get('scheduled_time')

    if not email or not subject or not content or not scheduled_date or not scheduled_time:
        return Response({"error": "All fields (email, subject, content, scheduled_date, scheduled_time) are required."}, 
                        status=status.HTTP_400_BAD_REQUEST)

    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        return Response({"error": "Invalid email format."}, status=status.HTTP_400_BAD_REQUEST)
    if len(subject) > 100:
        return Response({"error": "Email content cannot exceed 100 characters."}, status=status.HTTP_400_BAD_REQUEST)
    try:
        combined_datetime = make_aware(datetime.strptime(f"{scheduled_date} {scheduled_time}", "%Y-%m-%d %H:%M:%S"))
    except ValueError:
        return Response({"error": "Invalid date or time format. Use 'YYYY-MM-DD' for date and 'HH:MM:SS' for time."}, 
                        status=status.HTTP_400_BAD_REQUEST)
    
    # Ensure the scheduled time is not in the past
    if combined_datetime < now():
        return Response({"error": "Scheduled time cannot be in the past."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        serializer = EmailSerializer(data={
            'sender': user.id,
            'reciever_email': email,
            'subject': subject,
            'content': content,
            'scheduled_time': combined_datetime
        })
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Email scheduled successfully."}, status=status.HTTP_201_CREATED)
        else:
            return Response({"error": "Failed to schedule the email. Please check your inputs."}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error":"An unexpected error occurred, Please try again later "}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
