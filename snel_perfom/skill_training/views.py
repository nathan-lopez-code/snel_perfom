from datetime import date

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from pyexpat.errors import messages

from employee.models import Employee, Preferences
from .ia_logique import run_ai_recommendation_process

from .models import TrainingCourse, RecommendedTraining, EmployeeTraining, EmployeeSkill
from .utils import check_and_run_recommendations


@login_required
def ai_recommendations_list_view(request):
    """
    Vue pour afficher la liste détaillée des recommandations de formation de l'IA.
    Permet également le filtrage et la recherche. les recommandations de formation de l'IA s'affiche en fonction du role
    de l'utilisateur , tout pour un hr et conditinner par le departement pour un manager
    """
    preferences = Preferences.objects.get(pk=1) # frequence a la quel l'ia nous fera de recommandation
    if request.user.is_manager is False and request.user.is_hr is False:
        return redirect('dashboard:access_refuse')
    check_and_run_recommendations(preferences.frequence_recommendation) # fonction principale pour lancer la logique ia

    recommendations = RecommendedTraining.objects.exclude(status='Terminée')  # Récupérer toutes les recommandations faites par l'ia
    page_title = "Recommandations de Formation IA"
    user_department = request.user.department

    # filtrer en fonction du role
    if not request.user.is_hr:
        recommendations = recommendations.filter(employee__department=user_department)
        page_title = f"Recommandations de formation (Département: {user_department.name})"
        approuved_recommendation =  len(RecommendedTraining.objects.filter(status='Acceptée').filter(employee__department=user_department))
        pending_recommendation = len(RecommendedTraining.objects.filter(status='En attente').filter(employee__department=user_department))
        rejected_recommendation = len(RecommendedTraining.objects.filter(status='Refusée').filter(employee__department=user_department))
        enrolled_recommendation = len(RecommendedTraining.objects.filter(status='Inscrite').filter(employee__department=user_department))
        completed_recommendation = len(RecommendedTraining.objects.filter(status='Terminée').filter(employee__department=user_department))

    else:
        approuved_recommendation =  len(RecommendedTraining.objects.filter(status='Acceptée')),
        pending_recommendation = len(RecommendedTraining.objects.filter(status='En attente')),
        rejected_recommendation = len(RecommendedTraining.objects.filter(status='Refusée')),
        enrolled_recommendation = len(RecommendedTraining.objects.filter(status='Inscrite')),
        completed_recommendation = len(RecommendedTraining.objects.filter(status='Terminée')),

    status_filter = request.GET.get('status')
    if status_filter:
        recommendations = recommendations.filter(status=status_filter)

    search_query = request.GET.get('q')
    if search_query:
        recommendations = recommendations.filter(
            Q(employee__first_name__icontains=search_query) |
            Q(employee__last_name__icontains=search_query) |
            Q(course__title__icontains=search_query)
        )
    context = {
        'active_link':2,
        'recommendations': recommendations,
        'approuved_recommendation': approuved_recommendation,
        'pending_recommendation': pending_recommendation,
        'rejected_recommendation': rejected_recommendation,
        'enrolled_recommendation': enrolled_recommendation,
        'completed_recommendation': completed_recommendation,
        'page_title': page_title,
        'all_statuses': RecommendedTraining.STATUS_CHOICES, # Pour les options de filtre dans le template
        'current_status_filter': status_filter,
    }
    return render(request, 'recommandation_list.html', context)


@login_required
@require_POST
def update_recommendation_status(request, pk):
    """
    Vue pour mettre à jour le statut d'une recommandation de formation.
    """
    if request.user.is_manager is False and request.user.is_hr is False:
        return redirect('dashboard:access_refuse')

    recommendation = get_object_or_404(RecommendedTraining, pk=pk)

    action = request.POST.get('action')
    rejection_reason = request.POST.get('rejection_reason', '').strip() # Récupère le motif de refus

    if action == 'accept':
        message = 'Recommandation acceptée avec succès.'
        recommendation.accept_recommendation()
        try:
            # Tente de créer une nouvelle entrée EmployeeTraining ou de la récupérer si elle existe déjà
            employee_training, created = EmployeeTraining.objects.get_or_create(
                employee=recommendation.employee,
                course=recommendation.training_course,
                defaults={
                    'status': 'Inscrit',  # Le statut initial pour EmployeeTraining est 'PLANNED'
                    'enrollment_date': date.today(),
                    'recommended_by_ai': recommendation
                }
            )

            if created:
                message += " L'employé a été inscrit à la formation (statut 'Planifiée')."
                recommendation.mark_as_enrolled()
            else:
                message += f" L'employé était déjà inscrit à cette formation (statut actuel: {employee_training.get_status_display()})."
                recommendation.mark_as_enrolled()

        except Exception as e:
            message += f" Erreur lors de l'inscription via EmployeeTraining : {str(e)}"
            # Gérer l'erreur (annuler acceptation de reco, log, etc.)
            return JsonResponse({'message': message, 'status': 'error'})

    elif action == 'reject':
        if not rejection_reason:
            return JsonResponse({'success': False, 'message': 'Le motif de refus est obligatoire.'}, status=400)
        recommendation.reject_recommendation(rejection_reason)
        message = 'Recommandation refusée avec succès.'
    elif action == 'mark_enrolled':
        recommendation.mark_as_enrolled()
        message = 'Recommandation marquée comme inscrite.'
    else:
        return JsonResponse({'success': False, 'message': 'Action non valide.'}, status=400)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest': # Si c'est une requête AJAX
        return JsonResponse({'success': True, 'message': message})
    else:
        return redirect('dashboard:ai_recommendations_list') # Redirige vers la page de liste


