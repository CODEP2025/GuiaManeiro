
from django import template

register = template.Library()

@register.filter
def split(value, sep=';'):
    if value is None:
        return []
    return str(value).split(sep)

@register.filter
def strip(value):
    if value is None:
        return ''
    return str(value).strip()
