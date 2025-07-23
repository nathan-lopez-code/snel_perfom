from datetime import date
from django.db.models import Count, Avg, Sum, F, ExpressionWrapper, fields
from employee.models import Employee, Department  # Assurez-vous d'importer vos modèles
from skill_training.crack import all_employees


# --- Fonctions de Calcul des KPIs RH ---

def calculate_total_workforce(department):
    """
    Calcule le nombre total d'employés actifs.
    """
    if department:
        return len(Employee.objects.filter(department__name=department).filter(employee_status='ACT'))
    return Employee.objects.filter(employee_status='ACT').count()


def calculate_retention_rate(start_date, end_date, department):
    """
    Calcule le taux de rétention sur une période donnée.

    Arguments:
        start_date (date): Date de début de la période d'analyse.
        end_date (date): Date de fin de la période d'analyse.

    Le taux de rétention est calculé comme :
    (Nombre d'employés présents au début ET à la fin de la période) / (Nombre d'employés présents au début de la période) * 100
    """
    # Employés actifs au début de la période

    employees_at_start = Employee.objects.filter(
        hire_date__lte=start_date,
        employee_status='ACT'  # Considérer seulement les actifs au début
    )
    # Employés actifs à la fin de la période ET présents au début
    employees_retained = Employee.objects.filter(
        hire_date__lte=start_date,  # Étaient là au début
        employee_status='ACT',  # Sont encore actifs
    )

    if department:
        employees_at_start.filter(department__name=department)
        employees_retained.filter(department__name=department)

    if employees_at_start.count() == 0:
        return 0.0  # Éviter la division par zéro

    return (employees_retained.count() / employees_at_start.count()) * 100


def calculate_turnover_rate(start_date, end_date, department):
    """
    Calcule le taux de rotation (turnover) sur une période donnée.

    Arguments:
        start_date (date): Date de début de la période d'analyse.
        end_date (date): Date de fin de la période d'analyse.

    Le taux de rotation est calculé comme :
    (Nombre d'employés ayant quitté sur la période) / (Nombre moyen d'employés sur la période) * 100

    Pour simplifier, nous utilisons ici le nombre d'employés actifs au début de la période
    comme proxy pour le nombre moyen, ou vous pouvez le calculer plus précisément.

    Nécessite une logique pour identifier les "quittants" (employés dont le statut a changé de ACTIF à un statut de départ).
    Ceci est une version simplifiée. Pour une précision parfaite, le modèle Employee
    devrait avoir une `termination_date` ou un `date_of_status_change` pour les statuts de départ.
    """
    # Nombre d'employés au début de la période (proxy pour moyenne)
    employees_at_start = Employee.objects.filter(
        hire_date__lte=start_date,
        employee_status='ACT'
    )

    employees_who_left = Employee.objects.filter(
        employee_status__in=['RES', 'LIC', 'RET'],  # Statuts indiquant un départ
        updated_at__date__range=(start_date, end_date)  # Supposons que updated_at reflète le départ
    )

    if department:
        employees_at_start.filter(department__name=department)
        employees_who_left.filter(department__name=department)

    if employees_at_start.count() == 0:
        return 0.0



    return (employees_who_left.count() / employees_at_start.count()) * 100


def calculate_average_seniority():
    """
    Calcule l'ancienneté moyenne des employés actifs en années.
    """
    today = date.today()

    # Calculer la différence en jours entre aujourd'hui et la date d'embauche
    # Convertir la différence en années (approx.)
    seniority_in_days = Employee.objects.filter(employee_status='ACT').annotate(
        seniority_days=ExpressionWrapper(today - F('hire_date'), output_field=fields.DurationField())
    ).aggregate(avg_seniority_days=Avg('seniority_days'))['avg_seniority_days']

    if seniority_in_days:
        # Convertir les jours en années (365.25 pour tenir compte des années bissextiles)
        return seniority_in_days.days / 365.25
    return 0.0


def calculate_total_payroll(department):
    """
    Calcule la masse salariale totale mensuelle des employés actifs.
    """
    all_employees = Employee.objects.filter(employee_status='ACT')
    if department:
        all_employees.filter(department__name=department)
    total_salary = all_employees.aggregate(total_sum=Sum('salary'))['total_sum']
    return total_salary if total_salary is not None else 0.0


def calculate_average_cost_per_employee(department):
    """
    Calcule le coût moyen mensuel par employé actif (basé sur le salaire).
    Inclure les avantages sociaux nécessiterait un champ `benefits_cost` sur le modèle Employee.
    """
    if department:
        total_payroll = calculate_total_payroll(department)
        total_active_employees = calculate_total_workforce(department)
    else:
        total_payroll = calculate_total_payroll(department=None)
        total_active_employees = calculate_total_workforce(department=None)

    if total_active_employees == 0:
        return 0.0
    return total_payroll / total_active_employees


def get_workforce_distribution_by_department():
    """
    Retourne la répartition des effectifs actifs par département.
    """
    return Employee.objects.filter(employee_status='ACT').values('department__name').annotate(
        count=Count('id')).order_by('-count')


def get_workforce_distribution_by_gender():
    """
    Retourne la répartition des effectifs actifs par genre.
    """
    return Employee.objects.filter(employee_status='ACT').values('gender').annotate(count=Count('id')).order_by(
        '-count')


def get_workforce_distribution_by_age_range(department):
    """
    Retourne la répartition des effectifs actifs par tranche d'âge.

    Ceci est une implémentation simplifiée avec des tranches d'âge fixes.
    Vous pouvez la personnaliser.
    """
    today = date.today()
    employees = Employee.objects.filter(employee_status='ACT', date_of_birth__isnull=False)
    if department:
        employees.filter(department__name=department)
    age_ranges = {
        'Moins de 25 ans': 0,
        '25-34 ans': 0,
        '35-44 ans': 0,
        '45-54 ans': 0,
        '55 ans et plus': 0,
    }

    for emp in employees:
        age = today.year - emp.date_of_birth.year - \
              ((today.month, today.day) < (emp.date_of_birth.month, emp.date_of_birth.day))

        if age < 25:
            age_ranges['Moins de 25 ans'] += 1
        elif 25 <= age <= 34:
            age_ranges['25-34 ans'] += 1
        elif 35 <= age <= 44:
            age_ranges['35-44 ans'] += 1
        elif 45 <= age <= 54:
            age_ranges['45-54 ans'] += 1
        else:
            age_ranges['55 ans et plus'] += 1

    # Convertir en liste de dictionnaires pour une utilisation facile dans les templates/API
    return [{'range': k, 'count': v} for k, v in age_ranges.items()]

def get_workforce_distribution_by_contract_type():
    """
    Retourne la répartition des effectifs actifs par type de contrat.
    """
    return Employee.objects.filter(employee_status='ACT').values('contract_type').annotate(count=Count('id')).order_by(
        '-count')
