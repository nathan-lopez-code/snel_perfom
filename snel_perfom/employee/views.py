from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404

from performance.models import Goal, GoalDepartement
from skill_training.models import EmployeeSkill, RecommendedTraining, EmployeeTraining
from .models import Employee


def home_view(request):
    """
        Portail employee : affiche les informations sur l'employee
        ainsi que les formations encours
    """

    context = {
        'employee': request.user,
        'goals': Goal.objects.filter(employee=request.user),
        'goal_departement': GoalDepartement.objects.filter(department=request.user.department),
        'enrollments': EmployeeTraining.objects.filter(employee=request.user).order_by('-enrollment_date'),
    }

    return render(request, 'employee_page.html', context)



def employee_profile(request, pk):

    """
        Page de profile pour l'employee , affiche ses informations personelles ,
        ses competences , l'historique de formations suivi .
    """

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

