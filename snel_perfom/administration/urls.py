from django.urls import path
from .views import dashboard


app_name = 'administration'

urlpatterns = [
    path('dashboard', dashboard, name='dashboard'),
]