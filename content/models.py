from django.db import models

class HomePage(models.Model):
    headline = models.CharField(max_length=255, default="Upgrade your humanity.")
    subheadline = models.CharField(max_length=255, default="Lessons learned about humans through technology and systems...and vice versa")

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