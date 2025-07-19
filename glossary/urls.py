from django.urls import path
from django_distill import distill_path
# from .models.feed import TermFeed

from . import views

from .models import Term

def get_paginated_term_pages():
    """
    Generate the pagination parameters for all pages.
    This will yield dictionaries with a 'page' key, for every page of terms.
    """
    total_terms = Term.objects.count()
    paginate_by = 20  # Match the value in your TermList view
    num_pages = (total_terms // paginate_by) + (1 if total_terms % paginate_by > 0 else 0)
    
    for page in range(1, num_pages + 1):
        yield {'page': page}

def get_all_terms():
    # This function needs to return an iterable of dictionaries.
    # Dictionaries are required as the URL this distill function is used by
    # has named parameters. You can just export a small subset of values
    # here if you wish to limit what pages will be generated.
    for post in Term.objects.all():
        # Note 'slug' match the URL parameter names
        yield {'slug': post.slug}


urlpatterns = [
    distill_path('', views.TermList.as_view(), name='termList'),
    # distill_path(
    #     '', 
    #     views.TermList.as_view(), 
    #     name='termList',
    #     distill_func=lambda: [{'page': 1}]  # Default to the first page
    # ),
    distill_path(
        'page/<int:page>/', 
        views.TermList.as_view(), 
        name='termListPaginated',
        distill_func=get_paginated_term_pages
    ),
    # distill_path('feed/', TermFeed(), name='termFeed', distill_file="terms/feed/index.xml"),
    distill_path('<slug:slug>/', views.termDetail, name='termDetail', distill_func=get_all_terms),
]