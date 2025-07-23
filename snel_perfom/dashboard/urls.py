from django.urls import path
from .views import home, login_, logout_, access_refuse
app_name = 'dashboard'

urlpatterns = [
    path('', home, name='home'),
    path('login/', login_, name='login'),
    path('logout/', logout_, name='logout'),
    path('access_refuse/', access_refuse, name='access_refuse'),

]
