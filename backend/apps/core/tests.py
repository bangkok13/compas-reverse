import io
import json
import tempfile
import uuid
import zipfile
from pathlib import Path
from unittest.mock import patch
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.exceptions import ValidationError
from django.core.files.storage import FileSystemStorage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.utils import timezone
from PIL import Image
from apps.core.validators import validate_attachment
from apps.core.models import RateWindow
from apps.leads.models import Lead, LeadAttachment, Notification
from apps.materials.models import Material
from apps.portfolio.models import Category, Project, ProjectImage
from apps.services.models import Service
from apps.site_settings.models import SiteSettings


def photo(name="sample.png"):
    stream = io.BytesIO()
    Image.new("RGB", (90, 70), "#3978f6").save(stream, "PNG")
    return SimpleUploadedFile(name, stream.getvalue(), content_type="image/png")


@override_settings(DEBUG=True, SECURE_SSL_REDIRECT=False)
class WorkshopTests(TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.media_override = override_settings(MEDIA_ROOT=Path(self.directory.name) / "public")
        self.media_override.enable()
        self.private_fields = [LeadAttachment._meta.get_field("file"), Project._meta.get_field("model_file")]
        self.old_storages = [field.storage for field in self.private_fields]
        for field in self.private_fields:
            field.storage = FileSystemStorage(location=Path(self.directory.name) / "private")
        self.config = SiteSettings.objects.create()
        self.category = Category.objects.create(name="Оборудование", slug="equipment")
        self.service = Service.objects.create(title="Печать", slug="3d-printing", summary="Печать деталей", description="Описание")
        self.client = Client(enforce_csrf_checks=True)

    def tearDown(self):
        for field, storage in zip(self.private_fields, self.old_storages):
            field.storage = storage
        self.media_override.disable()
        self.directory.cleanup()

    def payload(self, **kwargs):
        return dict(name="Тестовый заказчик", phone="+7 999 000 00 00",
                    description="Нужен тестовый корпус для проекта", consent="true",
                    consent_version=self.config.consent_version,
                    idempotency_key=str(uuid.uuid4()), **kwargs)

    def post_lead(self, data):
        token = self.client.get("/api/csrf/").json()["csrfToken"]
        return self.client.post("/api/leads/", data, HTTP_X_CSRFTOKEN=token)

    def test_lead_files_private_and_idempotent(self):
        data = self.payload(files=[photo()])
        response = self.post_lead(data)
        self.assertEqual(response.status_code, 201, response.content)
        self.assertTrue(response.json()["reference"].startswith("3D-"))
        self.assertEqual(Lead.objects.count(), 1)
        self.assertEqual(Notification.objects.count(), 1)
        attachment = LeadAttachment.objects.get()
        self.assertTrue(attachment.file.storage.exists(attachment.file.name))
        self.assertNotIn("file", response.json())
        data["files"] = [photo()]
        repeated = self.post_lead(data)
        self.assertEqual(repeated.status_code, 200)
        self.assertEqual(repeated.json(), response.json())
        self.assertEqual(Lead.objects.count(), 1)
        data["description"] = "Изменённые данные той же отправки"
        data["files"] = [photo()]
        self.assertEqual(self.post_lead(data).status_code, 409)
        self.assertEqual(self.client.get(reverse("attachment-download", args=[attachment.pk])).status_code, 302)
        self.assertEqual(self.client.get("/api/leads/").status_code, 405)

    def test_csrf_consent_validation_and_honeypot(self):
        self.assertEqual(self.client.post("/api/leads/", self.payload()).status_code, 403)
        data = self.payload()
        del data["consent"]
        self.assertEqual(self.post_lead(data).status_code, 400)
        data["consent"] = "false"
        self.assertEqual(self.post_lead(data).status_code, 400)
        data["consent"] = "true"
        data["phone"] = "123"
        self.assertEqual(self.post_lead(data).status_code, 400)
        data["phone"] = "+79990000000"
        data["website"] = "spam"
        self.assertEqual(self.post_lead(data).status_code, 400)
        self.assertEqual(Lead.objects.count(), 0)

    def test_invalid_upload_rolls_back_entire_submission(self):
        self.assertEqual(self.post_lead(self.payload(files=[photo(), SimpleUploadedFile("fake.png", b"not an image")])).status_code, 400)
        self.assertEqual(Lead.objects.count(), 0)
        self.assertEqual(LeadAttachment.objects.count(), 0)
        self.assertEqual(self.post_lead(self.payload(files=[photo(f"file-{i}.png") for i in range(9)])).status_code, 400)

    def test_rate_limit_shared_by_requests(self):
        for _ in range(10):
            response = self.post_lead(self.payload())
            self.assertEqual(response.status_code, 201)
        response = self.post_lead(self.payload())
        self.assertEqual(response.status_code, 429)
        self.assertEqual(response["Retry-After"], "3600")

    def test_publication_draft_filtering_and_pagination(self):
        project = Project.objects.create(title="Скрытый проект", slug="hidden", category=self.category, summary="Образец")
        self.assertEqual(self.client.get("/api/projects/").json()["count"], 0)
        self.assertEqual(self.client.get("/api/projects/hidden/").status_code, 404)
        project.status = "published"
        project.save()
        self.assertEqual(self.client.get("/api/projects/hidden/").status_code, 200)
        self.assertEqual(self.client.get("/api/projects/?category=equipment").json()["count"], 1)
        self.assertEqual(self.client.get("/api/projects/?category=other").json()["count"], 0)
        self.assertEqual(self.client.get("/api/projects/?search=Скрытый").json()["count"], 1)
        for i in range(15):
            Project.objects.create(title=f"Проект {i}", slug=f"project-{i}", category=self.category, summary="Образец", status="published")
        data = self.client.get("/api/projects/").json()
        self.assertEqual(len(data["results"]), 12)
        self.assertEqual(len(self.client.get("/api/projects/?page=2").json()["results"]), 4)

    def test_disabled_material_and_service_hidden(self):
        self.service.is_active = False
        self.service.save()
        self.assertEqual(self.client.get("/api/services/").json(), [])
        self.assertEqual(self.client.get("/api/services/3d-printing/").status_code, 404)
        Material.objects.create(name="PETG", slug="petg", description="Test", is_active=False)
        self.assertEqual(self.client.get("/api/materials/").json(), [])

    def test_admin_publish_multiple_images_and_thumbnails(self):
        user = get_user_model().objects.create_superuser("owner", "test@example.test", "testing-only-password")
        admin = Client()
        admin.force_login(user)
        response = admin.post("/admin/portfolio/project/add/", {
            "title": "Новая деталь", "slug": "new-part", "category": self.category.pk,
            "summary": "Создано через административный интерфейс", "status": "published",
            "featured": "on", "sort_order": 0, "cover": photo("cover.png"),
            "upload_images": [photo("first.png"), photo("second.png")],
            "images-TOTAL_FORMS": "0", "images-INITIAL_FORMS": "0",
            "images-MIN_NUM_FORMS": "0", "images-MAX_NUM_FORMS": "1000", "_save": "Сохранить",
        })
        self.assertEqual(response.status_code, 302, response.context and response.context.get("adminform").form.errors)
        project = Project.objects.get(slug="new-part")
        self.assertEqual(project.images.count(), 2)
        self.assertTrue(project.thumbnail.name.endswith(".webp"))
        self.assertTrue(all(image.thumbnail for image in project.images.all()))
        api = self.client.get("/api/projects/new-part/").json()
        self.assertEqual(len(api["images"]), 2)
        self.assertTrue(api["cover"].startswith("/media/"))
        self.assertEqual(admin.get(f"/admin/portfolio/project/{project.pk}/change/").status_code, 200)

    def test_model_is_opt_in_and_not_listed(self):
        model = b"solid demo\nfacet normal 0 0 1\nouter loop\nvertex 0 0 0\nvertex 1 0 0\nvertex 0 1 0\nendloop\nendfacet\nendsolid demo"
        project = Project.objects.create(title="Модель", slug="model", category=self.category, summary="Пример", status="published",
                                         model_file=SimpleUploadedFile("demo.stl", model))
        self.assertEqual(self.client.get("/api/projects/model/model/").status_code, 404)
        project.viewer_enabled = True
        project.save()
        response = self.client.get("/api/projects/model/model/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(b"".join(response.streaming_content), model)
        self.assertNotIn("model_file", self.client.get("/api/projects/model/").json())
        self.assertNotIn("model_url", self.client.get("/api/projects/").json()["results"][0])
        project.status = "draft"
        project.save()
        self.assertEqual(self.client.get("/api/projects/model/model/").status_code, 404)

    def test_staff_without_lead_permission_cannot_download(self):
        self.post_lead(self.payload(files=[photo()]))
        attachment = LeadAttachment.objects.get()
        staff = get_user_model().objects.create_user("editor", password="test-only", is_staff=True)
        self.client.force_login(staff)
        url = reverse("attachment-download", args=[attachment.pk])
        self.assertEqual(self.client.get(url).status_code, 403)
        staff.user_permissions.add(Permission.objects.get(codename="view_leadattachment"))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response["Content-Disposition"].startswith("attachment;"))
        self.assertEqual(b"".join(response.streaming_content), photo().read())

    def test_production_requires_reviewed_legal_text(self):
        with override_settings(DEBUG=False):
            self.assertEqual(self.post_lead(self.payload()).status_code, 503)
            self.assertFalse(self.client.get("/api/settings/").json()["accept_leads"])

    def test_changed_consent_requires_refresh(self):
        payload = self.payload()
        self.config.consent_version = "reviewed-2"
        self.config.save()
        self.assertEqual(self.post_lead(payload).status_code, 400)
        self.assertEqual(Lead.objects.count(), 0)

    def test_notification_failure_does_not_lose_lead(self):
        self.post_lead(self.payload())
        with override_settings(LEAD_NOTIFICATION_EMAIL="admin@example.test"), patch("apps.leads.management.commands.process_notifications.send_mail", side_effect=OSError("offline")):
            call_command("process_notifications")
        item = Notification.objects.get()
        self.assertFalse(item.completed)
        self.assertEqual(item.attempts, 1)
        self.assertEqual(Lead.objects.count(), 1)
        item.next_attempt_at = timezone.now()
        item.save()
        with override_settings(LEAD_NOTIFICATION_EMAIL="admin@example.test"), patch("apps.leads.management.commands.process_notifications.send_mail") as mail:
            call_command("process_notifications")
            self.assertEqual(mail.call_count, 1)
        self.assertTrue(Notification.objects.get().completed)

    def test_seed_is_idempotent(self):
        call_command("seed_demo", verbosity=0)
        count = Project.objects.count()
        self.config.refresh_from_db()
        self.config.company_name = "Имя владельца"
        self.config.save()
        call_command("seed_demo", verbosity=0)
        self.assertEqual(Project.objects.count(), count)
        self.assertEqual(SiteSettings.objects.get().company_name, "Имя владельца")

    def test_bootstrap_without_demo_and_no_overwrite(self):
        self.config.privacy_text = "Текст владельца"
        self.config.save()
        with override_settings(DEBUG=False):
            call_command("bootstrap_content")
        self.assertEqual(Project.objects.count(), 0)
        self.assertEqual(Service.objects.count(), 6)
        self.assertEqual(SiteSettings.objects.get().privacy_text, "Текст владельца")

    def test_avif_upload_creates_webp_thumbnail(self):
        source = io.BytesIO()
        Image.new("RGB", (80, 60), "blue").save(source, "AVIF")
        project = Project(
            title="AVIF", slug="avif", category=self.category, summary="AVIF upload",
            cover=SimpleUploadedFile("image.avif", source.getvalue(), content_type="image/avif"),
        )
        project.full_clean()
        project.save()
        self.assertTrue(project.thumbnail.name.endswith(".webp"))


class ArchiveValidationTests(TestCase):
    def archive(self, entries):
        data = io.BytesIO()
        with zipfile.ZipFile(data, "w", zipfile.ZIP_DEFLATED) as archive:
            for name, content in entries:
                archive.writestr(name, content)
        return SimpleUploadedFile("archive.zip", data.getvalue())

    def test_rejects_traversal_nested_archive_code_and_bomb(self):
        for entries in [
            [("../escape.stl", "bad")], [("nested.zip", "zip")],
            [("run.exe", "exe")], [("part.obj", "0" * 200000)],
        ]:
            with self.subTest(entries=entries[0][0]), self.assertRaises(ValidationError):
                validate_attachment(self.archive(entries))

    def test_accepts_bounded_archive_without_extracting(self):
        file = self.archive([("readme.pdf", "%PDF-1.7\nTest document")])
        validate_attachment(file)
        self.assertEqual(file.tell(), 0)
