import re
from urllib.parse import urlparse


BASE_DOMAIN = "cyborgnewsletter.com"
DOMAIN_REGEX = re.compile(
    r'(?P<prefix>["\'])(https?://' + re.escape(BASE_DOMAIN) + r')(?P<path>/[^"\']*)'
)

def clean_absolute_urls(html_content):
    """
    Identifies and cleans absolute URLs matching BASE_DOMAIN to relative URLs.

    Returns a tuple: (cleaned_html_content, list_of_matches)
    """
    matches = []

    def replacer(match):
        # The path group contains the part after the domain, starting with a '/'
        path = match.group('path')
        matches.append({
            'original': match.group(2) + path, # The full absolute URL
            'relative': path
        })
        # The replacement is just the opening quote + the path
        return match.group('prefix') + path

    cleaned_content = DOMAIN_REGEX.sub(replacer, html_content)

    return cleaned_content, matches
