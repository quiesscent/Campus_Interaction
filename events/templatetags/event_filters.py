from django import template

register = template.Library()

@register.filter
def reaction_count(event, reaction_type):
    """Returns the count of reactions of a specific type for the given event."""
    return event.reactions.filter(reaction_type=reaction_type).count()
@register.filter
def multiply(value, arg):
    """Multiplies the value by the given argument."""
    try:
        return int(value) * int(arg)
    except (ValueError, TypeError):
        return value  # Return the original value if conversion fails
