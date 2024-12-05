from rest_framework import serializers
from .models import CustomUser


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser  
        fields = ['id', 'name', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}} 

    def create(self, validated_data):
        password = validated_data.pop('password')  # Remove password from validated data
        user = CustomUser(**validated_data)  # Create user instance without password
        user.set_password(password)  # Hash the password before saving
        user.save()  # Save the user with the hashed password
        return user