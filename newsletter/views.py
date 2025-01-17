from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.list import ListView

from .models import Newsletter

class NewsletterList(ListView):
    model = Newsletter # Use object_list in template
    paginate_by = 10
    template_name = 'newsletter/list.html'
    ordering = ['-publish_date']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['content'] = {'title': 'Newsletters', 'headline': 'The archives.', 'description': 'Peruse all of the CYBORG_ emails here or get them every week in your inbox.'}
        return context

# def newsletterList(request):
#     # content = HomePage.objects.get(pk=2)
#     newsletters = Newsletter.objects.order_by('-publish_date')

#     template_name = 'newsletter/list.html'

#     context = {'content': 'content', 'newsletters': newsletters}

#     return render(request, template_name, context)


def newsletterDetail(request, slug):
    content = get_object_or_404(Newsletter, slug=slug)

    template_name = 'newsletter/detail.html'

    context = {'content': content,}

    return render(request, template_name, context)