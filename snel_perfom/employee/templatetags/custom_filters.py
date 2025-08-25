from django import template

register = template.Library()

@register.filter
def mul(value, arg):
    """Multiplies the value by the argument."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return None

@register.filter
def div(value, arg):
    """Divides the value by the argument."""
    try:
        return float(value) / float(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        return None


@register.filter
def get_attribute(obj, attr):
    """Récupère la valeur d'un attribut sur un objet."""
    return getattr(obj, attr, None)

@register.filter
def get_attribute_display(obj, attr):
    """Récupère la valeur d'affichage d'un attribut (ex: get_status_display)."""
    return getattr(obj, f'get_{attr}_display', lambda: '')()