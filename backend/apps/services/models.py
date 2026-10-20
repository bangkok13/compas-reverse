from django.db import models
from apps.core.models import OrderedModel, SeoModel


class Service(OrderedModel, SeoModel):
    title = models.CharField("Услуга", max_length=200)
    slug = models.SlugField(unique=True)
    summary = models.CharField("Краткое описание", max_length=400)
    description = models.TextField("Описание")
    applications = models.TextField("Примеры применения", blank=True)
    materials = models.ManyToManyField("materials.Material", blank=True, verbose_name="Материалы")
    is_active = models.BooleanField("Доступна на сайте", default=True)

    class Meta(OrderedModel.Meta):
        verbose_name = "услуга"
        verbose_name_plural = "Услуги"

    def __str__(self):
        return self.title


class FAQ(OrderedModel):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="faq")
    question = models.CharField("Вопрос", max_length=300)
    answer = models.TextField("Ответ")

    class Meta(OrderedModel.Meta):
        verbose_name = "вопрос"
        verbose_name_plural = "Вопросы и ответы"
