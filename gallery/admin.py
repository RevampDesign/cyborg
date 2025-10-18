from django.contrib import admin
from cyborg.mixins import ExportModelCSVMixin, AdminViewOnLocalSiteMixin
from adminsortable2.admin import SortableAdminBase, SortableInlineAdminMixin

from .models import Artwork, WorkDetail, WorkButton, Exhibit, ExhibitWork

@admin.register(Artwork)
class ArtworkAdmin(SortableAdminBase, AdminViewOnLocalSiteMixin, admin.ModelAdmin):
    save_on_top = True
    readonly_fields = ("image_preview",)
    list_display = ('name', 'date_artwork_created', 'image_preview',)

    fieldsets = (
        ('Artwork', {
            'fields': ('name', 'about', 'image', 'date_artwork_created', 'artist', 'image_preview'),
        }),
        ('Schema', {
            'fields': ('art_medium', 'art_edition', 'artform', 'artwork_surface', ),
        }),
        ('Dimensions', {
            'fields': ('dimension_unit', 'height', 'width',)
        }),
    )


class InlineWorkButton(admin.TabularInline):
    model = WorkButton
    extra = 0


@admin.register(WorkDetail)
class WorkDetailAdmin(SortableAdminBase, AdminViewOnLocalSiteMixin, admin.ModelAdmin):
    save_on_top = True
    list_display = ('title',  'content_review', 'visual_review', 'seo_review', 'approved')
    list_editable = ('content_review', 'visual_review', 'seo_review',)

    inlines = [InlineWorkButton, ]


    fieldsets = (
        ('Meta / SEO', {
            'fields': ('title', 'description', 'keywords', 'slug', ),
        }),
        ('Article', {
            'fields': ('artwork', 'body', 'impact',),
        }),
        ('Publishing', {
            'fields': ('content_review', 'visual_review', 'seo_review', 'approved',),
        }),
    )



class InlineExhibitWork(admin.TabularInline):
    model = ExhibitWork
    extra = 0


@admin.register(Exhibit)
class ExhibitAdmin(SortableAdminBase, AdminViewOnLocalSiteMixin, admin.ModelAdmin):
    save_on_top = True
    list_display = ('title',  'content_review', 'visual_review', 'seo_review', 'approved')
    list_editable = ('content_review', 'visual_review', 'seo_review',)

    inlines = [InlineExhibitWork, ]


    fieldsets = (
        ('Meta / SEO', {
            'fields': ('title', 'description', 'keywords', 'slug', ),
        }),
        ('Exhibit Details', {
            'fields': ('name', 'about', 'image', 'start_date', 'end_date',),
        }),
        ('Publishing', {
            'fields': ('content_review', 'visual_review', 'seo_review', 'approved',),
        }),
    )