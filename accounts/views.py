from .models import CustomUser
from .serializers import UserSerializer
from .tasks import send_otp_to_email
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
import re
from django_ratelimit.decorators import ratelimit
from django_ratelimit.core import is_ratelimited



@api_view(['POST'])
def register_user(request):
    """Register a new user."""
    print(request.data)
    password = request.data.get('password')
    confirm_password = request.data.get('confirmPassword')
    email = request.data.get('email')
    name = request.data.get('name')

    if password != confirm_password:
        return Response({"error": "Passwords do not match."}, status=status.HTTP_400_BAD_REQUEST)
    
    if CustomUser.objects.filter(email=email).exists():
        return Response({"error": "User with this email already exists"}, status=status.HTTP_400_BAD_REQUEST)
    
    reg_name = r'^[a-zA-Z]+(?: [a-zA-Z]+)*$'
    if not name or len(name) < 3 or not re.match(reg_name, name):
        return Response({"error": "Name must be at least 3 characters long and contain only letters."}, status=status.HTTP_400_BAD_REQUEST)

    serializer = UserSerializer(data=request.data)
    try:
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            print("user",user)
            # Send the OTP to the user's email using Celery
            send_otp_to_email.delay(user.name, user.email, user.plain_otp)
            return Response(
                {
                    "message": "User registered successfully. An OTP has been sent to your email.",
                    "user_id": user.uuid
                },
                status=status.HTTP_201_CREATED
            )
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def verify_otp(request):
    """Verify the OTP sent to the user's email."""
    user_id = request.data.get('uuid')
    otp = request.data.get('otp')

    try:
        if not user_id or not otp:
            return Response({"error": "User ID and OTP are required."}, status=status.HTTP_400_BAD_REQUEST)

        user = CustomUser.objects.get(uuid=user_id)
        if user.is_verified:
            return Response({"error": "User is already verified."}, status=status.HTTP_400_BAD_REQUEST)
        if check_password(otp, user.otp):
            user.is_verified = True
            user.save()
            return Response({"message": "OTP verified successfully."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)

    except CustomUser.DoesNotExist:
        return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
    except ValueError:
        return Response({"error": "Invalid input provided."}, status=status.HTTP_400_BAD_REQUEST)
    except Exception:
        return Response({"error": "An unexpected error occurred. Please try again later."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@ratelimit(key='ip', rate='5/m', block=True)
def login_user(request):
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response({"error": "Both email and password are required."}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(email=email, password=password)
    if not user:
        return Response({"error": "Invalid email or password."}, status=status.HTTP_400_BAD_REQUEST)
    
    if not user.is_verified:
        return Response({"error": "User OTP is not verified."}, status=status.HTTP_400_BAD_REQUEST)

    # Generate tokens
    tokens = RefreshToken.for_user(user)
    return Response(
        {
            "message": "Login successful.",
            "access": str(tokens.access_token),
            "refresh": str(tokens)
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def home(request):
    print(request.user)
    return Response({"message": "Welcome to the AutoEmail API."}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    refresh_token = request.data.get('refresh')
    if not refresh_token:
        return Response({"error": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)
    try:
        # Blacklist the refresh token
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({"message": "Successfully logged out."}, status=status.HTTP_200_OK)

    except TokenError:
        return Response({"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['POST'])
def refresh_token(request):
    refresh_token = request.data.get('refresh')
    if not refresh_token:
        return Response({"error": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)
    try:
        token = RefreshToken(refresh_token)
        new_access_token = token.access_token
        new_refresh_token = str(token)
        return Response({
            "access": str(new_access_token),
            "refresh": new_refresh_token 
        }, status=status.HTTP_200_OK)
    except TokenError:
        return Response({"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": "An unexpected error occurred. Please try again later."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)