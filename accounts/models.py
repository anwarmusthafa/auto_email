import re
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.core.exceptions import ValidationError
import uuid 

class CustomUserManager(BaseUserManager):
    def create_user(self, email, name, password=None, **extra_fields):
        """
        Create and return a user with an email, name, and password.
        """
        if not email:
            raise ValueError("The Email field must be set.")
        if not self.is_valid_email(email):
            raise ValidationError("Email is not in a proper format.")
        if not name:
            raise ValueError("The Name field must be set.")
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None, **extra_fields):
        """
        Create and return a superuser with an email, name, and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, name, password, **extra_fields)

    @staticmethod
    def is_valid_email(email):
        """
        Validate the email format.
        """
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_regex, email) is not None


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model that uses email as the username.
    """
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=254, unique=True)
    otp = models.CharField(max_length=6, blank=True, null=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return f"{self.name} - {self.email}"

    def clean(self):
        if self.otp and not self.is_valid_otp(self.otp):
            raise ValidationError("OTP must be a 6-digit number.")

    @staticmethod
    def is_valid_otp(otp):
        return otp.isdigit() and len(otp) == 6
