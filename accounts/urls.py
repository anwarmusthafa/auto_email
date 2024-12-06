from django.urls import path
from . import views
urlpatterns = [
    
    path('register/', views.register_user, name='register-user'),
    path('verify-otp/', views.verify_otp, name='verify-otp'),
    path('login/', views.login_user, name='login-user'),
]
