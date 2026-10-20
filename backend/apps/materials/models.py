from django.db import models
from apps.core.models import OrderedModel, SeoModel


class Material(OrderedModel, SeoModel):
    name = models.CharField("Материал", max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField("Описание")
    applications = models.TextField("Применение", blank=True)
    advantages = models.TextField("Преимущества", blank=True)
    limitations = models.TextField("Ограничения", blank=True)
    properties = models.TextField("Ориентировочные свойства", blank=True)
    is_active = models.BooleanField("Доступен на сайте", default=True)

    class Meta(OrderedModel.Meta):
        verbose_name = "материал"
        verbose_name_plural = "Материалы"

    def __str__(self):
        return self.name
