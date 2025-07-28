from datetime import date
from django.db import models
from employee.models import Employee


class SkillCategory(models.Model):
    """
    General categories for skills.
    """
    name = models.CharField(max_length=100, unique=True, verbose_name="Nom de la Catégorie")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de Création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de Dernière Mise à Jour")

    class Meta:
        verbose_name = "Catégorie de Compétence"
        verbose_name_plural = "Catégories de Compétences"
        ordering = ['name']

    def __str__(self):
        return self.name


class Skill(models.Model):
    """
    Specific skills required or possessed.
    """
    name = models.CharField(max_length=150, unique=True, verbose_name="Nom de la Compétence")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    category = models.ForeignKey(SkillCategory, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='skills', verbose_name="Catégorie")
    is_critical_for_snel = models.BooleanField(
        default=False, verbose_name="Critique pour la SNEL",
        help_text="Indique si cette compétence est essentielle pour les opérations ou la stratégie de la SNEL."
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de Création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de Dernière Mise à Jour")

    class Meta:
        verbose_name = "Compétence"
        verbose_name_plural = "Compétences"
        ordering = ['name']

    def __str__(self):
        return self.name


class EmployeeSkill(models.Model):
    """
    Records an employee's proficiency level for a specific skill.
    """
    PROFICIENCY_CHOICES = [
        (1, 'Débutant (Notions de base)'),
        (2, 'Connaissance de base (Peut exécuter avec supervision)'),
        (3, 'Intermédiaire (Peut exécuter de manière autonome)'),
        (4, 'Avancé (Peut exécuter et former d\'autres)'),
        (5, 'Expert (Leader dans le domaine, innove)'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='employee_skills',
                                 verbose_name="Employé")  # Changed to Employee
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='employee_mastery',
                              verbose_name="Compétence")
    proficiency_level = models.IntegerField(choices=PROFICIENCY_CHOICES, verbose_name="Niveau de Maîtrise")

    last_assessed_date = models.DateField(auto_now=True, verbose_name="Date de Dernière Évaluation")
    # 'assessed_by' is still a user
    assessed_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='skills_assessed', verbose_name="Évalué par")

    ASSESSMENT_METHOD_CHOICES = [
        ('SELF', 'Auto-évaluation'),
        ('MANAGER', 'Évaluation Manager'),
        ('PEER', 'Évaluation Pair'),
        ('HR', 'Évaluation RH'),
        ('AI', 'Évaluation IA'),
        ('TEST', 'Test de Compétences'),
    ]
    assessment_method = models.CharField(max_length=50, choices=ASSESSMENT_METHOD_CHOICES, blank=True, null=True,
                                         verbose_name="Méthode d'Évaluation")

    class Meta:
        verbose_name = "Compétence Employé"
        verbose_name_plural = "Compétences Employés"
        unique_together = ('employee', 'skill')
        ordering = ['employee__last_name', 'skill__name']

    def __str__(self):
        return f"{self.employee.full_name} - {self.skill.name} ({self.get_proficiency_level_display()})"


class TrainingCourse(models.Model):
    """
    Information about available training courses.
    """
    TRAINING_TYPE_CHOICES = [
        ('En Ligne', 'En Ligne'),
        ('En Présentiel', 'En Présentiel'),
        ('Mixte (En ligne et Présentiel)', 'Mixte (En ligne et Présentiel)'),
    ]

    title = models.CharField(max_length=200, verbose_name="Titre de la Formation")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    provider = models.CharField(max_length=100, blank=True, null=True, verbose_name="Fournisseur (Interne/Externe)")
    duration_hours = models.IntegerField(null=True, blank=True, verbose_name="Durée (Heures)")
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Coût")

    skills_covered = models.ManyToManyField(Skill, related_name='courses', verbose_name="Compétences Couvertes")

    training_type = models.CharField(max_length=60, choices=TRAINING_TYPE_CHOICES, default='IN_PERSON',
                                     verbose_name="Type de Formation")
    url_link = models.URLField(max_length=200, blank=True, null=True, verbose_name="Lien (si en ligne)")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de Création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de Dernière Mise à Jour")

    class Meta:
        verbose_name = "Formation"
        verbose_name_plural = "Formations"
        ordering = ['title']

    def __str__(self):
        return self.title


class SkillGapAnalysis(models.Model):
    """
    Enregistre le resulte de lacune decouvert par l'ia dans l'analyse de competences
    """
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='skill_gap_analyses',
                                 verbose_name="Employé")  # Changed to Employee
    analysis_date = models.DateTimeField(auto_now_add=True, verbose_name="Date de l'Analyse")

    identified_gaps = models.ManyToManyField(Skill, related_name='gaps_identified_in_analysis',
                                             verbose_name="Lacunes Identifiées")

    recommendation_reason = models.TextField(verbose_name="Raison de la Recommandation (IA)")

    is_actioned = models.BooleanField(default=False, verbose_name="Action Prise Suite à l'Analyse")
    action_description = models.TextField(blank=True, null=True, verbose_name="Description de l'Action Prise")

    class Meta:
        verbose_name = "Analyse des Lacunes en Compétences (IA)"
        verbose_name_plural = "Analyses des Lacunes en Compétences (IA)"
        ordering = ['-analysis_date', 'employee__last_name']

    def __str__(self):
        return f"Analyse des lacunes pour {self.employee.full_name} le {self.analysis_date.strftime('%Y-%m-%d %H:%M')}"


