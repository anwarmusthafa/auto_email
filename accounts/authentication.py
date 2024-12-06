from django.contrib.auth.backends import BaseBackend
from .models import CustomUser
from django.db.models import Q

class EmailBackend(BaseBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        try:
            user = CustomUser.objects.get(email=email)
            if user.check_password(password):
                return user
        except CustomUser.DoesNotExist:
            return None
        return None
