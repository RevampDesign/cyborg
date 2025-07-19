from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.list import ListView
from django.urls import reverse

from .models import Term

class TermList(ListView):
    model = Term # Use object_list in template
    paginate_by = 20
    template_name = 'glossary/list.html'
    ordering = ['title']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['content'] = {'title': 'Glossary', 'headline': 'Common terms, theories, topics, and resources.', 'description': 'Get caught up with various terms and themes. A quick look at the research that influences the conclusions discussed in newsletters.'}
        return context



def termDetail(request, slug):
    content = get_object_or_404(Term, slug=slug)

    breadcrumb_parents = [{'title': 'Glossary', 'url': '/glossary/'}]

    change_url = reverse('admin:{app_label}_{model_name}_change'.format(app_label=content._meta.app_label, model_name=content._meta.model_name), args=(content.id,))

    template_name = 'glossary/detail.html'

    context = {'content': content, 'change_url': change_url, 'breadcrumb_parents': breadcrumb_parents}

    return render(request, template_name, context)