from django import forms
from django.contrib import admin
from django.forms import TextInput
from django.utils.html import format_html

from cyborg.mixins import AdminViewOnLocalSiteMixin

from .models import SpanCategory, TimelineEntry, TimelineEra, TimelineSpan


# ── Forms ────────────────────────────────────────────────────────────────────

class TimelineEntryForm(forms.ModelForm):
    class Meta:
        model = TimelineEntry
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["date"].required = False

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get("date"):
            source = cleaned_data.get("source")
            if source and source.date_published:
                cleaned_data["date"] = source.date_published
            else:
                self.add_error(
                    "date",
                    "Provide a date, or link a Source that has a publication date.",
                )
        return cleaned_data


# ── SpanCategory ─────────────────────────────────────────────────────────────

@admin.register(SpanCategory)
class SpanCategoryAdmin(AdminViewOnLocalSiteMixin, admin.ModelAdmin):
    list_display = ["name", "color_swatch", "weight"]
    list_editable = ["weight"]

    def color_swatch(self, obj):
        return format_html(
            '<span style="display:inline-block;width:18px;height:18px;'
            'background:{};border-radius:3px;vertical-align:middle;"></span>',
            obj.color,
        )
    color_swatch.short_description = "Color"

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == "color":
            kwargs["widget"] = TextInput(attrs={"type": "color"})
        return super().formfield_for_dbfield(db_field, request, **kwargs)


# ── TimelineEntry ─────────────────────────────────────────────────────────────

@admin.register(TimelineEntry)
class TimelineEntryAdmin(AdminViewOnLocalSiteMixin, admin.ModelAdmin):
    form = TimelineEntryForm
    save_on_top = True
    search_fields = ["title"]
    autocomplete_fields = ["source", "term", "related_entries"]
    date_hierarchy = "date"
    ordering = ["-date"]
    prepopulated_fields = {"slug": ("title",)}
    list_filter = ["kind", "date_precision", "approved"]
    list_display = ["__str__", "date", "date_precision", "display_kind_col", "has_source", "has_term"]

    def display_kind_col(self, obj):
        k = obj.display_kind
        label = obj.Kind(k).label
        if not obj.kind:
            label += " (derived)"
        return label
    display_kind_col.short_description = "Kind"

    def has_source(self, obj):
        return bool(obj.source_id)
    has_source.boolean = True
    has_source.short_description = "Source"

    def has_term(self, obj):
        return bool(obj.term_id)
    has_term.boolean = True
    has_term.short_description = "Term"

    fieldsets = (
        ("Timeline placement", {
            "fields": ("date", "date_precision", "kind"),
        }),
        ("Content", {
            "fields": ("title", "slug", "timeline_context"),
        }),
        ("Glossary links", {
            "fields": ("source", "term"),
        }),
        ("Connections", {
            "fields": ("related_entries",),
            "classes": ("collapse",),
        }),
        ("Meta / SEO", {
            "fields": ("description", "keywords", "noindex_nofollow"),
        }),
        ("Publishing", {
            "fields": ("content_review", "visual_review", "seo_review", "approved"),
        }),
    )


# ── TimelineSpan ──────────────────────────────────────────────────────────────

@admin.register(TimelineSpan)
class TimelineSpanAdmin(AdminViewOnLocalSiteMixin, admin.ModelAdmin):
    save_on_top = True
    search_fields = ["title"]
    autocomplete_fields = ["term"]
    ordering = ["-start_date"]
    list_display = ["title", "start_date", "end_date", "category", "start_fuzzy", "end_fuzzy"]
    list_filter = ["category", "start_fuzzy", "end_fuzzy"]


# ── TimelineEra ───────────────────────────────────────────────────────────────

@admin.register(TimelineEra)
class TimelineEraAdmin(AdminViewOnLocalSiteMixin, admin.ModelAdmin):
    ordering = ["-year"]
    list_display = ["year", "human_framing", "newsletter_title"]
    list_editable = ["human_framing"]
