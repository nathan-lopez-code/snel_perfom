from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Employee


@admin.register(Employee)
class EmployeeAdmin(UserAdmin):
    # Les champs à afficher dans la liste (vue générale de tous les employés)
    list_display = ('email', 'first_name', 'last_name', 'employee_id', 'is_staff', 'is_manager', 'is_hr')

    # Les champs par lesquels on peut filtrer les employés
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'is_manager', 'is_hr', 'department', 'position',
                   'contract_type', 'employee_status')

    # Les champs par lesquels on peut rechercher les employés
    search_fields = ('email', 'first_name', 'last_name', 'employee_id')

    # Groupement des champs dans les formulaires de création et de modification
    fieldsets = (
        ('Informations d\'Authentification', {
            'fields': ('email', 'password')
        }),
        ('Informations Personnelles', {
            'fields': ('first_name', 'last_name', 'gender', 'date_of_birth', 'profile_picture', 'phone_number',
                       'address')
        }),
        ('Informations d\'Emploi', {
            'fields': ('employee_id', 'hire_date', 'department', 'position', 'manager', 'contract_type',
                       'employee_status', 'salary', 'emergency_contact_name', 'emergency_contact_phone')
        }),
        ('Permissions et Statut', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'is_manager', 'is_hr', 'is_admin', 'groups',
                       'user_permissions')
        }),
        ('Dates Importantes', {
            'fields': ('last_login', 'date_joined')
        }),
    )

    # Pour les formulaires de création d'utilisateur, on retire des champs non nécessaires
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password', 'first_name', 'last_name', 'gender', 'date_of_birth', 'hire_date',
                       'department', 'position', 'bloquer'),
        }),
    )

    # Rendre les champs read-only pour éviter les modifications accidentelles
    readonly_fields = ('employee_id', 'last_login', 'date_joined')

    # La ligne ci-dessous est cruciale pour le tri.
    # UserAdmin utilise 'username' par défaut pour l'ordering,
    # mais vous devez le remplacer par un champ qui existe, comme 'email'.
    # Notez que j'ai commenté la ligne précédente qui était la cause de l'erreur.
    # ordering = ('username',)  # <-- Ceci est la ligne qui causait l'erreur
    ordering = ('email',)