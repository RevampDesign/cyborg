from django.contrib import admin
from cyborg.mixins import ExportModelCSVMixin, AdminViewOnLocalSiteMixin
from adminsortable2.admin import SortableAdminBase, SortableInlineAdminMixin

from .models import Term, Source, SourceAuthor, TermSource

class InlineTermSource(SortableInlineAdminMixin, admin.TabularInline):
    model = TermSource
    extra = 0

@admin.register(Term)
class TermAdmin(SortableAdminBase, AdminViewOnLocalSiteMixin, admin.ModelAdmin):
    save_on_top = True
    list_display = ('title',  'content_review', 'visual_review', 'seo_review', 'approved')
    list_editable = ('content_review', 'visual_review', 'seo_review',)

    inlines = [InlineTermSource,]

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
    filter_horizontal = ('author',)


@admin.register(SourceAuthor)
class SourceAuthorAdmin(AdminViewOnLocalSiteMixin, admin.ModelAdmin):
    save_on_top = True