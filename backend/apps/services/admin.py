from django.contrib import admin
from .models import Service, FAQ


class FAQInline(admin.TabularInline):
    model = FAQ
    extra = 1


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ["title", "is_active", "sort_order"]
    list_editable = ["is_active", "sort_order"]
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ["materials"]
    inlines = [FAQInline]
