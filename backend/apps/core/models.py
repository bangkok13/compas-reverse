from django.db import models


class OrderedModel(models.Model):
    sort_order = models.PositiveIntegerField("Порядок", default=0)

    class Meta:
        abstract = True
        ordering = ["sort_order", "pk"]


class SeoModel(models.Model):
    seo_title = models.CharField("SEO title", max_length=200, blank=True)
    seo_description = models.CharField("SEO description", max_length=320, blank=True)

    class Meta:
        abstract = True


class RateWindow(models.Model):
    key = models.CharField(max_length=80, primary_key=True)
    starts_at = models.DateTimeField()
    count = models.PositiveIntegerField(default=0)
