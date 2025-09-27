from django.db import models
from core.fields import OptimizedImageField
from meta_seo.models import MetaSEO
from publishing.models import Approval
from django.urls import reverse
import marko


class WorkDetail(MetaSEO, Approval):
    artwork = models.ForeignKey(
        "gallery.Artwork",
        related_name="work_details",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    body = models.TextField(blank=True, )

    impact = models.TextField(blank=True, help_text="Extra content for using the piece.")

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        kwargs = {
            'slug': self.slug
        }
        return reverse('workDetail', kwargs=kwargs)

    def save(self, *args, **kwargs):
        if self.body:
            self.body = marko.convert(self.body)

        super().save(*args, **kwargs)



class WorkButton(models.Model):
    work_detail = models.ForeignKey(
        'gallery.WorkDetail',
        related_name="buttons",
        on_delete=models.CASCADE,
        null=True,
    )

    title = models.CharField(max_length=50, default="Purchase Digital")
    link = models.CharField(max_length=500, )

    class ButtonTemplate(models.TextChoices):
        PRIMARY = 'btn-primary', 'Primary'
        SECONDARY = 'btn-secondary', 'Secondary'
        TEXT = 'btn-text', 'Text Button / Link'

    template = models.CharField(max_length=50, choices=ButtonTemplate.choices)
