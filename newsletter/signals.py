# newsletter/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Newsletter
from recommendation.models import RecommendedLink
from glossary.models import Term

@receiver(post_save, sender=Newsletter)
def generate_recommended_links(sender, instance, created, **kwargs):
    # This signal handler should trigger a background task
    # to avoid blocking the user's request.
    # For a simple example, we'll run the logic directly.
    # In a production environment, use Celery or another task queue.

    # 1. Fetch all glossary terms at once for efficiency
    glossary_terms = Term.objects.all()

    # 2. Iterate and check for matches
    for term in glossary_terms:
        # Check if the term title is a substring of the newsletter body
        if term.title.lower() in instance.body.lower():
            # 3. Create or update the RecommendedLink instance
            RecommendedLink.objects.update_or_create(
                newsletter=instance,
                term=term,
                defaults={'matched_text': term.title}
            )
