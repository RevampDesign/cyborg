from django.urls import path
from django_distill import distill_path

from . import views

from .models import Newsletter

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
    distill_path('<slug:slug>/', views.newsletterDetail, name='newsletterDetail', distill_func=get_all_newsletters),
]