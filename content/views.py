from django.shortcuts import render
from .models import HomePage
from newsletter.models import Newsletter

def homePage(request):
    content = HomePage.objects.get(pk=2)
    newsletters = Newsletter.objects.order_by('-publish_date')[:3]

    template_name = 'content/index.html'

    context = {'content': content, 'newsletters': newsletters}

    return render(request, template_name, context)