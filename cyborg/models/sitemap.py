from django.db import models
from django.urls import reverse
from django.contrib.sitemaps import Sitemap

class HTMLSitemap(Sitemap):
    def __init__(self, sitemaps, *args, **kwargs):
        # Pass this in from urls.py
        self.sitemaps = sitemaps
        super().__init__(*args, **kwargs)


    def items(self):
        return self.sitemaps.items()

    def location(self, obj):
        heading, url = obj
        return url

    def get_urls(self, page=1, site=None, protocol=None):
        urls = []
        for section, site in self.sitemaps.items():
            if not hasattr(site, 'heading'):
                site.heading = section
            
            for item in site.get_urls(page=page, site=site, protocol=protocol):
                item.section = site.heading
                urls.append(item)

        return urls

    def priority(self, obj):
        # Not used for the HTML version
        return None