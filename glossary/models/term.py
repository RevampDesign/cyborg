from django.db import models
from meta_seo.models import MetaSEO
from publishing.models import Approval
from django.urls import reverse

# from wagtail.models import Page
# from wagtail.admin.panels import FieldPanel
# from wagtail.fields import RichTextField

import marko

class Term(MetaSEO, Approval): # Removed Page to avoid migration issues merging to wagtail
    summary = models.TextField(blank=True, verbose_name="High Level Summary")

    # body = RichTextField(blank=True)

    sources = models.TextField(blank=True, help_text="List of sources / further exploration")

    # content_panels = Page.content_panels + [
    #     FieldPanel('summary'),
    #     FieldPanel('body'),
    #     FieldPanel('sources'),
    # ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        kwargs = {
            'slug': self.slug
        }
        return reverse('termDetail', kwargs=kwargs)

    def save(self, *args, **kwargs):
        # Markdown editing enabled:
        if self.summary:
            self.summary = marko.convert(self.summary)
        if self.sources:
            self.sources = marko.convert(self.sources)

        super().save(*args, **kwargs)