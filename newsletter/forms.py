from django import forms
from taggit.forms import TagWidget
from .models import Newsletter
from cyborg.widgets import RblTagInputWidget

class TaggitSelect2(forms.TextInput):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attrs['class'] = 'taggit-select2'

    class Media:
        css = {
            'all': ('https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/css/select2.min.css',)
        }
        js = (
            'https://cdn.jsdelivr.net/npm/jquery@3.6.0/dist/jquery.min.js',
            'https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/js/select2.min.js',
            'js/admin/taggit-select2-init.js', 
        )


class NewsletterForm(forms.ModelForm):
    class Meta:
        model = Newsletter
        fields = '__all__'
        widgets = {
            # 'tags': TaggitSelect2(),
            'tags': RblTagInputWidget,
        }