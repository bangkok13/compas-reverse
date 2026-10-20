from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from apps.leads.models import Lead
from apps.portfolio.models import Project


class Command(BaseCommand):
    help = "Remove only clearly marked local E2E records and test accounts."

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError("Only allowed in DEBUG mode.")
        Project.objects.filter(title="Демонстрационный проект E2E", is_demo=True).delete()
        Lead.objects.filter(name="Демонстрационный клиент E2E", description__startswith="Тестовая заявка:").delete()
        get_user_model().objects.filter(email="e2e@example.test").delete()
        self.stdout.write("Local E2E records removed.")
