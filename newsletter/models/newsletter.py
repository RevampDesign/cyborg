from django.db import models
from publishing.models import ScheduledPublish, Approval
from meta_seo.models import MetaSEO
import marko

class Newsletter(MetaSEO, Approval, ScheduledPublish):
    author = models.ForeignKey(
        'author.Author',
        related_name="newsletters",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        default=1
    )
    # headline = models.CharField(max_length=300, blank=True) # Might be unnecessary

    body = models.TextField(blank=True)

    live_view = 'newsletterDetail'
    preview_view = 'newsletterDetail'

    def __str__(self):
        if self.title:
            return self.title
        return 'Newsletter ' + (self.pk)

    def save(self, *args, **kwargs):
        # Markdown editing enabled:
        if self.body:
            self.body = marko.convert(self.body)

        super().save(*args, **kwargs)