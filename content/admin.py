from django.contrib import admin

from .models import HomePage, HomeHeroButton

class InlineHomeHeroButton(admin.TabularInline):
    model = HomeHeroButton
    extra = 0


@admin.register(HomePage)
class HomePageAdmin(admin.ModelAdmin):
    save_on_top = True

    inlines = [InlineHomeHeroButton, ]