@login_required(login_url='dashboard:login')
def formations_list_view(request):
    """
    Vue pour lister toutes les formations auxquelles les employés sont inscrits.
    Permet de filtrer par statut, recherche par nom d'employé/formation, et indique si recommandé par IA.
    """
    if request.user.is_manager is False and request.user.is_hr is False:
        return redirect('dashboard:access_refuse')

    all_employee_trainings = EmployeeTraining.objects.all().order_by('-enrollment_date')

    # Logique de filtrage (similaire à ai_recommendations_list_view)
    status_filter = request.GET.get('status')
    if status_filter:
        all_employee_trainings = all_employee_trainings.filter(status=status_filter)

    search_query = request.GET.get('q')
    if search_query:
        all_employee_trainings = all_employee_trainings.filter(
            Q(employee__first_name__icontains=search_query) |
            Q(employee__last_name__icontains=search_query) |
            Q(course__title__icontains=search_query)
        )

    all_employee_trainings = all_employee_trainings.select_related('employee', 'course', 'recommended_by_ai')
    department = None
    if request.user.is_manager:
        all_employee_trainings = all_employee_trainings.filter(employee__department=request.user.department)
        department = request.user.department.name

    STATUS_CHOICES = [
        ('Inscrit', 'Inscrit'),
        ('En Cours', 'En Cours'),
        ('Terminé', 'Terminé'),
        ('Annulé', 'Annulé'),
    ]
    context = {
        'active_link':3,
        'employee_trainings': all_employee_trainings,
        'page_title': "Suivi des Formations des Employés",
        'all_statuses': STATUS_CHOICES,
        'current_status_filter': status_filter,
        'department': department,

    }

    return render(request, 'formations_list.html', context)


@login_required
@require_POST
def update_employee_training_status(request, pk):
    """
    Vue pour mettre à jour le statut d'une inscription à une formation (EmployeeTraining).
    """

    if request.user.is_manager is False and request.user.is_hr is False:
        return redirect('dashboard:access_refuse')

    employee_training = get_object_or_404(EmployeeTraining, pk=pk)


    action = request.POST.get('action')
    message = "Statut mis à jour."

    if action == 'En Cours':
        employee_training.mark_in_progress()
        message = f"La formation pour {employee_training.employee.full_name} a été marquée 'En cours'."
    elif action == 'Terminé':
        employee_training.mark_attente_validation()
        message = f"La formation pour {employee_training.employee.full_name} a été marquée 'Terminé'."
    elif action == 'Annulé':
        employee_training.mark_cancelled()
        message = f"La formation pour {employee_training.employee.full_name} a été marquée 'Annulée'."
    else:
        return JsonResponse({'success': False, 'message': 'Action non valide.'}, status=400)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'message': message})
    else:
        return redirect('dashboards:formations_list')


@login_required
def manager_approval_list_view(request):
    """
    Affiche la liste des formations d'employés qui attendent l'approbation du manager.
    Les managers ne voient que les formations des employés de leur département.
    """
    if request.user.is_manager is False and request.user.is_hr is False:
        return redirect('dashboard:access_refuse')

    # Si le manager a un département défini, filtre par ce département
    if request.user.department:
        department_employees = Employee.objects.filter(department=request.user.department)
        pending_trainings = EmployeeTraining.objects.filter(
            employee__in=department_employees,
            status='Attente validation manager'
        ).order_by('-enrollment_date')
        page_title = f"Formations en attente d'approbation (Département : {request.user.department.name})"
    elif request.user.is_hr: # c'est HR
        pending_trainings = EmployeeTraining.objects.filter(
            status='Attente validation manager'
        ).order_by('-enrollment_date')
        page_title = "Toutes les formations en attente d'approbation"
    else:
        return redirect('dashboard:access_refuse')
    context = {
        'pending_trainings': pending_trainings,
        'page_title': page_title,
        'active_link' : 4
    }
    return render(request, 'manager_approval_list.html', context)


