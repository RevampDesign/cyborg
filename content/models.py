from django.db import models
from meta_seo.models import MetaSEO
from django.contrib.sitemaps import Sitemap
from django.urls import reverse

class HomePage(MetaSEO):
    headline = models.CharField(max_length=255, default="Upgrade your humanity.")
    subheadline = models.CharField(max_length=255, default="Lessons learned about humans through technology and systems...and vice versa")

    def get_absolute_url(self):
        return reverse('homePage')

class HomeHeroButton(models.Model):
    home_page = models.ForeignKey(
        'content.HomePage',
        related_name="buttons",
        on_delete=models.CASCADE,
        null=True,
    )

    title = models.CharField(max_length=50, default="Subscribe")
    link = models.CharField(max_length=500, default="/subscribe/")

    class ButtonTemplate(models.TextChoices):
        PRIMARY = 'btn-primary', 'Primary'
        SECONDARY = 'btn-secondary', 'Secondary'

    template = models.CharField(max_length=50, choices=ButtonTemplate.choices)


class HomeSitemap(Sitemap):
    changefreq = "monthly"
    priority = 1
    protocol = 'https'

    def items(self):
        return HomePage.objects.all()
        # return ['homePage'] #Static view, so call its URL name

    def heading(self):
        return 'Home Page'