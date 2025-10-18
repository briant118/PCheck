from django import template
import re

register = template.Library()

@register.filter
def get_int(value):
    try:
        match = re.search(r'\d+', str(value))
        if match:
            return int(match.group())
        return None
    except (ValueError, TypeError):
        return None