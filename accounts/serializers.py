import re
from rest_framework import serializers
from .models import CustomUser
import random
from django.contrib.auth.hashers import make_password

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser  
        fields = ['id', 'uuid', 'name', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}} 

    def create(self, validated_data):
        """
        Create a new user instance and hash the password.
        """
        password = validated_data.pop('password')  # Remove password from validated data
        user = CustomUser(**validated_data)
        user.set_password(password)  # Hash the password before saving

        # Generate, hash, and save OTP
        otp = self.generate_otp()
        user.otp = make_password(otp)  # Hash the OTP before saving
        user.save()
        user.plain_otp = otp
        return user

    @staticmethod
    def generate_otp(length=6):
        """
        Generate a random numeric OTP of the specified length.
        """
        return ''.join(random.choices('0123456789', k=length))
