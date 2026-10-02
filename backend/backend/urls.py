from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),

    # Hotel + Job API
    path("api/", include("hotel.urls")),
]