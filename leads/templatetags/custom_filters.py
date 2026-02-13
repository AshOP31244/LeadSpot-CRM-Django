from django import template

register = template.Library()


@register.filter
def format_stage(value):
    """Convert stage from 'oa_created' to 'OA CREATED'"""
    if not value:
        return value
    return value.upper().replace('_', ' ')
