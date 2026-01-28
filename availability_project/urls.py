"""
URL configuration for availability_project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('availability.urls')),
    path('api/', include('availability.api_urls')),
]