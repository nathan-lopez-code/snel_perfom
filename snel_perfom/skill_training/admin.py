from django.contrib import admin

from skill_training.models import Skill, SkillCategory, EmployeeSkill, TrainingCourse, EmployeeTraining, \
    SkillGapAnalysis, RecommendedTraining

admin.site.register(Skill)
admin.site.register(SkillCategory)
admin.site.register(EmployeeSkill)
admin.site.register(TrainingCourse)
admin.site.register(EmployeeTraining)
admin.site.register(SkillGapAnalysis)
admin.site.register(RecommendedTraining)
