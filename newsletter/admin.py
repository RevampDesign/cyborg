from django.contrib import admin, messages
from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
from django.template.response import TemplateResponse
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import path
from .models import Newsletter
from recommendation.models import RecommendedLink
from cyborg.mixins import ExportModelCSVMixin, AdminViewOnLocalSiteMixin
from .forms import NewsletterForm, ConfirmURLCleanupForm
from .utils import clean_absolute_urls

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


def cleanup_urls(self, request, queryset):
    """
    Admin action to clean absolute URLs to relative URLs in the body field.
    Includes a preview/confirmation step.
    """
    
    # Check if the user is confirming the action (POST request with 'confirm' in data)
    if 'confirm' in request.POST:
        # Handle the confirmation and actual cleanup
        form = ConfirmURLCleanupForm(request.POST)
        
        if form.is_valid():
            # Perform the cleanup on all selected objects
            count = 0
            for newsletter in queryset:
                # Clean the content and ignore the matches list here
                cleaned_content, _ = clean_absolute_urls(newsletter.body)
                
                if cleaned_content != newsletter.body:
                    # Only save if something changed
                    newsletter.body = cleaned_content
                    newsletter.save()
                    count += 1

            self.message_user(
                request,
                f"Successfully cleaned URLs in {count} newsletter(s).",
                messages.SUCCESS
            )
            # Redirect back to the change list page
            return HttpResponseRedirect(request.get_full_path())
        else:
            # If form is invalid but it was a POST, show error (shouldn't happen often)
            self.message_user(request, "Confirmation failed.", messages.ERROR)
            return HttpResponseRedirect(request.get_full_path())


    # 2. Handle the initial action call (GET or POST without confirmation)
    
    # Collect all matches to display in the preview
    all_matches = {}
    for newsletter in queryset:
        _, matches = clean_absolute_urls(newsletter.body)
        if matches:
            all_matches[newsletter.pk] = {
                'title': newsletter.title,
                'matches': matches
            }
    
    if not all_matches:
        self.message_user(
            request,
            "No absolute domain links were found in the selected newsletters. Nothing to clean.",
            messages.WARNING
        )
        return HttpResponseRedirect(request.get_full_path())

    # Pre-populate the form with necessary hidden fields
    # Note: You need to pass the selected object IDs so they are preserved
    initial = {
        '_selected_action': request.POST.getlist(ACTION_CHECKBOX_NAME), 
        'action': 'cleanup_urls',
    }
    form = ConfirmURLCleanupForm(initial=initial)

    # 3. Render the confirmation template
    return render(
        request,
        'newsletter/admin/confirm_url_cleanup.html',
        context={
            'title': "Confirm URL Cleanup Action",
            'queryset': queryset,
            'form': form,
            'all_matches': all_matches,
            'newsletter_count': len(queryset),
            'action_name': 'cleanup_urls',
            'media': self.media, # Essential for the admin change form
        }
    )
    
cleanup_urls.short_description = "Cleanup absolute domain URLs to relative URLs"


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
    convert_em_to_cite, cleanup_urls,]
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