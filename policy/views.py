from django.shortcuts import render, redirect, get_object_or_404

from .models import Policy

def policyDetail(request, slug):
    content = get_object_or_404(Policy, slug=slug)

    template_name = 'policy/detail.html'

    context = {'content': content,}

    return render(request, template_name, context)