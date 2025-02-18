from django.db import models
from publishing.models import Approval, ScheduledPublish
from meta_seo.models import MetaSEO
import marko

class Policy(MetaSEO, Approval, ScheduledPublish):
    # headline = models.CharField(max_length=255)
    body = models.TextField(blank=True)

    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    live_view = 'policyDetail'
    preview_view = 'policyDetail'

    def __str__(self):
        if self.title:
            return self.title
        return 'Policy ' + (self.pk)

    def save(self, *args, **kwargs):
        # Markdown editing enabled:
        if self.body:
            self.body = marko.convert(self.body)

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Policy"
        verbose_name_plural = "Policies"