import json
import logging
import time
from datetime import timedelta
from urllib.request import Request, urlopen
from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.db import transaction
from django.utils import timezone
from apps.leads.models import Notification
from apps.core.models import RateWindow

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Deliver queued lead notifications; --loop for a single dedicated worker."

    def add_arguments(self, parser):
        parser.add_argument("--loop", action="store_true")

    def handle(self, *args, **options):
        while True:
            ids = list(Notification.objects.filter(completed=False, next_attempt_at__lte=timezone.now()).values_list("pk", flat=True)[:50])
            for pk in ids:
                self.deliver(pk)
            RateWindow.objects.filter(starts_at__lt=timezone.now() - timedelta(days=2)).delete()
            if not options["loop"]:
                return
            time.sleep(15)

    def deliver(self, pk):
        with transaction.atomic():
            item = Notification.objects.select_for_update().select_related("lead").get(pk=pk)
            if item.completed or item.next_attempt_at > timezone.now():
                return
            # Keep personal details and source attachments inside the secured admin.
            message = f"Новая заявка {item.lead}\n{settings.SITE_URL}/admin/leads/lead/{item.lead_id}/change/"
            item.attempts += 1
            try:
                if settings.LEAD_NOTIFICATION_EMAIL and not item.email_sent_at:
                    send_mail("Новая заявка 3D-мастерской", message, settings.DEFAULT_FROM_EMAIL, [settings.LEAD_NOTIFICATION_EMAIL])
                    item.email_sent_at = timezone.now()
                if settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_CHAT_ID and not item.telegram_sent_at:
                    req = Request(
                        f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage",
                        data=json.dumps({"chat_id": settings.TELEGRAM_CHAT_ID, "text": message}).encode(),
                        headers={"Content-Type": "application/json"},
                    )
                    with urlopen(req, timeout=15) as response:
                        if not json.load(response).get("ok"):
                            raise RuntimeError("Telegram delivery failed")
                    item.telegram_sent_at = timezone.now()
                if settings.LEAD_NOTIFICATION_EMAIL or (settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_CHAT_ID):
                    item.completed = True
            except Exception:
                # Do not log exception URLs: Telegram tokens may be included.
                logger.error("Notification delivery failed for queue item %s, attempt %s", item.pk, item.attempts)
            item.next_attempt_at = timezone.now() + timedelta(seconds=min(3600, 30 * 2 ** min(item.attempts, 7)))
            item.save()
