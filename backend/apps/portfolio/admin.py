from django import forms
from django.contrib import admin
from django.utils.html import format_html
from apps.core.validators import validate_image
from .models import Category, Project, ProjectImage


class MultipleInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleImages(forms.FileField):
    widget = MultipleInput

    def clean(self, data, initial=None):
        files = data if isinstance(data, (list, tuple)) else [data] if data else []
        if len(files) > 20:
            raise forms.ValidationError("За один раз можно загрузить до 20 фотографий.")
        for file in files:
            super().clean(file, initial)
            validate_image(file)
        return files


class ProjectForm(forms.ModelForm):
    upload_images = MultipleImages(label="Добавить несколько фотографий", required=False)

    class Meta:
        model = Project
        fields = "__all__"
        widgets = {"model_file": forms.FileInput()}


class ImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 0
    fields = ["preview", "image", "caption", "role", "sort_order"]
    readonly_fields = ["preview"]

    def preview(self, obj):
        if obj.thumbnail:
            return format_html('<img src="{}" width="100" alt="">', obj.thumbnail.url)
        return "—"


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    form = ProjectForm
    list_display = ["title", "category", "status", "featured", "is_demo", "sort_order"]
    list_filter = ["status", "category", "featured", "is_demo"]
    list_editable = ["status", "featured", "sort_order"]
    search_fields = ["title", "summary"]
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ["services"]
    inlines = [ImageInline]
    actions = ["publish", "hide"]
    save_on_top = True
    fieldsets = [
        ("Основное", {"fields": ["title", "slug", "category", "status", "featured", "is_demo", "sort_order"]}),
        ("Содержание", {"fields": ["summary", "description", "problem", "solution", "result"]}),
        ("Технологии", {"fields": ["material", "technology", "services", "completed_at"]}),
        ("Файлы", {"fields": ["cover", "upload_images", "video_url", "model_file", "viewer_enabled"]}),
        ("Поисковая оптимизация", {"fields": ["seo_title", "seo_description"], "classes": ["collapse"]}),
    ]

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        offset = form.instance.images.count()
        for i, file in enumerate(form.cleaned_data.get("upload_images", [])):
            ProjectImage.objects.create(project=form.instance, image=file, sort_order=offset + i)

    @admin.action(description="Опубликовать выбранные проекты")
    def publish(self, request, queryset):
        queryset.update(status=Project.Status.PUBLISHED)

    @admin.action(description="Скрыть выбранные проекты")
    def hide(self, request, queryset):
        queryset.update(status=Project.Status.DRAFT)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "sort_order"]
    list_editable = ["sort_order"]
    prepopulated_fields = {"slug": ("name",)}
