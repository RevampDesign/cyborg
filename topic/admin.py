from django.contrib import admin
from .models import Topic
from cyborg.mixins import ExportModelCSVMixin
from adminsortable2.admin import SortableAdminMixin

@admin.register(Topic)
class TopicAdmin(SortableAdminMixin, ExportModelCSVMixin, admin.ModelAdmin):
    save_on_top = True
    list_display = ('title', 'content_review', 'visual_review', 'seo_review', 'approved')
    list_editable = ('content_review', 'visual_review', 'seo_review',)

    actions = ['export_urls_as_csv',]

    fieldsets = (
        ('Meta / SEO', {
            'fields': ('title', 'description', 'keywords', 'slug',),
        }),
        ('Mini-Essay', {
            'fields': ('body',),
        }),
        ('Publishing', {
            'fields': ('content_review', 'visual_review', 'seo_review', 'approved',),
        }),
    )