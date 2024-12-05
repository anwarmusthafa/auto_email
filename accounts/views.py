from django.shortcuts import render
from .models import CustomUser
from rest_framework.decorators import api_view
from .serializers import UserSerializer
from rest_framework.response import Response
from rest_framework import status
from .tasks import send_otp_to_email
# Create your views here.

@api_view(['POST'])
def register_user(request):
    serializer = UserSerializer(data=request.data) 
    try:
        if serializer.is_valid():
            user = serializer.save()
            # Send the OTP to the user's email using Celery
            send_otp_to_email.delay(user.name, user.email, user.plain_otp)

            # Include user ID in the response
            return Response({
                "message": "User registered successfully. An OTP has been sent to your email.",
                "user_id": user.uuid  # Send user ID to the frontend
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
