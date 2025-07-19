from django.contrib import admin
from cyborg.mixins import ExportModelCSVMixin, AdminViewOnLocalSiteMixin

from .models import Term

@admin.register(Term)
class TermAdmin(AdminViewOnLocalSiteMixin, admin.ModelAdmin):
    save_on_top = True
    list_display = ('title',  'content_review', 'visual_review', 'seo_review', 'approved')
    list_editable = ('content_review', 'visual_review', 'seo_review',)


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