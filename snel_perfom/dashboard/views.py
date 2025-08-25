from datetime import date, timedelta
from django.contrib.auth import login, logout
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from dashboard.forms import LoginForm
from employee.models import Employee, Department
from performance.models import GoalDepartement
from skill_training.models import RecommendedTraining, EmployeeTraining
from django.contrib.auth import authenticate
from .utils_ import (
    calculate_total_workforce,
    calculate_retention_rate,
    calculate_turnover_rate,
    calculate_average_seniority,
    calculate_total_payroll,
    calculate_average_cost_per_employee,
    get_workforce_distribution_by_department,
    get_workforce_distribution_by_gender,
    get_workforce_distribution_by_age_range,
    get_workforce_distribution_by_contract_type
)

@login_required(login_url='dashboard:login')
def access_refuse(request):
    return render(request, 'acces_devied.html')



@login_required(login_url='dashboard:login') # l'utilisateur doit etre connecter pour voir cette page
def home(request):
    """
        Dashboard home page, tableau de bord pour les managers et hr
    """

    if request.user.is_manager is False and request.user.is_hr is False:
        return redirect('dashboard:access_refuse')

    today = date.today()
    user = request.user
    one_year_ago = today - timedelta(days=365*5)

    # configuration du contexte d'affichage en fonction du role
    if user.is_hr:

        kpis = {
            'total_workforce': calculate_total_workforce(department=None),
            'retention_rate': calculate_retention_rate(one_year_ago, today, department=None),
            'turnover_rate': calculate_turnover_rate(one_year_ago, today, department=None),
            'average_seniority': calculate_average_seniority(),
            'total_payroll': calculate_total_payroll(department=None),
            'average_cost_per_employee': calculate_average_cost_per_employee(department=None),
        }
        distributions = {
            'by_department': get_workforce_distribution_by_department(),
            'by_gender': get_workforce_distribution_by_gender(),
            'by_age_range': get_workforce_distribution_by_age_range(department=None),
            'by_contract_type': get_workforce_distribution_by_contract_type(),
        }
        context = {
            'active_link':1,
            'kpis': kpis,
            'employees': Employee.objects.all().exclude(is_superuser=True),
            'user': user,
            'distributions': distributions,
            'pending_recommendation': RecommendedTraining.objects.filter(status='En attente').count(),
            'rate_a_r': taux_de_recommandation_accepter(),
            'enrol_cours': EmployeeTraining.objects.filter(status="En Cours").count(),
            'taux_canceled_course': taux_d_abandon_cours(),
            'page_title': "Tableau de Bord KPIs RH Généraux",
        }

    elif user.is_manager:  # si l'utilisateur est un manager
        department = user.department.name # n'affiche que les employees de son departement
        kpis = {
            'total_workforce': calculate_total_workforce(department),
            'retention_rate': calculate_retention_rate(one_year_ago, today, department),
            'turnover_rate': calculate_turnover_rate(one_year_ago, today, department),
            'average_seniority': calculate_average_seniority(),
            'total_payroll': calculate_total_payroll(department),
            'average_cost_per_employee': calculate_average_cost_per_employee(department),

        }

        context = {
            'active_link': 1,

            'departement': user.department.name,
            'objectif_atteint' : GoalDepartement.objects.filter(department=user.department).filter(status="COMPLETED").count(),
            'kpis': kpis,
            'employees_in_department': Employee.objects.filter(department=user.department).exclude(employee_id=user.employee_id),
            'pending_recommendation': RecommendedTraining.objects.filter(status='En attente').filter(employee__department=user.department).count(),
            'enrol_cours': EmployeeTraining.objects.filter(status="En Cours").filter(employee__department=user.department).count(),
            'taux_canceled_course': taux_d_abandon_cours(department=user.department),
            'rate_a_r': taux_de_recommandation_accepter(department=user.department),

        }
    else : # si c'est un employee simple -
        return redirect('dashboard:access_refuse')

    return render(request, 'index.html', context)


def login_(request):
    """
        Vue de connexion pour tous les utilisateurs, en fonction du role et du poste
        elle redirige vers la page ideal.
    """

    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            if user:

                if user.bloquer:
                    return redirect('dashboard:bloquer')

                login(request, user)

                if user.is_manager or user.is_hr: # si l'employé est un manager
                    return redirect('dashboard:home') # interface pour manager et HR

                elif user.is_admin : # si c'est un administrateur
                    return redirect('administration:home')

                else :
                    return redirect('employee:home')   # interface employee simple
            else:
                context = {
                    'form': form,
                    'error': 'Mot de passe ou email incorrect',
                }
                return render(request, 'login.html', context)
        else:
            context = {
                'form': form,
                'error': 'formulaire non valide',
            }
            return render(request, 'index.html', context)

    return render(request, 'login.html', {'form': form})


@login_required(login_url='dashboard:login')
def logout_(request):
    try:
        logout(request)
        return redirect('dashboard:login')
    except:
        return HttpResponse('Erreur de deconnexion')


def bloquer(request):
    return render(request, 'bloquer.html')


def taux_de_recommandation_accepter(department=None):
    trainings = RecommendedTraining.objects.all()
    if department:
        trainings = trainings.filter(employee__department=department)
    if trainings.count() == 0:
        return 0
    else :
        training_inscrit = trainings.filter(status='Inscrite')
        return training_inscrit.count() * 100 / trainings.count()


def taux_d_abandon_cours(department=None):
    trainings = EmployeeTraining.objects.filter(status="Annulé")
    if department:
        trainings = trainings.filter(employee__department=department)
    if trainings.count() == 0:
        return 0
    else:
        return trainings.count() * 100 / EmployeeTraining.objects.all().count()
