from django import forms

from skill_training.models import TrainingCourse


class TrainingCourseForm(forms.ModelForm):
    class Meta:
        model = TrainingCourse
        fields = ['title', 'description', 'provider', 'duration_hours', 'cost', 'skills_covered', 'training_type', 'url_link']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'provider': forms.TextInput(attrs={'class': 'form-control'}),
            'duration_hours': forms.NumberInput(attrs={'class': 'form-control'}),
            'cost': forms.NumberInput(attrs={'class': 'form-control'}),
            'skills_covered': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'training_type': forms.Select(attrs={'class': 'form-select'}),
            'url_link': forms.URLInput(attrs={'class': 'form-control'}),
        }