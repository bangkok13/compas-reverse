from django.contrib import admin
from .models import SiteSettings


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not SiteSettings.objects.exists() and super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        return False

    fieldsets = [
        ("Мастерская", {"fields": ["company_name", "logo", "region"]}),
        ("Главная", {"fields": ["hero_title", "hero_subtitle", "process", "advantages", "business_text"]}),
        ("Контакты", {"fields": ["phone", "email", "telegram", "max_url", "address", "hours", "map_url", "legal_details"]}),
        ("SEO", {"fields": ["seo_title", "seo_description"]}),
        ("Персональные данные", {"fields": ["privacy_text", "consent_text", "consent_version", "legal_reviewed", "accept_leads"]}),
    ]
