from django.contrib.auth.decorators import login_required
from django.core.checks import messages
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from employee.models import Employee
from skill_training.models import TrainingCourse, EmployeeTraining, EmployeeSkill


@login_required(login_url='dashboard:login')
def list_course(request):
    if request.user.is_hr is False:
        return redirect('dashboard:access_refuse')
    else:
        context = {
            'all_courses': TrainingCourse.objects.all()
        }
        return render(request, 'creation_formation.html', context)


@login_required(login_url='dashboard:login')
def create_course(request):

    if request.user.is_hr is False:
        return redirect('dashboard:access_refuse')
    else:
        context = {}
        return render(request, 'creation_formation.html', context)


@login_required(login_url='dashboard:login')
def edit_course(request, course_id):
    if request.user.is_hr is False:
        return redirect('dashboard:access_refuse')
    else:
        context = {}
        return render(request, 'creation_formation.html', context)


@login_required(login_url='dashboard:login')
def detail_course(request, course_id):
    course = get_object_or_404(TrainingCourse, pk=course_id)

    total_participants = EmployeeTraining.objects.filter(course=course).values('employee').distinct().count()

    participants_list = EmployeeTraining.objects.filter(course=course).select_related('employee').values(
        'employee').distinct()

    employee_ids = [item['employee'] for item in participants_list]
    actual_participants = Employee.objects.filter(pk__in=employee_ids).order_by('first_name', 'last_name')

    context = {
        'course': course,
        'total_participants': total_participants,
        'participants_list': actual_participants,  # List of Employee objects
    }
    return render(request, 'course_details.html', context)



@login_required(login_url='dashboard:login')
def mark_course_inscrit(request, course_id):
    training = get_object_or_404(EmployeeTraining, pk=course_id)
    training.mark_in_progress()
    return redirect('employee:home')


@login_required(login_url='dashboard:login')
def mark_attente_validation(request, course_id):
    training = get_object_or_404(EmployeeTraining, pk=course_id)
    training.mark_attente_validation()
    return redirect('employee:home')


@login_required(login_url='dashboard:login')
def mark_course_completed(request, course_id):
    """
    Marque une participation à une formation comme 'Terminée' et ajoute/met à jour
    les compétences associées au profil de l'employé.

    Args:
        request (HttpRequest): L'objet requête Django.
        course_id (int): La clé primaire de l'instance EmployeeTraining à marquer comme terminée.
    """
    employee_training = get_object_or_404(EmployeeTraining, pk=course_id)

    # Assure-toi que seuls les requêtes POST sont acceptées pour cette action sensible
    if request.method == 'POST':
        # On peut récupérer un score optionnel via le formulaire si nécessaire
        score_str = request.POST.get('score')
        score = int(score_str) if score_str and score_str.isdigit() else None

        try:
            with transaction.atomic():  # Démarre une transaction atomique

                # 1. Marquer la formation comme terminée dans EmployeeTraining
                employee_training.mark_completed()  # Utilise la méthode que tu as définie dans le modèle
                employee_training.score = score
                employee_training.save()

                # Si cette formation était liée à une recommandation IA, la marquer aussi comme terminée
                if employee_training.recommended_by_ai:
                    employee_training.recommended_by_ai.mark_as_completed()
                    messages.success(request,
                                     f"La recommandation pour '{employee_training.course.title}' a également été marquée comme terminée.")

                # 2. Récupérer l'employé et les compétences couvertes par le cours
                employee = employee_training.employee
                skills_covered_by_course = employee_training.course.skills_covered.all()

                # 3. Ajouter/Mettre à jour les compétences de l'employé
                for skill in skills_covered_by_course:
                    # Tente de récupérer la compétence de l'employé existante
                    employee_skill, created = EmployeeSkill.objects.get_or_create(
                        employee=employee,
                        skill=skill,
                        defaults={
                            'proficiency_level': 1,  # Niveau initial si la compétence est nouvelle
                            'last_assessed_date': date.today(),
                            'assessment_method': 'TRAINING'  # Ou 'COURSE_COMPLETION'
                        }
                    )

                    if not created:
                        # Si la compétence existe déjà, incrémenter son niveau de maîtrise
                        # ou la mettre à jour si nécessaire. Ici, on l'incrémente d'un niveau,
                        # mais sans dépasser le niveau Expert (5).
                        old_level = employee_skill.proficiency_level
                        new_level = min(old_level + 1, 5)  # Incrémente d'un niveau, max 5

                        if new_level > old_level:
                            employee_skill.proficiency_level = new_level
                            employee_skill.last_assessed_date = date.today()
                            employee_skill.assessment_method = 'TRAINING'  # Ou 'COURSE_COMPLETION'
                            employee_skill.save()
                            messages.info(request,
                                          f"Niveau de maîtrise de '{skill.name}' mis à jour pour {employee.full_name} : de {old_level} à {new_level}.")
                        else:
                            messages.info(request,
                                          f"Niveau de maîtrise de '{skill.name}' pour {employee.full_name} est déjà au maximum (Expert).")
                    else:
                        messages.success(request,
                                         f"Compétence '{skill.name}' ajoutée à {employee.full_name} avec un niveau Débutant (1).")

                messages.success(request,
                                 f"Formation '{employee_training.course.title}' marquée comme terminée pour {employee.full_name}.")

                # Redirection vers le profil de l'employé
                return redirect('employee:user_profile', pk=employee.pk)

        except Exception as e:
            messages.error(request, f"Une erreur est survenue lors de la finalisation de la formation : {e}")
            # Redirection vers la même page ou une page d'erreur
            return redirect('skilltraining:course_detail',
                            pk=employee_training.course.pk)  # Ou une autre page pertinente

    # Si ce n'est pas une requête POST, redirige ou affiche une page d'erreur
    messages.warning(request,
                     "Requête non valide. Veuillez utiliser la méthode POST pour marquer une formation comme terminée.")
    return redirect('skilltraining:course_detail', pk=employee_training.course.pk)  # Redirige vers la page du cours