from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.views.generic.list import ListView
from django.urls import reverse

from .models import Artwork, WorkDetail, Exhibit

class Gallery(ListView):
    model = WorkDetail # Use object_list in template
    paginate_by = 10
    template_name = 'gallery/list.html'
    ordering = ['title']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['content'] = {'title': 'Gallery', 'headline': 'Art pieces for humanity.', 'description': 'Works created by Jess Brown for the purpose of promoting the dignity of humanity or critiques of systems that remove that dignity.'}
        return context



def workDetail(request, slug):
    content = get_object_or_404(WorkDetail, slug=slug)

    if not content.approved:
        raise Http404("Not Found")

    breadcrumb_parents = [{'title': 'Gallery', 'url': '/gallery/'}]

    change_url = reverse('admin:{app_label}_{model_name}_change'.format(app_label=content._meta.app_label, model_name=content._meta.model_name), args=(content.id,))

    template_name = 'gallery/detail.html'

    context = {'content': content, 'change_url': change_url, 'breadcrumb_parents': breadcrumb_parents}

    return render(request, template_name, context)


def exhibit(request, slug, year):
    content = get_object_or_404(
            Exhibit, 
            slug=slug, 
            start_date__year=year
        )

    if not content.approved:
        raise Http404("Not Found")

    breadcrumb_parents = [{'title': 'Gallery', 'url': '/gallery/'}]

    change_url = reverse('admin:{app_label}_{model_name}_change'.format(app_label=content._meta.app_label, model_name=content._meta.model_name), args=(content.id,))

    template_name = 'gallery/exhibit.html'

    context = {'content': content, 'change_url': change_url, 'breadcrumb_parents': breadcrumb_parents}

    return render(request, template_name, context)