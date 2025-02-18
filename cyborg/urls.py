"""
URL configuration for cyborg project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django_distill import distill_path

from content.views import homePage

urlpatterns = [
    distill_path('', homePage, name="homePage"),
    distill_path('subscribe/', TemplateView.as_view(template_name='content/subscribe.html'), name='subscribe'),
    path('newsletters/', include('newsletter.urls')),
    path('policies/', include('policy.urls')),
    path('machina/', admin.site.urls),
]
