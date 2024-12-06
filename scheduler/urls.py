from django.urls import path
from . import views
urlpatterns = [
    
    path('schedule-email/', views.schedule_email, name='schedule-email'),
  
]
