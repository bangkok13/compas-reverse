from django.db import connection
from django.http import JsonResponse, FileResponse, Http404
from django.middleware.csrf import get_token
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import ensure_csrf_cookie
from django.shortcuts import get_object_or_404
from rest_framework import serializers, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from apps.materials.models import Material
from apps.services.models import Service, FAQ
from apps.portfolio.models import Project, Category, ProjectImage
from apps.site_settings.models import SiteSettings


class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = "__all__"


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = ["question", "answer"]


class ServiceSerializer(serializers.ModelSerializer):
    materials = serializers.SerializerMethodField()
    faq = FAQSerializer(many=True, read_only=True)

    def get_materials(self, obj):
        return MaterialSerializer([m for m in obj.materials.all() if m.is_active], many=True).data

    class Meta:
        model = Service
        fields = "__all__"


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectImage
        fields = ["id", "image", "thumbnail", "caption", "role", "sort_order"]


class ProjectSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    material = serializers.SerializerMethodField()

    def get_material(self, obj):
        return MaterialSerializer(obj.material).data if obj.material and obj.material.is_active else None

    class Meta:
        model = Project
        fields = ["id", "title", "slug", "summary", "category", "material", "technology",
                  "cover", "thumbnail", "completed_at", "is_demo", "featured", "updated_at"]


class ProjectDetailSerializer(ProjectSerializer):
    images = ImageSerializer(many=True, read_only=True)
    model_url = serializers.SerializerMethodField()
    model_format = serializers.SerializerMethodField()
    services = serializers.SerializerMethodField()

    def get_model_url(self, obj):
        return f"/api/projects/{obj.slug}/model/" if obj.viewer_enabled and obj.model_file else None

    def get_model_format(self, obj):
        return obj.model_file.name.rsplit(".", 1)[-1] if obj.viewer_enabled and obj.model_file else None

    def get_services(self, obj):
        return ServiceSerializer([s for s in obj.services.all() if s.is_active], many=True).data

    class Meta(ProjectSerializer.Meta):
        fields = ProjectSerializer.Meta.fields + [
            "description", "problem", "solution", "result", "video_url", "images", "model_url",
            "model_format", "services", "seo_title", "seo_description",
        ]


class ProjectViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = "slug"

    def get_serializer_context(self):
        return {"view": self, "format": self.format_kwarg}

    def get_serializer_class(self):
        return ProjectDetailSerializer if self.action == "retrieve" else ProjectSerializer

    def get_queryset(self):
        qs = Project.objects.filter(status=Project.Status.PUBLISHED).select_related("category", "material").prefetch_related("images", "services__faq", "services__materials")
        for param, field in [("category", "category__slug"), ("material", "material__slug"), ("service", "services__slug")]:
            value = self.request.query_params.get(param)
            if value:
                qs = qs.filter(**{field: value})
        if self.request.query_params.get("featured") == "true":
            qs = qs.filter(featured=True)
        search = self.request.query_params.get("search", "").strip()[:100]
        if search:
            from django.db.models import Q
            qs = qs.filter(Q(title__icontains=search) | Q(summary__icontains=search))
        return qs.distinct()


class MaterialViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Material.objects.filter(is_active=True)
    serializer_class = MaterialSerializer
    lookup_field = "slug"
    pagination_class = None


class ServiceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Service.objects.filter(is_active=True).prefetch_related("materials", "faq")
    serializer_class = ServiceSerializer
    lookup_field = "slug"
    pagination_class = None


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = None


class SettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteSettings
        fields = "__all__"


@api_view(["GET"])
def site_settings(request):
    obj, _ = SiteSettings.objects.get_or_create(pk=1)
    data = SettingsSerializer(obj).data
    from django.conf import settings
    data["accept_leads"] = obj.accept_leads and (settings.DEBUG or obj.legal_reviewed)
    return Response(data)


@ensure_csrf_cookie
@never_cache
def csrf(request):
    return JsonResponse({"csrfToken": get_token(request)})


def health(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return JsonResponse({"status": "ok"})
    except Exception:
        return JsonResponse({"status": "unavailable"}, status=503)


def project_model(request, slug):
    obj = get_object_or_404(Project, slug=slug, status=Project.Status.PUBLISHED, viewer_enabled=True)
    if not obj.model_file:
        raise Http404
    response = FileResponse(obj.model_file.open("rb"), content_type="application/octet-stream")
    response["Cache-Control"] = "private, no-store"
    response["X-Content-Type-Options"] = "nosniff"
    return response
