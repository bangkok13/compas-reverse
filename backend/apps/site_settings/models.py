from django.db import models
from apps.core.storage import unique_upload
from apps.core.validators import validate_image


class SiteSettings(models.Model):
    company_name = models.CharField("Название", max_length=200, default="3D Engineering Volgograd")
    logo = models.ImageField("Логотип", upload_to=unique_upload, validators=[validate_image], blank=True)
    hero_title = models.CharField("Заголовок главной", max_length=250, default="Восстанавливаем детали, которых больше нет в продаже.")
    hero_subtitle = models.TextField("Подзаголовок", default="3D-сканирование, реверс-инжиниринг и изготовление функциональных деталей из инженерных пластиков в Волгограде.")
    phone = models.CharField("Телефон", max_length=40, blank=True)
    email = models.EmailField("Email", blank=True)
    telegram = models.URLField("Telegram", blank=True)
    max_url = models.URLField("MAX", blank=True)
    address = models.CharField("Публичный адрес", max_length=300, blank=True)
    hours = models.CharField("Режим работы", max_length=200, blank=True)
    legal_details = models.TextField("Реквизиты", blank=True)
    map_url = models.URLField("Ссылка на карту", blank=True)
    region = models.CharField("Регион", max_length=200, default="Волгоград · Волжский · Доставка по России")
    seo_title = models.CharField("SEO title", max_length=200, default="3D-печать и восстановление деталей в Волгограде")
    seo_description = models.CharField("SEO description", max_length=320, default="3D-печать, сканирование и реверс-инжиниринг в Волгограде и Волжском. Изготовление функциональных деталей из инженерных пластиков.")
    process = models.JSONField("Этапы работы", default=list, blank=True)
    advantages = models.JSONField("Преимущества", default=list, blank=True)
    business_text = models.TextField("Для организаций", blank=True)
    privacy_text = models.TextField("Политика конфиденциальности", blank=True)
    consent_text = models.TextField("Согласие на обработку данных", blank=True)
    legal_reviewed = models.BooleanField("Юридические тексты проверены", default=False)
    consent_version = models.CharField("Версия согласия", max_length=40, default="draft-1")
    accept_leads = models.BooleanField("Принимать заявки", default=True, help_text="Перед production-запуском проверьте реквизиты, согласие и место хранения данных.")

    class Meta:
        verbose_name = "настройки сайта"
        verbose_name_plural = "Настройки сайта"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.company_name
