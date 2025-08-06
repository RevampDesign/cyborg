from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.list import ListView
from django.urls import reverse

from .models import Newsletter
import re

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

def find_linked_newsletters(article):
    # Look for CYBORG_ newsletter slugs and return a list of them.
    slug_search = re.compile(r'\/newsletters\/(.+)\/\"\>')
    slugs_found = slug_search.findall(article)
    slugs = []
    if slugs_found:
        for slug in slugs_found:
            slugs.append(slug)
        return slugs
    return None

def newsletterDetail(request, slug):
    content = get_object_or_404(Newsletter, slug=slug)

    breadcrumb_parents = [{'title': 'Newsletters', 'url': '/newsletters/'}]

    newsletter_slugs_found = find_linked_newsletters(content.body)

    newsletter_previews = []
    
    if newsletter_slugs_found:
        for slug in newsletter_slugs_found:
            pre = Newsletter.objects.get(slug=slug)
            obj = {
                'title': pre.title,
                'slug': slug,
                'url': pre.get_absolute_url(), 
                'description': pre.description,
                'publish_date': pre.publish_date,
            }
            newsletter_previews.append(obj)


    print("LINKED:\t", newsletter_previews)

    change_url = reverse('admin:{app_label}_{model_name}_change'.format(app_label=content._meta.app_label, model_name=content._meta.model_name), args=(content.id,))

    template_name = 'newsletter/detail.html'

    context = {'content': content, 'change_url': change_url, 'breadcrumb_parents': breadcrumb_parents, 'newsletter_previews': newsletter_previews}

    return render(request, template_name, context)