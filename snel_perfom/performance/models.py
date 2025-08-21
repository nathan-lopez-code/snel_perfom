from django.db import models
from employee.models import Employee, Department


class PerformanceMetric(models.Model):
    """
    Defines generic performance indicators used across SNEL.
    """
    name = models.CharField(max_length=100, unique=True, verbose_name="Nom de la Métrique")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    unit = models.CharField(
        max_length=50, blank=True, null=True,
        help_text="Unité de mesure (e.g., %, Jours, Nombre, Échelle de Likert)",
        verbose_name="Unité"
    )
    is_quantitative = models.BooleanField(
        default=True, verbose_name="Est Quantitative",
        help_text="Cochez si la métrique est mesurable par un nombre."
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de Création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de Dernière Mise à Jour")

    class Meta:
        verbose_name = "Métrique de Performance"
        verbose_name_plural = "Métrique de Performance"
        ordering = ['name']

    def __str__(self):
        return self.name


class Goal(models.Model):
    """
    Represents a performance goal assigned to an employee.
    """
    STATUS_CHOICES = [
        ('NOT_STARTED', 'Non Démarré'),
        ('IN_PROGRESS', 'En Cours'),
        ('COMPLETED', 'Complété'),
        ('OVERDUE', 'En Retard'),
        ('CANCELED', 'Annulé'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='goals',
                                 verbose_name="Employé Cible")  # Changed from CustomUser to Employee
    title = models.CharField(max_length=200, verbose_name="Titre de l'Objectif")
    description = models.TextField(blank=True, null=True, verbose_name="Description Détaillée")
    start_date = models.DateField(verbose_name="Date de Début")
    end_date = models.DateField(verbose_name="Date de Fin Cible")

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NOT_STARTED',
                              verbose_name="Statut de l'Objectif")

    target_value = models.FloatField(null=True, blank=True, verbose_name="Valeur Cible")
    current_value = models.FloatField(null=True, blank=True, verbose_name="Valeur Actuelle")
    metric = models.ForeignKey(PerformanceMetric, on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='goals', verbose_name="Métrique Associée")

    # The 'set_by' is still a user who logs in and sets the goal
    set_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='goals_set', verbose_name="Défini par")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de Création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de Dernière Mise à Jour")

    class Meta:
        verbose_name = "Objectif"
        verbose_name_plural = "Objectifs"
        ordering = ['-end_date', 'employee__last_name']
        unique_together = ('employee', 'title', 'start_date')

    def __str__(self):
        return f"Objectif pour {self.employee.full_name}: {self.title}"


class GoalDepartement(models.Model):
    """
    Represents a performance goal assigned to an employee.
    """
    STATUS_CHOICES = [
        ('NOT_STARTED', 'Non Démarré'),
        ('IN_PROGRESS', 'En Cours'),
        ('COMPLETED', 'Complété'),
        ('OVERDUE', 'En Retard'),
        ('CANCELED', 'Annulé'),
    ]

    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='goals_department',
                                 verbose_name="departement Cible")  # Changed from CustomUser to Employee
    title = models.CharField(max_length=200, verbose_name="Titre de l'Objectif")
    description = models.TextField(blank=True, null=True, verbose_name="Description Détaillée")
    start_date = models.DateField(verbose_name="Date de Début")
    end_date = models.DateField(verbose_name="Date de Fin Cible")

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NOT_STARTED',
                              verbose_name="Statut de l'Objectif")

    target_value = models.FloatField(null=True, blank=True, verbose_name="Valeur Cible")
    current_value = models.FloatField(null=True, blank=True, verbose_name="Valeur Actuelle")

    # The 'set_by' is still a user who logs in and sets the goal
    set_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='goaldepartment_set', verbose_name="Défini par")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de Création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de Dernière Mise à Jour")

    class Meta:
        verbose_name = "Objectif"
        verbose_name_plural = "Objectifs"
        ordering = ['-end_date', ]

    def __str__(self):
        return f"Objectif du departement {self.departement.name}: {self.title}"

class PerformanceReview(models.Model):
    """
    Represents a formal performance evaluation of an employee.
    """
    SCORE_CHOICES = [
        (1, 'Insuffisant (Ne répond pas aux attentes)'),
        (2, 'À Améliorer (Répond parfois aux attentes)'),
        (3, 'Satisfaisant (Répond aux attentes)'),
        (4, 'Bon (Dépasse les attentes)'),
        (5, 'Excellent (Dépasse largement les attentes)'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='performance_reviews',
                                 verbose_name="Employé Évalué")  # Changed from CustomUser to Employee
    # Reviewer is still a user who logs in to conduct the review
    reviewer = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='reviews_conducted', verbose_name="Évaluateur")

    review_date = models.DateField(verbose_name="Date de l'Évaluation")
    overall_score = models.IntegerField(choices=SCORE_CHOICES, verbose_name="Score Global")
    comments = models.TextField(verbose_name="Commentaires Généraux")
    next_steps = models.TextField(blank=True, null=True, verbose_name="Prochaines Étapes et Plan de Développement")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de Création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de Dernière Mise à Jour")

    class Meta:
        verbose_name = "Évaluation de Performance"
        verbose_name_plural = "Évaluations de Performance"
        unique_together = ('employee', 'review_date')
        ordering = ['-review_date', 'employee__last_name']

    def __str__(self):
        return f"Évaluation de {self.employee.full_name} le {self.review_date}"


class Feedback(models.Model):
    """
    Records continuous feedback (positive or constructive) between employees.
    """
    FEEDBACK_TYPE_CHOICES = [
        ('POSITIVE', 'Positif'),
        ('CONSTRUCTIVE', 'Constructif'),
        ('360', '360 Degrés (issu d\'une campagne formelle)'),
    ]

    # Giver and Receiver are still users (system users)
    giver = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='feedback_given',
                              verbose_name="Donné par")
    receiver = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='feedback_received',
                                 verbose_name="Reçu par")  # Changed to Employee for the recipient

    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_TYPE_CHOICES, verbose_name="Type de Feedback")
    content = models.TextField(verbose_name="Contenu du Feedback")

    related_goal = models.ForeignKey(Goal, on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='feedback_entries', verbose_name="Objectif Lié")

    date_given = models.DateTimeField(auto_now_add=True, verbose_name="Date du Feedback")

    class Meta:
        verbose_name = "Feedback"
        verbose_name_plural = "Feedbacks"
        ordering = ['-date_given']

    def __str__(self):
        return f"Feedback de {self.giver.full_name} à {self.receiver.full_name} ({self.get_feedback_type_display()})"