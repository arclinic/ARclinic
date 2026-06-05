from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/auth/", include("config.auth_urls")),
    path("api/v1/marketing/", include("marketing.urls")),
    path("api/v1/management/", include("management.urls")),
    path("api/v1/contact-center/", include("contact_center.urls")),
    path("api/v1/accounting/", include("accounting.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
