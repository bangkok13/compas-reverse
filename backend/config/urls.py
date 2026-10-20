from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from apps.core.api import (
    ProjectViewSet, CategoryViewSet, ServiceViewSet, MaterialViewSet,
    site_settings, csrf, health, project_model,
)
from apps.leads.api import LeadCreateView, download_attachment

admin.site.site_header = "3D-мастерская · Управление"
admin.site.site_title = "Мастерская"
admin.site.index_title = "Проекты, контент и заявки"
router = DefaultRouter()
router.register("projects", ProjectViewSet, basename="project")
router.register("categories", CategoryViewSet)
router.register("services", ServiceViewSet)
router.register("materials", MaterialViewSet)
urlpatterns = [
    path("admin/attachments/<int:pk>/download/", admin.site.admin_view(download_attachment), name="attachment-download"),
    path("admin/", admin.site.urls),
    path("api/settings/", site_settings),
    path("api/csrf/", csrf),
    path("api/health/", health),
    path("api/leads/", LeadCreateView.as_view()),
    path("api/projects/<slug:slug>/model/", project_model),
    path("api/", include(router.urls)),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
