from django.urls import path

from .models import ElementEvaluation
from .views import GoalListView, GoalCreateView, GoalUpdateView, GoalUpdateStatusView, PerformanceReviewListView, \
    PerformanceReviewCreateView, PerformanceReviewUpdateView, EnrollInTrainingView, ElementEvaluationCreate, \
    ListeElementEvaluation, PerformanceReviewDetailView

app_name = 'goals'

urlpatterns = [
    path('', GoalListView.as_view(), name='list'),
    path('create/', GoalCreateView.as_view(), name='create'),
    path('<int:pk>/update/', GoalUpdateView.as_view(), name='update'),
    path('<int:pk>/update_status/', GoalUpdateStatusView.as_view(), name='update_status'),
    path('evaluations/liste', PerformanceReviewListView.as_view(), name='perform-list'),
    path('evaluer/', PerformanceReviewCreateView.as_view(), name='perform-create'),
    path('<int:pk>/update/', PerformanceReviewUpdateView.as_view(), name='perform-update'),
    path('<int:pk>/details/', PerformanceReviewDetailView.as_view(), name='perform-detail'),
    path('<int:pk>/Enroller/', EnrollInTrainingView.as_view(), name='perform-enroller'),
    path('element/create/', ElementEvaluationCreate.as_view(), name='element-create'),
    path('element/liste/', ListeElementEvaluation.as_view(), name='element-liste'),
]