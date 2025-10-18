from django.urls import path
from django_distill import distill_path

from . import views

from .models import Artwork, WorkDetail, Exhibit

def get_paginated_work_pages():
    """
    Generate the pagination parameters for all pages.
    This will yield dictionaries with a 'page' key, for every page of works.
    """
    total_works = WorkDetail.objects.count()
    paginate_by = 10  # Match the value in your workList view
    num_pages = (total_works // paginate_by) + (1 if total_works % paginate_by > 0 else 0)
    
    for page in range(1, num_pages + 1):
        yield {'page': page}

def get_all_works():
    # This function needs to return an iterable of dictionaries.
    # Dictionaries are required as the URL this distill function is used by
    # has named parameters. You can just export a small subset of values
    # here if you wish to limit what pages will be generated.
    for post in WorkDetail.objects.all():
        if post.approved:
            # Note 'slug' match the URL parameter names
            yield {'slug': post.slug}

def get_all_exhibits():
    # This function needs to return an iterable of dictionaries.
    # Dictionaries are required as the URL this distill function is used by
    # has named parameters. You can just export a small subset of values
    # here if you wish to limit what pages will be generated.
    for post in Exhibit.objects.all():
        if post.approved:
            # Note 'slug' match the URL parameter names
            yield {'slug': post.slug, 'year': post.start_date.year}


urlpatterns = [
    distill_path('', views.Gallery.as_view(), name='gallery'),
    # distill_path(
    #     '', 
    #     views.TermList.as_view(), 
    #     name='termList',
    #     distill_func=lambda: [{'page': 1}]  # Default to the first page
    # ),
    distill_path(
        'page/<int:page>/', 
        views.Gallery.as_view(), 
        name='galleryPaginated',
        distill_func=get_paginated_work_pages
    ),
    # distill_path('feed/', TermFeed(), name='termFeed', distill_file="terms/feed/index.xml"),
    distill_path('exhibit/<slug:slug>/<int:year>/', views.exhibit, name='exhibit', distill_func=get_all_exhibits),
    distill_path('<slug:slug>/', views.workDetail, name='workDetail', distill_func=get_all_works),
]