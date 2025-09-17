from django.contrib import admin
from django.template.response import TemplateResponse
from django.urls import path
from .models import Newsletter
from recommendation.models import RecommendedLink
from cyborg.mixins import ExportModelCSVMixin, AdminViewOnLocalSiteMixin
from .forms import NewsletterForm

import re
from django.utils.html import format_html

def convert_em_to_cite(modeladmin, request, queryset):
    """
    Admin action to convert <em> tags with capitalized words to <cite>.
    """
    if 'apply' in request.POST:
        # The logic to save the changes remains the same
        for obj in queryset:
            body = obj.body
            matches = re.findall(r'(<em>[^<]*[A-Z][^<]*</em>)', body)
            for match in matches:
                cite_tag = match.replace('<em>', '<cite>').replace('</em>', '</cite>')
                body = body.replace(match, cite_tag, 1)
            obj.body = body
            obj.save()
        
        modeladmin.message_user(request, f"Successfully converted <em> to <cite> for {queryset.count()} objects.")
        return

    # Prepare data for the confirmation template
    items_to_confirm = []
    for obj in queryset:
        matches = re.findall(r'(<em>[^<]*[A-Z][^<]*</em>)', obj.body)
        if matches:
            items_to_confirm.append({
                'object': obj,
                'matches': [format_html(match) for match in matches],
            })

    context = {
        'items_to_confirm': items_to_confirm,
        'queryset': queryset,
        'action_name': 'convert_em_to_cite',
    }
            
    return TemplateResponse(request, 'newsletter/admin/confirm_em_to_cite.html', context)

convert_em_to_cite.short_description = "Convert <em> to <cite> tags for selected items"



class InlineGLossaryLink(admin.TabularInline):
    model = RecommendedLink
    extra = 0

@admin.register(Newsletter)
class NewsletterAdmin(ExportModelCSVMixin, AdminViewOnLocalSiteMixin, admin.ModelAdmin):
    save_on_top = True
    list_display = ('title', 'tag_list', 'publish_date_only', 'content_review', 'visual_review', 'seo_review', 'approved')
    list_editable = ('content_review', 'visual_review', 'seo_review',)
    search_fields = ('title', 'body',)

    inlines = (InlineGLossaryLink,)
    actions = ['export_urls_as_csv', 
    convert_em_to_cite, ]
    form = NewsletterForm

    fieldsets = (
        ('Meta / SEO', {
            'fields': ('title', 'description', 'keywords', 'slug', 'author', 'noindex_nofollow'),
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