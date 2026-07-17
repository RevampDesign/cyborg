from django.db import models
from django.template.defaultfilters import slugify

from meta_seo.models import MetaSEO
from publishing.models import Approval


class SpanCategory(models.Model):
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=7, help_text="Hex color, e.g. #6e44ff")
    weight = models.PositiveIntegerField(default=0, help_text="Ordering in compass/legend")

    class Meta:
        ordering = ["weight"]

    def __str__(self):
        return self.name


class TimelineEra(models.Model):
    year = models.PositiveIntegerField(unique=True)
    human_framing = models.CharField(
        max_length=300,
        blank=True,
        help_text="One-line editorial frame for this year, in the author's voice.",
    )
    newsletter_url = models.URLField(blank=True)
    newsletter_title = models.CharField(max_length=300, blank=True)

    class Meta:
        ordering = ["-year"]

    def __str__(self):
        return str(self.year)


class TimelineEntry(MetaSEO, Approval):
    # MetaSEO provides: title, slug, description, keywords, noindex_nofollow,
    #                   date_created, date_updated
    # Approval provides: content_review, visual_review, seo_review,
    #                    approved, last_approval_date

    date = models.DateField(
        help_text="Where this sits on the timeline. May differ from the Source's publication date."
    )

    class DatePrecision(models.TextChoices):
        EXACT = "exact", "Exact date"
        MONTH = "month", "Month"
        YEAR = "year", "Year"

    date_precision = models.CharField(
        max_length=10,
        choices=DatePrecision.choices,
        default=DatePrecision.EXACT,
    )

    timeline_context = models.TextField(
        blank=True,
        help_text="Short framing for the timeline view (markdown). Detail content comes from linked Term/Source.",
    )

    source = models.ForeignKey(
        "glossary.Source",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="timeline_entries",
    )
    term = models.ForeignKey(
        "glossary.Term",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="timeline_entries",
    )
    related_entries = models.ManyToManyField("self", blank=True)

    class Kind(models.TextChoices):
        FILM = "film", "Film / TV"
        BOOK = "book", "Book / Publication"
        TECH = "tech", "Technology"
        EVENT = "event", "Historical Event"
        IDEA = "idea", "Idea / Concept"
        PERSONAL = "personal", "Personal / Newsletter"

    kind = models.CharField(
        max_length=20,
        choices=Kind.choices,
        blank=True,
        help_text="Leave blank to derive from linked Source's type.",
    )

    SOURCE_TYPE_TO_KIND = {
        "Movie": Kind.FILM,
        "TVSeries": Kind.FILM,
        "Book": Kind.BOOK,
        "Article": Kind.BOOK,
        "ScholarlyArticle": Kind.BOOK,
        "NewsArticle": Kind.BOOK,
    }

    @property
    def display_kind(self):
        if self.kind:
            return self.kind
        if self.source_id:
            return self.SOURCE_TYPE_TO_KIND.get(self.source.creative_work_type, self.Kind.EVENT)
        if self.term_id:
            return self.Kind.IDEA
        return self.Kind.EVENT

    def display_date(self):
        if self.date_precision == self.DatePrecision.EXACT:
            return self.date.strftime("%-d %B %Y").lstrip("0")
        if self.date_precision == self.DatePrecision.MONTH:
            return self.date.strftime("%B %Y")
        return str(self.date.year)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse("timeline_entry_detail", kwargs={"slug": self.slug})

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-date"]
        verbose_name_plural = "timeline entries"


class TimelineSpan(Approval):
    # Approval provides: content_review, visual_review, seo_review,
    #                    approved, last_approval_date
    # No MetaSEO here — title and slug declared directly.

    title = models.CharField(max_length=300)
    slug = models.SlugField(unique=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True, help_text="Blank = ongoing.")
    start_fuzzy = models.BooleanField(default=True)
    end_fuzzy = models.BooleanField(default=True)
    description = models.TextField(blank=True, help_text="Markdown.")
    term = models.ForeignKey(
        "glossary.Term",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="timeline_spans",
    )
    category = models.ForeignKey(
        SpanCategory,
        on_delete=models.PROTECT,
        related_name="spans",
    )

    # lane is computed at view time, never stored.

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-start_date"]
