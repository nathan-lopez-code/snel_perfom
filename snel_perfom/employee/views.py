from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404

from skill_training.models import EmployeeSkill, RecommendedTraining, EmployeeTraining
from .models import Employee


def home_view(request):


    context = {
        'employee': request.user,
        'enrollments': EmployeeTraining.objects.filter(employee=request.user).order_by('-enrollment_date'),
    }

    return render(request, 'employee_page.html', context)


def employee_profile(request, pk):

    employee = get_object_or_404(
        Employee.objects.select_related(
            'department', 'position', 'manager'
        ).prefetch_related(
            Prefetch('employee_skills',
                     queryset=EmployeeSkill.objects.select_related('skill', 'assessed_by').order_by('skill__name')),
            Prefetch('trainings_taken',
                     queryset=EmployeeTraining.objects.select_related('course').order_by('-enrollment_date')),
            Prefetch('recommended_trainings',
                     queryset=RecommendedTraining.objects.select_related('training_course').order_by(
                         '-recommendation_date')),
        ),
        pk=pk
    )

    context = {
        'employee': employee,
        'employee_skills': employee.employee_skills.all(),  # Accéder aux données pré-chargées
        'employee_trainings': employee.trainings_taken.all(),  # Accéder aux données pré-chargées
        'recommended_trainings': employee.recommended_trainings.all(),  # Accéder aux données pré-chargées
    }
    return render(request, 'employee_profile.html', context)

