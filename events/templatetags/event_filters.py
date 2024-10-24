from django import template

register = template.Library()

@register.filter
def reaction_count(event, reaction_type):
    """Returns the count of reactions of a specific type for the given event."""
    return event.reactions.filter(reaction_type=reaction_type).count()
