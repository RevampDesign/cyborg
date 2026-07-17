import datetime

from django.contrib import admin
from django.template.defaultfilters import slugify
from cyborg.mixins import ExportModelCSVMixin, AdminViewOnLocalSiteMixin
from adminsortable2.admin import SortableAdminBase, SortableInlineAdminMixin

from .models import Term, Source, SourceAuthor, SourcePublisher, TermSource

# Imported here (not at top of timeline.admin) to avoid circular imports.
from timeline.models import TimelineEntry, TimelineSpan


class InlineTermSource(SortableInlineAdminMixin, admin.TabularInline):
    model = TermSource
    extra = 0


class TimelineEntryInline(admin.StackedInline):
    model = TimelineEntry
    fk_name = "source"
    extra = 0
    fields = ["title", "slug", "date", "date_precision", "kind", "timeline_context", "approved"]

    def get_extra(self, request, obj=None, **kwargs):
        # Show one pre-filled form only when editing an existing Source;
        # nothing to derive from on the "add new source" page.
        return 1 if obj else 0

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        if obj is not None:
            bf = formset.form.base_fields
            title = obj.alt_title or obj.title
            bf["title"].initial = title
            bf["slug"].initial = slugify(title)
            bf["kind"].initial = TimelineEntry.SOURCE_TYPE_TO_KIND.get(
                obj.creative_work_type, ""
            )
            bf["timeline_context"].initial = obj.description
            if obj.date_published:
                bf["date"].initial = obj.date_published
            elif obj.copyright_year:
                bf["date"].initial = datetime.date(obj.copyright_year, 1, 1)
                bf["date_precision"].initial = TimelineEntry.DatePrecision.YEAR
        return formset


class TimelineEntryFromTermInline(TimelineEntryInline):
    fk_name = "term"


class TimelineSpanInline(admin.TabularInline):
    model = TimelineSpan
    fk_name = "term"
    extra = 0
    fields = ["title", "start_date", "end_date", "start_fuzzy", "end_fuzzy", "category"]


@admin.register(Term)
class TermAdmin(SortableAdminBase, AdminViewOnLocalSiteMixin, admin.ModelAdmin):
    save_on_top = True

    search_fields = ['title']
    list_display = ('title',  'content_review', 'visual_review', 'seo_review', 'approved')
    list_editable = ('content_review', 'visual_review', 'seo_review',)
    inlines = [InlineTermSource, TimelineEntryFromTermInline, TimelineSpanInline]

    fieldsets = (
        ('Meta / SEO', {
            'fields': ('title', 'description', 'keywords', 'slug', ),
        }),
        ('Article', {
            'fields': ('summary', 'sources',),
        }),
        ('Publishing', {
            'fields': ('content_review', 'visual_review', 'seo_review', 'approved',),
        }),
    )


@admin.register(Source)
class SourceAdmin(AdminViewOnLocalSiteMixin, admin.ModelAdmin):
    save_on_top = True
    search_fields = ['title', 'alt_title']
    filter_horizontal = ('author',)
    list_display = ('__str__',  'authors', 'creative_work_type', 'copyright_year', )
    list_filter = ['creative_work_type',]
    inlines = [TimelineEntryInline]

    def authors(self, obj):
        return ", ".join(o.name for o in obj.author.all())


@admin.register(SourceAuthor)
class SourceAuthorAdmin(AdminViewOnLocalSiteMixin, admin.ModelAdmin):
    save_on_top = True

@admin.register(SourcePublisher)
class SourcePublisherAdmin(AdminViewOnLocalSiteMixin, admin.ModelAdmin):
    save_on_top = True