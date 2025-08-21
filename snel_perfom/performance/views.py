from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Goal, PerformanceReview
from .forms import GoalCreateForm, GoalUpdateStatusForm, PerformanceReviewForm
from django.http import HttpResponseRedirect
from django.views import View


class GoalListView(LoginRequiredMixin, ListView):
    """
    Vue pour lister tous les objectifs.
    """
    model = Goal
    context_object_name = 'goals'
    template_name = 'goal_list.html'

    def get_queryset(self):
        # Permet à un manager de voir les objectifs de ses employés.
        # Permet à un employé de voir ses propres objectifs.
        if self.request.user.is_manager:
            return Goal.objects.filter(employee__manager=self.request.user)
        return Goal.objects.filter(employee=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['update_form'] = GoalUpdateStatusForm()
        return context


class GoalCreateView(LoginRequiredMixin, CreateView):
    """
    Vue pour créer un nouvel objectif.
    """
    model = Goal
    form_class = GoalCreateForm
    template_name = 'goal_create.html'
    success_url = reverse_lazy('goals:list')

    def get_form_kwargs(self):
        """
        Passe l'utilisateur actuel au formulaire pour filtrer les employés.
        """
        kwargs = super().get_form_kwargs()
        kwargs['manager'] = self.request.user  # Assurez-vous que self.request.user est votre modèle Employee
        return kwargs

    def form_valid(self, form):
        form.instance.set_by = self.request.user
        return super().form_valid(form)

class GoalUpdateView(LoginRequiredMixin, UpdateView):
    """
    Vue pour modifier un objectif existant.
    """
    model = Goal
    form_class = GoalUpdateStatusForm
    template_name = 'goal_update.html'
    success_url = reverse_lazy('goals:list')

    def get_queryset(self):
        # S'assure que seul le manager peut modifier les objectifs.
        return super().get_queryset().filter(employee__manager=self.request.user)


class GoalUpdateStatusView(LoginRequiredMixin, View):
    """
    Vue pour mettre à jour le statut et la valeur d'un objectif via une requête POST.
    """

    def post(self, request, pk):
        goal = get_object_or_404(Goal, pk=pk)
        form = GoalUpdateStatusForm(request.POST, instance=goal)
        if form.is_valid():
            form.save()
            # Redirige vers la page d'où vient la requête
        return redirect(request.META.get('HTTP_REFERER', reverse_lazy('goals:list')))


class PerformanceReviewListView(LoginRequiredMixin, ListView):
    """
    Vue pour lister les revues de performance.
    Un manager voit les revues de ses employés, un employé voit ses propres revues.
    """
    model = PerformanceReview
    template_name = 'review_list.html'
    context_object_name = 'reviews'

    def get_queryset(self):
        # Si l'utilisateur est un manager, il voit les revues de ses employés.
        if self.request.user.is_manager:
            return PerformanceReview.objects.filter(employee__manager=self.request.user).order_by('-review_date')
        # Si c'est un employé simple, il voit ses propres revues.
        return PerformanceReview.objects.filter(employee=self.request.user).order_by('-review_date')


class PerformanceReviewCreateView(LoginRequiredMixin, CreateView):
    """
    Vue pour créer une nouvelle revue de performance.
    """
    model = PerformanceReview
    form_class = PerformanceReviewForm
    template_name = 'review_form.html'
    success_url = reverse_lazy('goals:perform-list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['reviewer'] = self.request.user
        return kwargs

    def form_valid(self, form):
        # L'évaluateur est automatiquement l'utilisateur connecté
        form.instance.reviewer = self.request.user
        return super().form_valid(form)


class PerformanceReviewUpdateView(LoginRequiredMixin, UpdateView):
    """
    Vue pour modifier une revue de performance existante.
    Seul l'évaluateur peut modifier la revue.
    """
    model = PerformanceReview
    form_class = PerformanceReviewForm
    template_name = 'review_form.html'
    success_url = reverse_lazy('goals:perform-list')

    def get_queryset(self):
        # S'assure que seul l'évaluateur peut modifier sa propre revue
        queryset = super().get_queryset()
        return queryset.filter(reviewer=self.request.user)