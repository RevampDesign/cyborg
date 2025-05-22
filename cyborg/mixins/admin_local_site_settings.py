from django.conf import settings
from django.contrib import admin
from django.contrib.sites.models import Site
from django.urls import NoReverseMatch
from django.utils.http import urlparse

class AdminViewOnLocalSiteMixin(admin.ModelAdmin):
    """ This should allow django-distill to use the correct prod. settings for output like sitemaps, but since the admin is local-only, the mixin makes the view on site buttons use the local Site ID for convenience """

    # Ensure the "View on site" button is enabled.
    # This is often True by default if get_absolute_url is defined on the model.
    view_on_site = True

    def get_view_on_site_url(self, obj=None):
        if obj is None or not hasattr(obj, 'get_absolute_url'):
            return None

        try:
            # Fetch the Site object for SITE_ID = 1
            site_1 = Site.objects.get(pk=1) # Or use a configurable setting
            path = obj.get_absolute_url()

            # Determine the scheme (http/https)
            # You can make this configurable, e.g., via settings.py
            # Default to 'http' for local development.
            scheme = getattr(settings, 'ADMIN_SITE_1_SCHEME', 'http')
            domain = site_1.domain

            # Ensure the domain does not already contain a scheme for concatenation
            parsed_domain = urlparse(f'//{domain}') # Use // to allow urlparse to correctly identify netloc
            actual_domain = parsed_domain.netloc or parsed_domain.path # Handle cases where domain might be just 'localhost'

            final_url = f"{scheme}://{actual_domain}{path}"
            return final_url

        except Site.DoesNotExist:
            # Log this issue or handle as desired
            print(f"Warning: Site with ID 1 not found. Cannot generate admin 'View on site' link for {obj}.")
            return None # Fallback to no link or default behavior if appropriate
        except NoReverseMatch:
            print(f"Warning: NoReverseMatch for {obj} when generating admin 'View on site' link.")
            return None
        except Exception as e:
            print(f"Error generating view on site URL for {obj}: {e}")
            return None