from django.urls import path
from .views import (
    ai_recommendations_list_view,
    update_recommendation_status,
    formations_list_view,
    update_employee_training_status,
    manager_approval_list_view,
    approve_training_and_evaluate_skills_view
)

app_name = 'Skill_Training'
urlpatterns = [
    path('recommendation/', ai_recommendations_list_view, name='ai_recommandations_list'),
    path('recommendation/<int:pk>/update_status/', update_recommendation_status, name='update_recommendation_status'),
    path('list/', formations_list_view, name='formations_list'),
    path('update_status/<int:pk>/', update_employee_training_status, name='update_employee_training_status'),
    path('Training/approbation', manager_approval_list_view, name='manager_approval_list'),
    path('Training/approbation/<int:employee_training_pk>', approve_training_and_evaluate_skills_view, name='approve_training_and_evaluate_skills_view'),

]