from django import template

register = template.Library()

@register.filter
def chunks(value, chunk_size):
    """Yield successive n-sized chunks from a list."""
    for i in range(0, len(value), chunk_size):
        yield value[i:i + chunk_size]

# custom_filters.py
from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    return value * arg
