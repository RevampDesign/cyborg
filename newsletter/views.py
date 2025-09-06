from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.list import ListView
from django.urls import reverse

from .models import Newsletter
from glossary.models import Term
import re


from django.http import JsonResponse
from taggit.models import Tag

def tag_autocomplete(request):
    query = request.GET.get('q', '')
    tags = Tag.objects.filter(name__icontains=query).values_list('name', flat=True)
    return JsonResponse(list(tags), safe=False)


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

def get_linked_newsletters(article):
    # Look for CYBORG_ newsletter slugs and return a list of them.
    slug_search = re.compile(r'\/newsletters\/([\w-]+)\/\"\>')
    slugs_found = slug_search.findall(article)
    if not slugs_found:
        return None

    newsletter_previews = []
    for slug in slugs_found:
        try:
            pre = Newsletter.objects.get(slug=slug)
            obj = {
                'title': pre.title,
                'slug': slug,
                'url': pre.get_absolute_url(), 
                'description': pre.description,
                'publish_date': pre.publish_date,
            }
            newsletter_previews.append(obj)
        except:
            print(f"Couldn't find slug: {slug}")

    return newsletter_previews

def get_linked_terms(article):
    # Look for glossary/terms slugs and return a list of them.
    slug_search = re.compile(r'\/glossary\/([\w-]+)\/\"\>')
    slugs_found = slug_search.findall(article)
    if not slugs_found:
        return None

    term_previews = []

    for slug in slugs_found:
        # slugs.append(slug)

        pre = Term.objects.get(slug=slug)
        obj = {
            'title': pre.title,
            'slug': slug,
            'url': pre.get_absolute_url(), 
            'description': pre.description,
        }
        term_previews.append(obj)

    print("LINKED:\t", term_previews)
    return term_previews


def newsletterDetail(request, slug):
    content = get_object_or_404(Newsletter, slug=slug)

    breadcrumb_parents = [{'title': 'Newsletters', 'url': '/newsletters/'}]

    newsletter_previews = get_linked_newsletters(content.body)
    # print("LINKED:\t", newsletter_previews)

    glossary_terms_previews = get_linked_terms(content.body)

    change_url = reverse('admin:{app_label}_{model_name}_change'.format(app_label=content._meta.app_label, model_name=content._meta.model_name), args=(content.id,))

    template_name = 'newsletter/detail.html'

    context = {'content': content, 'change_url': change_url, 'breadcrumb_parents': breadcrumb_parents, 'newsletter_previews': newsletter_previews, 'glossary_terms_previews': glossary_terms_previews}

    return render(request, template_name, context)