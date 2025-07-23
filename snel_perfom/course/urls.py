from django.urls import path

from course.views import detail_course, edit_course, create_course, list_course, mark_attente_validation, mark_course_inscrit

app_name = 'course'

urlpatterns = [
    path('list/', list_course, name='list_course'),
    path('<int:course_id>/detail', detail_course, name='detail_course'),
    path('<int:course_id>/edit', edit_course, name='edit_course'),
    path('creer/', create_course, name='create_course'),
    path('<int:course_id>/terminer/', mark_attente_validation, name='mark_attente_validation'),
    path('<int:course_id>/inscrit/', mark_course_inscrit, name='mark_course_inscrit'),
]