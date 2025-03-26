from django.urls import path
from django_distill import distill_path

from . import views

from .models import Topic

def get_paginated_topic_pages():
    """
    Generate the pagination parameters for all pages.
    This will yield dictionaries with a 'page' key, for every page of topics.
    """
    total_topics = Topic.objects.count()
    paginate_by = 10  # Match the value in your TopicList view
    num_pages = (total_topics // paginate_by) + (1 if total_topics % paginate_by > 0 else 0)
    
    for page in range(1, num_pages + 1):
        yield {'page': page}

def get_all_topics():
    # This function needs to return an iterable of dictionaries.
    # Dictionaries are required as the URL this distill function is used by
    # has named parameters. You can just export a small subset of values
    # here if you wish to limit what pages will be generated.
    for post in Topic.objects.all():
        # Note 'slug' match the URL parameter names
        yield {'slug': post.slug}


urlpatterns = [
    distill_path('', views.TopicList.as_view(), name='topicList'),
    # distill_path(
    #     '', 
    #     views.TopicList.as_view(), 
    #     name='topicList',
    #     distill_func=lambda: [{'page': 1}]  # Default to the first page
    # ),
    distill_path(
        'page/<int:page>/', 
        views.TopicList.as_view(), 
        name='topicListPaginated',
        distill_func=get_paginated_topic_pages
    ),
    distill_path('<slug:slug>/', views.topicDetail, name='topicDetail', distill_func=get_all_topics),
]