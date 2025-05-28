from django.urls import path
from django_distill import distill_path
from .models.feed import NewsletterFeed

from . import views

from .models import Newsletter

def get_paginated_newsletter_pages():
    """
    Generate the pagination parameters for all pages.
    This will yield dictionaries with a 'page' key, for every page of newsletters.
    """
    total_newsletters = Newsletter.objects.count()
    paginate_by = 10  # Match the value in your NewsletterList view
    num_pages = (total_newsletters // paginate_by) + (1 if total_newsletters % paginate_by > 0 else 0)
    
    for page in range(1, num_pages + 1):
        yield {'page': page}

def get_all_newsletters():
    # This function needs to return an iterable of dictionaries.
    # Dictionaries are required as the URL this distill function is used by
    # has named parameters. You can just export a small subset of values
    # here if you wish to limit what pages will be generated.
    for post in Newsletter.objects.all():
        # Note 'slug' match the URL parameter names
        yield {'slug': post.slug}


urlpatterns = [
    distill_path('', views.NewsletterList.as_view(), name='newsletterList'),
    # distill_path(
    #     '', 
    #     views.NewsletterList.as_view(), 
    #     name='newsletterList',
    #     distill_func=lambda: [{'page': 1}]  # Default to the first page
    # ),
    distill_path(
        'page/<int:page>/', 
        views.NewsletterList.as_view(), 
        name='newsletterListPaginated',
        distill_func=get_paginated_newsletter_pages
    ),
    distill_path('feed/', NewsletterFeed(), name='newsletterFeed', distill_file="rss.xml"),
    distill_path('<slug:slug>/', views.newsletterDetail, name='newsletterDetail', distill_func=get_all_newsletters),
]