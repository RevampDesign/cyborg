from django.shortcuts import render
from .models import HomePage
from newsletter.models import Newsletter
from cyborg.models import HTMLSitemap

def homePage(request):
    content = HomePage.objects.get(pk=2)
    newsletters = Newsletter.objects.order_by('-publish_date')[:3]

    template_name = 'content/index.html'

    context = {'content': content, 'newsletters': newsletters}

    return render(request, template_name, context)


def htmlSitemap(request, sitemaps):
    sitemap = HTMLSitemap(sitemaps)

    return render(request, 'sitemap.html', {'sitemaps': sitemap})


# from django.http import HttpResponse
# def robots_txt(request):
#     template_name = 'robots.txt'

#     return HttpResponse(content, content_type="text/plain")