from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import Lead, LeadAttachment, Notification


class AttachmentInline(admin.TabularInline):
    model = LeadAttachment
    fields = ["download", "size"]
    readonly_fields = fields
    extra = 0
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

    def download(self, obj):
        return format_html('<a href="{}">{}</a>', reverse("attachment-download", args=[obj.pk]), obj.original_name)


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ["reference", "name", "service", "status", "created_at"]
    list_filter = ["status", "service", "created_at"]
    search_fields = ["name", "phone", "email", "reference"]
    list_editable = ["status"]
    readonly_fields = [
        "reference", "created_at", "consent", "consent_version", "name", "phone", "email",
        "service", "description", "dimensions", "quantity", "material", "deadline",
    ]
    exclude = ["idempotency_key", "payload_hash"]
    inlines = [AttachmentInline]

    def has_add_permission(self, request):
        return False


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ["lead", "attempts", "completed", "email_sent_at", "telegram_sent_at", "next_attempt_at"]
    readonly_fields = ["lead", "attempts", "email_sent_at", "telegram_sent_at"]

    def has_add_permission(self, request):
        return False
