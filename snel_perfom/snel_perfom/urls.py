"""
    configuration URL de l'application snel_perfom .

"""
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dashboard.urls', namespace='dashboard')), # application index
    path('training/', include('skill_training.urls', namespace='Skill_Training')), # application principal
    path('employee/', include('employee.urls', namespace='employee')), # application pour l'employee
    path('cours/', include('course.urls', namespace='course')), # app pour les formations
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) # configuration de fichier static pour l'hebergment
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

