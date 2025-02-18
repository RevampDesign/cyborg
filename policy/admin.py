from django.contrib import admin
from .models import Policy

@admin.register(Policy)
class PolicyAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = ('title',  'content_review', 'visual_review', 'seo_review', 'approved')
    list_editable = ('content_review', 'visual_review', 'seo_review',)


    fieldsets = (
        ('Meta / SEO', {
            'fields': ('title', 'description', 'keywords', 'slug', ),
        }),
        ('Article', {
            'fields': ('body',),
        }),
        ('Publishing', {
            'fields': ('publish_date', 'content_review', 'visual_review', 'seo_review', 'approved',),
        }),
    )