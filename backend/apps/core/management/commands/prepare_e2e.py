import os
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from apps.core.models import RateWindow


class Command(BaseCommand):
    help = "Create a local-only E2E account using credentials passed through environment."

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError("Only available in a local DEBUG environment.")
        username = os.environ.get("E2E_ADMIN_USER")
        password = os.environ.get("E2E_ADMIN_PASSWORD")
        if not username or not password:
            raise CommandError("E2E_ADMIN_USER and E2E_ADMIN_PASSWORD are required.")
        user, created = get_user_model().objects.get_or_create(username=username)
        if not created and not user.email.endswith("@example.test"):
            raise CommandError("Refusing to change a non-test account.")
        user.email = "e2e@example.test"
        user.is_staff = user.is_superuser = True
        user.set_password(password)
        user.save()
        RateWindow.objects.all().delete()
        self.stdout.write("Local E2E account ready.")
