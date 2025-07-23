from django.urls import path
from .views import home_view, employee_profile


app_name = 'employee'


urlpatterns = [
    path('home/', home_view, name='home'),
    path('profile/<int:pk>', employee_profile, name='employee_profile'),
]