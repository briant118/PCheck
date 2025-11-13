from django import template
import re

register = template.Library()

@register.filter
def get_int(value):
    """
    Extract the first integer found in the value.
    Returns None if no digits are present.
    """
    try:
        match = re.search(r'\d+', str(value))
        if not match:
            return None
        return int(match.group())
    except (ValueError, TypeError, AttributeError):
        return None
    

@register.filter
def to_range(value):
    try:
        value = int(value)
        if value < 1:
            return range(0)
        return range(1, value + 1)
    except (TypeError, ValueError):
        return range(0)