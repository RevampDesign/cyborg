from django.contrib import admin
from cyborg.mixins import ExportModelCSVMixin, AdminViewOnLocalSiteMixin
from adminsortable2.admin import SortableAdminBase, SortableInlineAdminMixin

from .models import Term, Source, SourceAuthor, SourcePublisher, TermSource

class InlineTermSource(SortableInlineAdminMixin, admin.TabularInline):
    model = TermSource
    extra = 0

@admin.register(Term)
class TermAdmin(SortableAdminBase, AdminViewOnLocalSiteMixin, admin.ModelAdmin):
    save_on_top = True
    
    search_fields = ['title']
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
    search_fields = ['title', 'alt_title']
    filter_horizontal = ('author',)
    list_display = ('__str__',  'authors', 'creative_work_type', 'date_published', )
    list_filter = ['creative_work_type',]

    def authors(self, obj):
        return ", ".join(o.name for o in obj.author.all())


@admin.register(SourceAuthor)
class SourceAuthorAdmin(AdminViewOnLocalSiteMixin, admin.ModelAdmin):
    save_on_top = True

@admin.register(SourcePublisher)
class SourcePublisherAdmin(AdminViewOnLocalSiteMixin, admin.ModelAdmin):
    save_on_top = True