# ... (vos imports et fonctions is_manager, is_hr, is_employee existantes) ...

@login_required
def approve_training_and_evaluate_skills_view(request, employee_training_pk):
    """
    Permet au manager d'approuver une formation terminée par un employé
    et d'évaluer/mettre à jour les compétences associées.
    """
    if request.user.is_manager is False and request.user.is_hr is False:
        return redirect('dashboard:access_refuse')

    employee_training = get_object_or_404(EmployeeTraining, pk=employee_training_pk)

    # Vérifier si la formation est bien en attente d'approbation
    if employee_training.status != 'Attente validation manager':
        messages.error(request, "Cette formation n'est pas en attente d'approbation manager.")
        return redirect('Skill_Training:manager_approval_list')  # Redirige vers la liste des attentes

    # Vérifier que le manager est bien celui du département de l'employé
    if request.user.department:
        if employee_training.employee.department != request.user.department:
            if not request.user.is_hr:
                return redirect('Skill_Training:manager_approval_list')

    # Récupérer les compétences associées à ce cours
    skills_covered = employee_training.course.skills_covered.all()
    # Récupérer les compétences existantes de l'employé pour pré-remplir les niveaux actuels
    employee_current_skills = {
        es.skill: es for es in
        EmployeeSkill.objects.filter(employee=employee_training.employee, skill__in=skills_covered)
    }

    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Marquer la formation comme "Terminée"
                employee_training.mark_completed()

                # Si cette formation était liée à une recommandation IA, la marquer aussi comme terminée
                if employee_training.recommended_by_ai:
                    employee_training.recommended_by_ai.mark_as_completed()

                # Traiter l'évaluation des compétences
                for skill in skills_covered:
                    proficiency_level_key = f'skill_{skill.pk}_level'
                    # Assurez-vous que le champ existe dans le POST et est un entier valide
                    try:
                        new_proficiency_level = int(request.POST.get(proficiency_level_key))
                        if not (1 <= new_proficiency_level <= 5):  # Valider le niveau
                            raise ValueError("Niveau de maîtrise invalide. Doit être entre 1 et 5.")
                    except (ValueError, TypeError):
                        messages.warning(request,
                                         f"Niveau de maîtrise non fourni ou invalide pour la compétence '{skill.name}'. Elle n'a pas été mise à jour.")
                        continue  # Passe à la compétence suivante

                    employee_skill, created = EmployeeSkill.objects.get_or_create(
                        employee=employee_training.employee,
                        skill=skill,
                        defaults={
                            'proficiency_level': new_proficiency_level,
                            'last_assessed_date': date.today(),
                            'assessment_method': 'MANAGER_ASSESSMENT'
                        }
                    )

                    if not created:
                        # Si la compétence existait déjà, la mettre à jour
                        old_level = employee_skill.proficiency_level
                        if new_proficiency_level != old_level:
                            employee_skill.proficiency_level = new_proficiency_level
                            employee_skill.last_assessed_date = date.today()
                            employee_skill.assessment_method = 'MANAGER_ASSESSMENT'
                            employee_skill.save()

                employee_training.recommended_by_ai.mark_as_completed()
                return redirect(
                    'Skill_Training:manager_approval_list')

        except Exception as e:
            messages.error(request, f"Une erreur est survenue lors de l'approbation : {e}")
            # Renvoyer le formulaire avec les données existantes si possible
            context = {
                'employee_training': employee_training,
                'skills_covered': skills_covered,
                'employee_current_skills': employee_current_skills,
                'proficiency_choices': EmployeeSkill.PROFICIENCY_CHOICES,
            }
            return render(request, 'approve_training_and_evaluate_skills.html', context)

    # Pour la requête GET, afficher le formulaire d'évaluation
    context = {
        'employee_training': employee_training,
        'skills_covered': skills_covered,
        'employee_current_skills': employee_current_skills,
        'proficiency_choices': EmployeeSkill.PROFICIENCY_CHOICES,  # Pour afficher les options dans le template
    }
    return render(request, 'approve_training_and_evaluate_skills.html', context)