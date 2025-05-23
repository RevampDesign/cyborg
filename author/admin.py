from django.contrib import admin
from cyborg.mixins import AdminViewOnLocalSiteMixin

from .models import Author

@admin.register(Author)
class AuthorAdmin(AdminViewOnLocalSiteMixin, admin.ModelAdmin):
    save_on_top = True