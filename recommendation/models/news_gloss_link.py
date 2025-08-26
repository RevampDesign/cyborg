from django.db import models
from newsletter.models import Newsletter
from glossary.models import Term

class RecommendedLink(models.Model):
    newsletter = models.ForeignKey(Newsletter, on_delete=models.CASCADE, related_name='recommended_links')
    term = models.ForeignKey(Term, on_delete=models.CASCADE)
    matched_text = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    active = models.BooleanField(default=True, help_text="Uncheck to remove from the page's rail.")

    class Meta:
        # Prevents duplicate recommendations for the same newsletter/term pair
        unique_together = ('newsletter', 'term')