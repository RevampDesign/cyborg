from django.db import models
from publishing.models import ScheduledPublish, Approval
from meta_seo.models import MetaSEO
from taggit.managers import TaggableManager
import marko, re

# def discover_possible_citations_in_text(body):
#     pattern = r'<em>([^<]*[A-Z][^<]*)</em>'
#     matches = re.findall(pattern, body)
#     for potential in matches:


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

    tags = TaggableManager(blank=True)

    live_view = 'newsletterDetail'
    preview_view = 'newsletterDetail'

    def available_tags(self):
        return u", ".join(o.name for o in self.tags.all())

    def read_time(self):
        return f"{round(len(self.body.split(" ")) / 200)} Min."

    def schema_publish_date(self):
        return self.publish_date.strftime("%Y-%m-%dT%H:%M:%SZ")

    def __str__(self):
        if self.title:
            return self.title
        return 'Newsletter ' + (self.pk)

    def save(self, *args, **kwargs):
        # Markdown editing enabled:
        if self.body:
            self.body = marko.convert(self.body)

        super().save(*args, **kwargs)