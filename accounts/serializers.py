import re
from rest_framework import serializers
from .models import CustomUser
import random
from django.contrib.auth.hashers import make_password

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser  
        fields = ['id','uuid','name', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}} 

    def create(self, validated_data):
        """
        Create a new user instance and hash the password.
        """
        password = validated_data.pop('password')  # Remove password from validated data
        user = CustomUser(**validated_data)
        user.set_password(password) # Hash the password before saving

        # Generate, hash, and save OTP
        otp = self.generate_otp()
        user.otp = make_password(otp)  # Hash the OTP before saving
        user.save()
        user.plain_otp = otp
        return user

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value

    def validate_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Name cannot be empty.")
        
        if len(value) < 3:
            raise serializers.ValidationError("Name must be at least 3 characters long.")

        if not value.isalpha():
            raise serializers.ValidationError("Name must contain only alphabetic characters.")

        return value

    def validate_password(self, value):
        """
        Validate that the password meets the required complexity rules.
        """
        errors = []
        if len(value) < 6:
            errors.append("at least 6 characters")
        if not re.search(r"[A-Z]", value):
            errors.append("one uppercase letter")
        if not re.search(r"[0-9]", value):
            errors.append("one numeric character")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            errors.append("one special character")

        if errors:
            raise serializers.ValidationError(f"Password must contain {', '.join(errors)}.")

        return value
    @staticmethod
    def generate_otp(length=6):
        """
        Generate a random numeric OTP of the specified length.
        """
        return ''.join(random.choices('0123456789', k=length))
