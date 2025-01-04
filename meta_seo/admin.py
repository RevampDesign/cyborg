from django.contrib import admin

class MetaSEOAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Meta / SEO', {
            'fields': ('title', 'description', 'keywords', 'slug', 'social_media_image', 'noindex_nofollow')
        }),
    )
