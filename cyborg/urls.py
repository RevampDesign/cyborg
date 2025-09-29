from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django_distill import distill_path
from django.contrib.sitemaps.views import sitemap
from django.conf import settings
from django.conf.urls.static import static

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
    path('gallery/', include('gallery.urls')),
    path('glossary/', include('glossary.urls')),
    path('newsletters/', include('newsletter.urls')),
    path('policies/', include('policy.urls')),
    distill_path('sitemap/', htmlSitemap, {'sitemaps': sitemaps}, name='htmlSitemap', ),
	distill_path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    distill_path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type="text/plain"), name='robots'),
    distill_path('sdrp/', TemplateView.as_view(template_name='content/sdrp.html'), name='sdrp'),
    path('machina/', admin.site.urls),

    path('admin/', include(wagtailadmin_urls)),
    path('documents/', include(wagtaildocs_urls)),
    path('pages/', include(wagtail_urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)