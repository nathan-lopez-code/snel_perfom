from django.urls import path
from .views import GoalListView, GoalCreateView, GoalUpdateView, GoalUpdateStatusView, PerformanceReviewListView, \
    PerformanceReviewCreateView, PerformanceReviewUpdateView

app_name = 'goals'

urlpatterns = [
    path('', GoalListView.as_view(), name='list'),
    path('create/', GoalCreateView.as_view(), name='create'),
    path('<int:pk>/update/', GoalUpdateView.as_view(), name='update'),
    path('<int:pk>/update_status/', GoalUpdateStatusView.as_view(), name='update_status'),
    path('evaluations/liste', PerformanceReviewListView.as_view(), name='perform-list'),
    path('evaluer/', PerformanceReviewCreateView.as_view(), name='perform-create'),
    path('<int:pk>/update/', PerformanceReviewUpdateView.as_view(), name='perform-update'),
]