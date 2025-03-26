from django.db import models
from publishing.models import ScheduledPublish, Approval
from meta_seo.models import MetaSEO
from django.urls import reverse 
import marko
from taggit.managers import TaggableManager

class Topic(MetaSEO, Approval):
    body = models.TextField(blank=True, help_text="Mini-essay on the topic.")

    tags = TaggableManager(blank=True)

    order = models.PositiveIntegerField(
        default=0,
        blank=False,
        null=False,
    )

    live_view = 'topicDetail'
    preview_view = 'topicDetail'

    def get_absolute_url(self):
        """ For 'View on Site' buttons. Calls the View with the slug as the argument. If the page is approved and the publish date is reached, the 'View on Site' button will go to the live page, otherwise, it goes to the preview page. """
        kwargs = {
            'slug': self.slug
        }
        if self.approved:
            return reverse(self.live_view, kwargs=kwargs)
        else:
            return reverse(self.preview_view, kwargs=kwargs)

    def __str__(self):
        if self.title:
            return self.title
        return 'Newsletter ' + (self.pk)

    def save(self, *args, **kwargs):
        # Markdown editing enabled:
        if self.body:
            self.body = marko.convert(self.body)

        super().save(*args, **kwargs)

    class Meta:
        ordering = ['order']
