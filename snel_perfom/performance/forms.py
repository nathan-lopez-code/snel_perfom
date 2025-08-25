from django import forms

from employee.models import Employee
from .models import Goal, PerformanceReview, ElementEvaluation


class GoalCreateForm(forms.ModelForm):
    """
    Formulaire pour la création complète d'un objectif.
    """

    class Meta:
        model = Goal
        fields = ['employee', 'title', 'description', 'start_date', 'end_date', 'target_value', 'metric']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'target_value': forms.NumberInput(attrs={'class': 'form-control'}),
            'metric': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        # Récupère l'utilisateur passé depuis la vue
        manager = kwargs.pop('manager', None)
        super().__init__(*args, **kwargs)

        # Filtre le queryset du champ 'employee'
        if manager:
            # Assurez-vous que votre modèle Employee a un champ `department` et `manager`
            self.fields['employee'].queryset = Employee.objects.filter(department=manager.department)
            # Optionnel : Exclure le manager lui-même de la liste
            self.fields['employee'].queryset = self.fields['employee'].queryset.exclude(pk=manager.pk)


class GoalUpdateStatusForm(forms.ModelForm):
    """
    Formulaire pour la mise à jour du statut et de la valeur d'un objectif.
    """
    class Meta:
        model = Goal
        fields = ['status', 'current_value']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'current_value': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class ElementEvaluationForm(forms.ModelForm):

    class Meta:
        model = ElementEvaluation
        fields = ['domaine', 'objectif']
        widgets = {
            'domaine': forms.Select(attrs={'class': 'form-select'}),
            'objectif': forms.TextInput(attrs={'class': 'form-control'}),
        }


class PerformanceReviewForm(forms.ModelForm):
    """
    Formulaire pour créer et modifier une revue de performance.
    """

    class Meta:
        model = PerformanceReview
        # Inclure tous les champs pertinents pour le formulaire
        fields = [
            'employee', 'review_date', 'comments',
            'securite_au_travail', 'competences_techniques',
            'efficacite_operationnelle', 'qualite_service_client',
            'collaboration_equipe', 'formations_recommender',
        ]

        # Ajouter des widgets pour un style CSS moderne
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'review_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),

            # Widgets pour les domaines de compétence
            'securite_au_travail': forms.Select(attrs={'class': 'form-select'}),
            'competences_techniques': forms.Select(attrs={'class': 'form-select'}),
            'efficacite_operationnelle': forms.Select(attrs={'class': 'form-select'}),
            'qualite_service_client': forms.Select(attrs={'class': 'form-select'}),
            'collaboration_equipe': forms.Select(attrs={'class': 'form-select'}),

            'formations_recommender': forms.SelectMultiple(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        # Récupère le manager depuis la vue pour filtrer la liste des employés
        reviewer = kwargs.pop('reviewer', None)
        super().__init__(*args, **kwargs)

        # Le manager ne peut évaluer que ses propres employés
        if reviewer and reviewer.is_manager:
            self.fields['employee'].queryset = Employee.objects.filter(manager=reviewer)