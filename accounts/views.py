from django.shortcuts import render
from .models import CustomUser
from rest_framework.decorators import api_view
from .serializers import UserSerializer
from rest_framework.response import Response
from rest_framework import status
from .tasks import send_otp_to_email
from django.contrib.auth.hashers import check_password
# Create your views here.

@api_view(['POST'])
def register_user(request):
    password = request.data.get('password')
    confirm_password = request.data.get('confirm-password')
    if password != confirm_password:
        return Response({"error": "Passwords do not match"}, status=status.HTTP_400_BAD_REQUEST)
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

@api_view(['POST'])
def verify_otp(request):
    user_id = request.data.get('uuid')
    otp = request.data.get('otp')
    try:
        if not user_id or not otp:
            return Response({"error": "User ID and OTP are required."}, status=status.HTTP_400_BAD_REQUEST)

        user = CustomUser.objects.get(uuid=user_id)
        if check_password(otp, user.otp):
            user.is_verified = True
            user.save()
            return Response({"message": "OTP verified successfully"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)
    except CustomUser.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    except ValueError:
        return Response({"error": "Invalid input provided."}, status=status.HTTP_400_BAD_REQUEST)
    except Exception:
        return Response({"error": "An unexpected error occurred. Please try again later."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
