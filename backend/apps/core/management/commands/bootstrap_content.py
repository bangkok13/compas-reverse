from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create the initial editable service/material catalog without fictitious projects."

    def handle(self, *args, **options):
        call_command("seed_demo", content_only=True)
