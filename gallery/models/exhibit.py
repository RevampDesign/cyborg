from django.db import models
from core.fields import OptimizedImageField
from meta_seo.models import MetaSEO
from publishing.models import Approval
import datetime
from django.utils.html import format_html
from django.urls import reverse

class Exhibit(MetaSEO, Approval):
    """ Most fields pulled from schema: 
    https://schema.org/ExhibitionEvent """

    name = models.CharField(max_length=300, blank=True, help_text="Title of the exhibit as it will be displayed on site and in schema")

    about = models.TextField(blank=True, help_text="The subject matter of the content.")

    image = OptimizedImageField(
        upload_to='images/gallery/exhibit/%Y/%m/',
        blank=True,
    )
    image_webp = models.ImageField(
        upload_to='images/gallery/exhibit/%Y/%m/',
        null=True,
        blank=True
    )

    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)


    # Put in offers??? Or just have individual artworks have them...
    # Example from https://schema.org/ExhibitionEvent
    # <div itemscope="" itemtype="https://schema.org/ExhibitionEvent">
    #    <a itemprop="offers" href="http://www.vam.ac.uk/whatson/event/5150/date/20151007/">Book tickets</a>
    # </div>

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        kwargs = {
            'slug': self.slug,
            'year': self.start_date.year
        }
        return reverse('exhibit', kwargs=kwargs)

    def save(self, *args, **kwargs):
        if self.title and not self.name:
            self.name = self.title

        super().save(*args, **kwargs)


class ExhibitWork(models.Model):
    """ Junction between artworks and exhibit so that many artworks can be in many exhibits, but we can still control the order of the works. """

    exhibit = models.ForeignKey(
        'gallery.Exhibit',
        on_delete=models.CASCADE,
        null=True,
    )
    
    artwork = models.ForeignKey(
        'gallery.Artwork',
        on_delete=models.CASCADE,
        null=True,
    )

    # Auto Ordering field for sortable2
    order = models.PositiveIntegerField(default=0, blank=False, null=False)

    class Meta(object):
        # Auto Ordering field for sortable2
        ordering = ['order']
    