from datetime import timedelta
from django.utils import timezone
from skill_training.models import RecommendedTraining
from skill_training.ia_logique import run_ai_recommendation_process
from employee.models import Preferences

def check_and_run_recommendations(frequency_type):
    """
    Vérifie le temps écoulé depuis la dernière recommandation IA et déclenche
    la fonction run_ai_recommendation si la fréquence spécifiée est atteinte.
    """
    now = timezone.now()
    last_recommendation = RecommendedTraining.objects.order_by('-recommendation_date').first()

    if not last_recommendation:
        run_ai_recommendation_process()
        return True

    time_since_last_recommendation = now - last_recommendation.recommendation_date

    if frequency_type == 'journaliere':
        threshold = timedelta(days=1)
    elif frequency_type == 'hebdomadaire':
        threshold = timedelta(weeks=1)
    elif frequency_type == 'mensuel':
        threshold = timedelta(days=30)
    else:
        return False

    if time_since_last_recommendation >= threshold:
        try:
            run_ai_recommendation_process()
            return True
        except Exception as e:
            return False
    else:
        return False