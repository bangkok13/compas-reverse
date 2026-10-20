import hashlib
import json
import re
from datetime import timedelta
from pathlib import Path
from django.conf import settings
from django.core.exceptions import ValidationError as DjangoValidationError, PermissionDenied
from django.db import transaction, IntegrityError
from django.db.models import F
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.crypto import salted_hmac
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from rest_framework import serializers, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.core.models import RateWindow
from apps.core.validators import validate_attachment
from apps.services.models import Service
from apps.site_settings.models import SiteSettings
from .models import Lead, LeadAttachment, Notification


class LeadSerializer(serializers.ModelSerializer):
    idempotency_key = serializers.UUIDField()
    consent = serializers.BooleanField(required=True)
    consent_version = serializers.CharField(max_length=40)
    website = serializers.CharField(required=False, allow_blank=True, write_only=True)
    service = serializers.PrimaryKeyRelatedField(queryset=Service.objects.filter(is_active=True), required=False, allow_null=True)

    class Meta:
        model = Lead
        fields = ["idempotency_key", "name", "phone", "email", "service", "description",
                  "dimensions", "quantity", "material", "deadline", "consent", "consent_version", "website"]
        extra_kwargs = {
            "description": {"max_length": 10000, "min_length": 10},
            "quantity": {"min_value": 1, "max_value": 100000},
            "name": {"min_length": 2},
        }

    def validate_phone(self, value):
        digits = re.sub(r"\D", "", value)
        if not 10 <= len(digits) <= 15:
            raise serializers.ValidationError("Укажите телефон, включая код города или страны.")
        return value

    def validate_consent(self, value):
        if not value:
            raise serializers.ValidationError("Необходимо согласие на обработку персональных данных.")
        return value

    def validate_deadline(self, value):
        if value and value < timezone.localdate():
            raise serializers.ValidationError("Выберите сегодняшнюю или будущую дату.")
        return value


def allow_request(request):
    # Only the trusted Nginx proxy may set X-Real-IP. Backend port is private in Compose.
    ip = request.META.get("HTTP_X_REAL_IP") or request.META.get("REMOTE_ADDR", "")
    key = salted_hmac("lead-rate", ip).hexdigest()
    now = timezone.now()
    with transaction.atomic():
        window, _ = RateWindow.objects.get_or_create(key=key, defaults={"starts_at": now})
        window = RateWindow.objects.select_for_update().get(pk=window.pk)
        if window.starts_at < now - timedelta(hours=1):
            window.starts_at, window.count = now, 0
        if window.count >= 10:
            return False
        window.count += 1
        window.save()
    return True


@method_decorator(csrf_protect, name="dispatch")
class LeadCreateView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        if not allow_request(request):
            return Response({"detail": "Слишком много обращений. Попробуйте через час."}, status=429, headers={"Retry-After": "3600"})
        config, _ = SiteSettings.objects.get_or_create(pk=1)
        if not config.accept_leads or (not settings.DEBUG and not config.legal_reviewed):
            return Response({"detail": "Приём заявок временно приостановлен."}, status=503)
        serializer = LeadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        if data.pop("consent_version") != config.consent_version:
            return Response({"detail": "Текст согласия обновился. Обновите страницу и ознакомьтесь с новой версией."}, status=400)
        if data.pop("website", ""):
            return Response({"detail": "Не удалось отправить заявку."}, status=400)
        files = request.FILES.getlist("files")
        if len(files) > 8 or sum(f.size for f in files) > settings.MAX_TOTAL_UPLOAD:
            return Response({"files": ["Не более 8 файлов и 50 МБ суммарно."]}, status=400)
        digest = hashlib.sha256(json.dumps(
            {k: str(v.pk if hasattr(v, "pk") else v) for k, v in data.items()}, sort_keys=True,
        ).encode())
        try:
            for file in files:
                validate_attachment(file)
                digest.update(file.name.encode())
                for chunk in file.chunks():
                    digest.update(chunk)
                file.seek(0)
        except DjangoValidationError as exc:
            return Response({"files": exc.messages}, status=400)
        payload_hash = digest.hexdigest()
        existing = Lead.objects.filter(idempotency_key=data["idempotency_key"]).first()
        if existing:
            return self.replay(existing, payload_hash)
        stored = []
        try:
            with transaction.atomic():
                lead = Lead.objects.create(**data, consent_version=config.consent_version, payload_hash=payload_hash)
                for file in files:
                    attachment = LeadAttachment(
                        lead=lead, file=file, original_name=Path(file.name).name[:250], size=file.size,
                    )
                    stored.append(attachment.file)
                    attachment.save()
                Notification.objects.create(lead=lead, next_attempt_at=timezone.now())
        except IntegrityError:
            for file in stored:
                if file._committed:
                    file.delete(save=False)
            existing = Lead.objects.filter(idempotency_key=data["idempotency_key"]).first()
            if existing:
                return self.replay(existing, payload_hash)
            raise
        except Exception:
            for file in stored:
                if file._committed:
                    file.delete(save=False)
            raise
        return Response({"reference": str(lead)}, status=status.HTTP_201_CREATED, headers={"Cache-Control": "no-store"})

    def replay(self, lead, payload_hash):
        if lead.payload_hash != payload_hash:
            return Response({"detail": "Эта отправка уже обработана с другими данными. Начните новую заявку."}, status=409)
        return Response({"reference": str(lead)}, headers={"Cache-Control": "no-store"})


def download_attachment(request, pk):
    if not request.user.is_active or not request.user.is_staff or not request.user.has_perm("leads.view_leadattachment"):
        raise PermissionDenied
    attachment = get_object_or_404(LeadAttachment, pk=pk)
    response = FileResponse(attachment.file.open("rb"), as_attachment=True,
                            filename=attachment.original_name, content_type="application/octet-stream")
    response["Cache-Control"] = "private, no-store"
    return response
