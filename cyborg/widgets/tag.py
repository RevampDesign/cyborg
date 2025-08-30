from django.forms.widgets import Textarea
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string

class RblTagInputWidget(Textarea):
    template_name = 'newsletter/widgets/tag-web-component.html'
    # cyborg/templates/widgets/tag-web-component.html

    class Media:
        js = (
            'js/admin/tag.js', # Path to your web component file
        )
        css = {
            'all': ('css/admin/tag.css',)
        }

    def render(self, name, value, attrs=None, renderer=None):
        # Check if the value is a list-like object (e.g., a queryset of Tags)
        if value is not None and not isinstance(value, str):
            # Convert each Tag object to a string before joining
            value = ', '.join([str(tag) for tag in value])
        
        # Now, `value` is a comma-separated string, which `super().render()` can handle
        return super().render(name, value, attrs, renderer)