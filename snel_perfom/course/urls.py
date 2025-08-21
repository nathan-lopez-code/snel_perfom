from django.urls import path

from course.views import detail_course, edit_course, create_course, list_course, mark_attente_validation, \
    mark_course_inscrit, TrainingCourseCreateView, TrainingCourseUpdateView, TrainingCourseDeleteView, \
    TrainingCourseListView

app_name = 'course'

urlpatterns = [
    path('list/', list_course, name='list_course'),
    path('<int:course_id>/detail', detail_course, name='detail_course'),
    path('<int:course_id>/edit', edit_course, name='edit_course'),
    path('creer/', create_course, name='create_course'),
    path('<int:course_id>/terminer/', mark_attente_validation, name='mark_attente_validation'),
    path('<int:course_id>/inscrit/', mark_course_inscrit, name='mark_course_inscrit'),
    path('add/', TrainingCourseCreateView.as_view(), name='trainingcourse-add'),
    path('liste', TrainingCourseListView.as_view(), name='trainingcourse-list'),
    path('<int:pk>/edit/', TrainingCourseUpdateView.as_view(), name='trainingcourse-update'),
    path('<int:pk>/delete/', TrainingCourseDeleteView.as_view(), name='trainingcourse-delete'),
]