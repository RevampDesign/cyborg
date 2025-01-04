from django.db import models

class Author(models.Model):
    name = models.CharField(max_length=300, default="Jess Brown", help_text="Name as will be displayed on site and in schema")
    bio = models.TextField(blank=True, default="<p>Designer turned developer with MS. I'm exploring the relationships between technology, humanity, and other systems. After my diagnosis of Multiple Sclerosis, I was forced to confront uncomfortable aspects of life: my queerness, my mortality, my limitations. I believe it is through the acceptance of both the good and the bad—healthy, unhealthy; productive, unproductive; safe, risky—we can find progress, peace, and potential.</p>")

    # headshot ...?

    def __str__(self):
        return self.name