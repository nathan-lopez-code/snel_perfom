from django.contrib.auth.base_user import BaseUserManager
from django.urls import reverse
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from datetime import date


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nom du Département")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de Création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de Dernière Mise à Jour")

    class Meta:
        verbose_name = "Département"
        verbose_name_plural = "Départements"
        ordering = ['name']

    def __str__(self):
        return self.name


class Position(models.Model):
    title = models.CharField(max_length=100, unique=True, verbose_name="Titre du Poste")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='positions', verbose_name="Département Associé")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de Création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de Dernière Mise à Jour")

    class Meta:
        verbose_name = "Poste"
        verbose_name_plural = "Postes"
        ordering = ['title']

    def __str__(self):
        return self.title


class CustomUserManager(BaseUserManager):
    """
    Gestionnaire de modèle utilisateur personnalisé où l'email est l'identifiant unique
    pour l'authentification au lieu des noms d'utilisateur.
    """

    def create_user(self, email, password=None, **extra_fields):
        """
        Crée et enregistre un utilisateur avec l'email et le mot de passe donnés.
        """
        if not email:
            raise ValueError("L'adresse e-mail doit être définie")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Crée et enregistre un superutilisateur avec l'email et le mot de passe donnés.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)  # S'assurer que le superutilisateur est actif

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Le superutilisateur doit avoir is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Le superutilisateur doit avoir is_superuser=True.")

        # Appel de la méthode create_user que nous venons de définir
        return self.create_user(email, password, **extra_fields)


class Employee(AbstractUser):
    """
    Represents a person employed by SNEL, holding all HR-related data.
    Not every employee needs to be a system user.
    """


    # constant

    GENDER_CHOICES = [
        ('M', 'Masculin'),
        ('F', 'Féminin'),
        ('O', 'Autre'),
    ]
    CONTRACT_TYPE_CHOICES = [
        ('CDI', 'Contrat à Durée Indéterminée'),
        ('CDD', 'Contrat à Durée Déterminée'),
        ('INT', 'Intérim'),
        ('STA', 'Stage'),
        ('AUT', 'Autre'),
    ]
    EMPLOYEE_STATUS_CHOICES = [
        ('ACT', 'Actif'),
        ('CON', 'En Congé'),
        ('SUS', 'Suspendu'),
        ('RES', 'Démissionnaire'),
        ('LIC', 'Licencié'),
        ('RET', 'Retraité'),
    ]

    # authentification informations
    email = models.EmailField(unique=True, verbose_name="Adresse E-mail de Connexion")
    username = None

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    # snel id employee
    employee_id = models.CharField(
        max_length=50, unique=True, blank=True,
        verbose_name="Numéro Matricule",
        help_text="Numéro d'identification unique de l'employé à la SNEL (généré automatiquement)."
    )


    # post management

    is_hr = models.BooleanField(
        default=False, verbose_name="Est RH",
        help_text="Indique si l'utilisateur a des privilèges du département des ressources humaines."
    )
    is_manager = models.BooleanField(
        default=False, verbose_name="Est Manager",
        help_text="Indique si l'utilisateur est un manager avec une équipe à gérer."
    )


    # Personal Information
    date_of_birth = models.DateField(null=True, blank=True, verbose_name="Date de Naissance")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True, verbose_name="Genre")
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="Numéro de Téléphone")
    address = models.TextField(blank=True, null=True, verbose_name="Adresse Résidentielle")
    profile_picture = models.ImageField(upload_to='media/employee_pics/', null=True, blank=True,
                                        verbose_name="Photo de Profil")

    # Employment Information
    hire_date = models.DateField(verbose_name="Date d'Embauche", null=True)  # Used for year of engagement
    contract_type = models.CharField(max_length=3, choices=CONTRACT_TYPE_CHOICES, default='CDI',
                                     verbose_name="Type de Contrat")
    employee_status = models.CharField(max_length=3, choices=EMPLOYEE_STATUS_CHOICES, default='ACT',
                                       verbose_name="Statut de l'Employé")
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                 verbose_name="Salaire Mensuel Brut")

    emergency_contact_name = models.CharField(max_length=100, blank=True, null=True,
                                              verbose_name="Contact d'Urgence (Nom)")
    emergency_contact_phone = models.CharField(max_length=20, blank=True, null=True,
                                               verbose_name="Contact d'Urgence (Téléphone)")

    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='department_employees', verbose_name="Département")
    position = models.ForeignKey(Position, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='position_employees', verbose_name="Poste")
    manager = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='managed_employees', verbose_name="Manager Direct")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de Création Fiche")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date Dernière Maj Fiche")



    class Meta:
        verbose_name = "Employé SNEL"
        verbose_name_plural = "Employés SNEL"
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.employee_id})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def current_age(self):
        if self.date_of_birth:
            today = date.today()
            return today.year - self.date_of_birth.year - \
                ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        return None


    def is_simple_employee(self):
        if not self.is_manager and not self.is_hr:
            return True
        return False

    def get_absolute_url(self):
        """
        Retourne l'URL canonique pour l'objet CustomUser, redirigeant vers
        sa page de profil spécifique.
        """
        # Utilise 'dashboards:user_profile' avec l'ID (pk) de l'utilisateur
        return reverse('employee:user_profile', kwargs={'pk': self.pk})


    def save(self, *args, **kwargs):

        if not self.employee_id:

            super().save(*args, **kwargs)  # Call the "real" save() method.

            first_letters = self.first_name[:2].upper() if self.first_name else "XX"
            last_letters = self.last_name[:2].upper() if self.last_name else "YY"

            hire_year_short = str(self.hire_date.year)[-2:] if self.hire_date else str(date.today().year)[-2:]

            sequential_id = str(self.pk).zfill(3)

            self.employee_id = f"{first_letters}-{last_letters}-{hire_year_short}-{sequential_id}"
            super().save(update_fields=['employee_id'])
        else:
            # If employee_id already exists, just perform a regular save
            super().save(*args, **kwargs)



class Preferences(models.Model):

    FREQUENCE_CHOICES = (
        ('hebdomadaire', 'hedomadaire'),
        ('mensuel', 'mensuel'),
        ('Quotidient', 'Quotidient'),
    )

    frequence_recommendation = models.CharField(max_length=40, help_text="Frequence d'actulisation de recommendations IA", choices=FREQUENCE_CHOICES, default='journaliere')
