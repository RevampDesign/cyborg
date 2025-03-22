from django.contrib import admin
from .models import Newsletter
from cyborg.mixins import ExportModelCSVMixin

@admin.register(Newsletter)
class NewsletterAdmin(ExportModelCSVMixin, admin.ModelAdmin):
    save_on_top = True
    list_display = ('title', 'publish_date_only', 'content_review', 'visual_review', 'seo_review', 'approved')
    list_editable = ('content_review', 'visual_review', 'seo_review',)

    actions = ['export_urls_as_csv',]

    fieldsets = (
        ('Meta / SEO', {
            'fields': ('title', 'description', 'keywords', 'slug', 'author',),
        }),
        ('Article', {
            'fields': ('body',),
        }),
        ('Publishing', {
            'fields': ('publish_date', 'content_review', 'visual_review', 'seo_review', 'approved',),
        }),
    )