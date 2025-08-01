from django import template

register = template.Library()

@register.filter
def get_proficiency_badge_color(level):
    """
    Retourne une couleur de badge Bootstrap/Phoenix en fonction du niveau de maîtrise.
    Utilisé dans les templates pour afficher visuellement le niveau de compétence.
    """
    if level == 1:
        return 'danger'    # Rouge pour Débutant
    elif level == 2:
        return 'warning'   # Jaune/Orange pour Connaissance de base
    elif level == 3:
        return 'info'      # Bleu clair pour Intermédiaire
    elif level == 4:
        return 'primary'   # Bleu foncé pour Avancé
    elif level == 5:
        return 'success'   # Vert pour Expert
    return 'secondary' # Couleur par défaut si le niveau n'est pas reconnu



@register.filter
def get_item(dictionary, key):
    """
    Permet d'accéder à un élément d'un dictionnaire par sa clé dans les templates Django.
    Utile quand la clé est un objet complexe (comme une instance d'un modèle).

    Exemple d'utilisation dans un template :
    {% load custom_filters %} {# N'oubliez pas cette ligne en haut de votre template #}
    ...
    {% with current_employee_skill=employee_current_skills|get_item:skill %}
        {% if current_employee_skill %}
            Niveau actuel : {{ current_employee_skill.get_proficiency_level_display }}
        {% endif %}
    {% endwith %}
    """
    if isinstance(dictionary, dict) and key in dictionary:
        return dictionary.get(key)
    return None