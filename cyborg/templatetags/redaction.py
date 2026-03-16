import re
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

def replace_with_bars(match):
    # Extract the text between <redacted> and </redacted>
    content = match.group(1)
    # Replace every character (including spaces) with the heavy vertical bar
    # Using the unicode character directly is often more reliable than the entity
    redacted_text = '░' * len(content)

    # Add back redacted inline
    redacted_text = f'<redacted title="Redacted. Subscribe to get uncensored content!">{redacted_text}</redacted>'
    return redacted_text

@register.filter(name='apply_redaction')
def apply_redaction(value):
    if not isinstance(value, str):
        return value

    # Regex to find <redacted>content</redacted>
    pattern = r'<redacted>(.*?)</redacted>'
    
    # Process the string
    # flags=re.DOTALL ensures it catches content spanning multiple lines
    result = re.sub(pattern, replace_with_bars, value, flags=re.DOTALL)
    
    # We return mark_safe so Django doesn't escape the HTML of the rest of your body
    return mark_safe(result)