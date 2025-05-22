from django.contrib import admin
from .models import Newsletter
from cyborg.mixins import ExportModelCSVMixin, AdminViewOnLocalSiteMixin


@admin.register(Newsletter)
class NewsletterAdmin(ExportModelCSVMixin, AdminViewOnLocalSiteMixin, admin.ModelAdmin):
    save_on_top = True
    list_display = ('title', 'tag_list', 'publish_date_only', 'content_review', 'visual_review', 'seo_review', 'approved')
    list_editable = ('content_review', 'visual_review', 'seo_review',)

    actions = ['export_urls_as_csv',]

    fieldsets = (
        ('Meta / SEO', {
            'fields': ('title', 'description', 'keywords', 'slug', 'author',),
        }),
        ('Article', {
            'fields': ('body', 'tags', ),
        }),
        ('Publishing', {
            'fields': ('publish_date', 'content_review', 'visual_review', 'seo_review', 'approved',),
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('tags')

    def tag_list(self, obj):
        return u", ".join(o.name for o in obj.tags.all())