from django.contrib import admin
from cyborg.mixins import ExportModelCSVMixin, AdminViewOnLocalSiteMixin

from .models import HomePage, HomeHeroButton

class InlineHomeHeroButton(admin.TabularInline):
    model = HomeHeroButton
    extra = 0


@admin.register(HomePage)
class HomePageAdmin(AdminViewOnLocalSiteMixin, admin.ModelAdmin):
    save_on_top = True

    inlines = [InlineHomeHeroButton, ]