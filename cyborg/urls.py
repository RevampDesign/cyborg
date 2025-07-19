"""
URL configuration for cyborg project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django_distill import distill_path
from django.contrib.sitemaps.views import sitemap

from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls

from content.views import homePage, htmlSitemap
from content.models import HomeSitemap
from newsletter.models import NewsletterSitemap
from topic.models import TopicSitemap

sitemaps = {
    'home': HomeSitemap,
    'newsletters': NewsletterSitemap,
    'topics': TopicSitemap,
}

urlpatterns = [
    distill_path('', homePage, name="homePage"),
    distill_path('subscribe/', TemplateView.as_view(template_name='content/subscribe.html'), name='subscribe'),
    path('topics/', include('topic.urls')),
    path('glossary/', include('glossary.urls')),
    path('newsletters/', include('newsletter.urls')),
    path('policies/', include('policy.urls')),
    distill_path('sitemap/', htmlSitemap, {'sitemaps': sitemaps}, name='htmlSitemap', ),
	distill_path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    distill_path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type="text/plain"), name='robots'),
    path('machina/', admin.site.urls),

    path('admin/', include(wagtailadmin_urls)),
    path('documents/', include(wagtaildocs_urls)),
    path('pages/', include(wagtail_urls)),
]
