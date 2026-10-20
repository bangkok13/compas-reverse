import uuid
from django.db import models
from apps.core.storage import private_storage, unique_upload
from apps.core.validators import validate_attachment


class Lead(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "Новая"
        ESTIMATING = "estimating", "На оценке"
        WAITING = "waiting", "Ожидает ответа клиента"
        APPROVED = "approved", "Согласована"
        IN_PROGRESS = "in_progress", "В работе"
        DONE = "done", "Готова"
        CLOSED = "closed", "Закрыта"
        CANCELLED = "cancelled", "Отменена"

    reference = models.UUIDField("Номер", default=uuid.uuid4, unique=True, editable=False)
    idempotency_key = models.UUIDField(unique=True, editable=False)
    payload_hash = models.CharField(max_length=64, editable=False)
    name = models.CharField("Имя", max_length=120)
    phone = models.CharField("Телефон", max_length=40)
    email = models.EmailField(blank=True)
    service = models.ForeignKey("services.Service", on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Услуга")
    description = models.TextField("Описание задачи")
    dimensions = models.CharField("Размеры", max_length=200, blank=True)
    quantity = models.PositiveIntegerField("Количество", default=1)
    material = models.CharField("Материал", max_length=100, blank=True)
    deadline = models.DateField("Желаемый срок", null=True, blank=True)
    consent = models.BooleanField("Согласие", default=False)
    consent_version = models.CharField("Версия согласия", max_length=40)
    created_at = models.DateTimeField("Дата обращения", auto_now_add=True)
    status = models.CharField("Статус", max_length=20, choices=Status.choices, default=Status.NEW)
    internal_notes = models.TextField("Внутренние комментарии", blank=True)
    estimated_price = models.DecimalField("Предварительная стоимость", max_digits=12, decimal_places=2, null=True, blank=True)
    final_price = models.DecimalField("Итоговая стоимость", max_digits=12, decimal_places=2, null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "заявка"
        verbose_name_plural = "Заявки"

    def __str__(self):
        return f"3D-{str(self.reference).upper()}"


class LeadAttachment(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name="attachments")
    file = models.FileField("Файл", upload_to=unique_upload, storage=private_storage, validators=[validate_attachment])
    original_name = models.CharField("Исходное имя", max_length=250)
    size = models.PositiveIntegerField("Размер")

    class Meta:
        verbose_name = "вложение"
        verbose_name_plural = "Вложения"


class Notification(models.Model):
    lead = models.OneToOneField(Lead, on_delete=models.CASCADE)
    email_sent_at = models.DateTimeField(null=True, blank=True)
    telegram_sent_at = models.DateTimeField(null=True, blank=True)
    attempts = models.PositiveIntegerField(default=0)
    next_attempt_at = models.DateTimeField()
    completed = models.BooleanField(default=False)
