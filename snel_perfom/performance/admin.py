from django.contrib import admin

from performance.models import PerformanceMetric, PerformanceReview, Goal, Feedback

admin.site.register(PerformanceMetric)
admin.site.register(PerformanceReview)
admin.site.register(Goal)
admin.site.register(Feedback)