class RecommendedTraining(models.Model):

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='recommended_trainings',
                                 verbose_name="Employé")
    training_course = models.ForeignKey(TrainingCourse, on_delete=models.CASCADE,
                                        related_name='ai_recommendations', verbose_name="Formation Recommandée")

    recommendation_date = models.DateTimeField(auto_now_add=True, verbose_name="Date de Recommandation")

    reasoning = models.TextField(null=True, blank=True, verbose_name="Raisonnement de l'IA")

    confidence_score = models.FloatField(
        null=True, blank=True,
        help_text="Score de confiance de l'IA pour cette recommandation (0-1, 1 étant le plus confiant).",
        verbose_name="Score de Confiance IA"
    )

    is_accepted = models.BooleanField(default=False, verbose_name="Accepté par l'Employé/Manager")
    accepted_date = models.DateField(null=True, blank=True, verbose_name="Date d'Acceptation")

    # Ajout d'un champ pour le statut détaillé (si ce n'est pas déjà le cas)
    STATUS_CHOICES = [
        ('En attente', 'En attente'),
        ('Refusée', 'Refusée'),
        ('Inscrite', 'Inscrite'),
        ('Terminée', 'Terminée'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='En attente',
                              verbose_name="Statut de la Recommandation")

    rejection_reason = models.TextField(blank=True, null=True, verbose_name="Motif de Refus")

    originating_gap_analysis = models.ForeignKey(SkillGapAnalysis, on_delete=models.SET_NULL,
                                                 null=True, blank=True,
                                                 related_name='related_recommendations',
                                                 verbose_name="Issue de l'Analyse de Lacune")

    class Meta:
        verbose_name = "Recommandation de Formation (IA)"
        verbose_name_plural = "Recommandations de Formations (IA)"
        unique_together = ('employee', 'training_course', 'recommendation_date')
        ordering = ['-recommendation_date', 'employee__last_name']

    def __str__(self):
        return f"Recommandation pour {self.employee.full_name}: {self.training_course.title}"


    def accept_recommendation(self):
        self.is_accepted = True
        self.accepted_date = date.today()
        self.status = 'Acceptée'
        self.save()

    def reject_recommendation(self, reason=None):
        self.is_accepted = False
        self.accepted_date = None
        self.status = 'Refusée'
        self.rejection_reason = reason
        self.save()

    # Méthode pour marquer comme inscrite (si un flux d'inscription existe)
    def mark_as_enrolled(self):
        self.status = 'Inscrite'
        self.save()

    # Méthode pour marquer comme complétée (après la fin de la formation)
    def mark_as_completed(self):
        self.status = 'Terminée'
        self.save()


class EmployeeTraining(models.Model):
    """
    Records an employee's participation in a training course.
    """
    STATUS_CHOICES = [
        ('Inscrit', 'Inscrit'),
        ('En Cours', 'En Cours'),
        ('Attente validation manager', 'Attente validation manager'),
        ('Terminé', 'Terminé'),
        ('Annulé', 'Annulé'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='trainings_taken',
                                 verbose_name="Employé")  # Changed to Employee
    course = models.ForeignKey(TrainingCourse, on_delete=models.CASCADE, related_name='participants',
                               verbose_name="Formation")

    enrollment_date = models.DateField(verbose_name="Date d'Inscription", blank=True, null=True)
    completion_date = models.DateField(null=True, blank=True, verbose_name="Date de Complétion")
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default='Inscrit', verbose_name="Statut")

    score = models.IntegerField(null=True, blank=True, verbose_name="Score Obtenu (si applicable)")
    feedback_on_course = models.TextField(blank=True, null=True, verbose_name="Feedback sur la Formation")

    recommended_by_ai = models.OneToOneField(
        'RecommendedTraining',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='related_employee_training',
        verbose_name="Recommandée par l'IA"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date d'Enregistrement")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de Dernière Mise à Jour")

    class Meta:
        verbose_name = "Participation Formation"
        verbose_name_plural = "Participations Formations"
        unique_together = ('employee', 'course', 'enrollment_date')
        ordering = ['-enrollment_date', 'employee__last_name']

    def __str__(self):
        return f"{self.employee.full_name} - {self.course.title} ({self.get_status_display()})"

    def mark_in_progress(self):
        self.status = 'En Cours'
        if not self.enrollment_date:  # Si la date de début n'est pas déjà définie
            self.enrollment_date = date.today()
        self.save()

    def mark_attente_validation(self):
        self.status = 'Attente validation manager'
        if not self.enrollment_date:
            self.enrollment_date = self.enrollment_date  # Ou date.today()
        if not self.completion_date:
            self.completion_date = date.today()
        self.save()
        return self

    def mark_completed(self):
        self.status = 'Terminé'
        if not self.completion_date:  # Si la date de fin n'est pas déjà définie
            self.completion_date = date.today()
        if not self.enrollment_date:  # S'assurer que start_date est défini si complété
            self.enrollment_date = self.enrollment_date  # Ou date.today()
        self.save()

    def mark_cancelled(self):
        self.status = 'Annulé'
        self.save()

