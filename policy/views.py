from django.shortcuts import render, redirect, get_object_or_404

from .models import Policy

def policyDetail(request, slug):
    content = get_object_or_404(Policy, slug=slug)
    breadcrumb_parents = [{'title': 'Policies', 'url': None}]

    template_name = 'policy/detail.html'

    context = {'content': content, 'breadcrumb_parents': breadcrumb_parents,}

    return render(request, template_name, context)