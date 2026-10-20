from django.db import models
from apps.core.models import OrderedModel, SeoModel
from apps.core.storage import unique_upload, private_storage
from apps.core.validators import validate_image, validate_model
from apps.core.images import make_thumbnail


class Category(OrderedModel):
    name = models.CharField("Название", max_length=160)
    slug = models.SlugField(unique=True)

    class Meta(OrderedModel.Meta):
        verbose_name = "категория"
        verbose_name_plural = "Категории проектов"

    def __str__(self):
        return self.name


class Project(OrderedModel, SeoModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Черновик"
        PUBLISHED = "published", "Опубликовано"

    title = models.CharField("Название", max_length=200)
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, verbose_name="Категория")
    summary = models.CharField("Краткое описание", max_length=400)
    description = models.TextField("Полное описание", blank=True)
    problem = models.TextField("Задача клиента", blank=True)
    solution = models.TextField("Как решали задачу", blank=True)
    result = models.TextField("Результат", blank=True)
    material = models.ForeignKey("materials.Material", on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Материал")
    technology = models.CharField("Технология", max_length=200, blank=True)
    services = models.ManyToManyField("services.Service", blank=True, related_name="projects", verbose_name="Услуги")
    cover = models.ImageField("Обложка", upload_to=unique_upload, validators=[validate_image], blank=True)
    thumbnail = models.ImageField(upload_to="thumbnails/", editable=False, blank=True)
    video_url = models.URLField("Ссылка на видео", blank=True)
    model_file = models.FileField("3D-модель (STL/GLB)", upload_to=unique_upload, storage=private_storage, validators=[validate_model], blank=True)
    viewer_enabled = models.BooleanField("Разрешить просмотр модели", default=False, help_text="Просмотр передаёт модель браузеру. Конфиденциальные модели не публикуйте.")
    completed_at = models.DateField("Дата выполнения", null=True, blank=True)
    status = models.CharField("Статус", max_length=20, choices=Status.choices, default=Status.DRAFT)
    featured = models.BooleanField("На главной", default=False)
    is_demo = models.BooleanField("Демонстрационный пример", default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta(OrderedModel.Meta):
        verbose_name = "проект"
        verbose_name_plural = "Проекты"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.cover and (not self.cover._committed or not self.thumbnail):
            make_thumbnail(self.cover, self.thumbnail)
        super().save(*args, **kwargs)


class ProjectImage(OrderedModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField("Фотография", upload_to=unique_upload, validators=[validate_image])
    thumbnail = models.ImageField(upload_to="thumbnails/", editable=False, blank=True)
    caption = models.CharField("Подпись", max_length=250, blank=True)
    role = models.CharField("До / после", max_length=10, blank=True, choices=[("before", "До"), ("after", "После")])

    class Meta(OrderedModel.Meta):
        verbose_name = "фотография"
        verbose_name_plural = "Фотографии проекта"

    def save(self, *args, **kwargs):
        if self.image and (not self.image._committed or not self.thumbnail):
            make_thumbnail(self.image, self.thumbnail)
        super().save(*args, **kwargs)
