from django.db import transaction
from django.db.models.signals import post_delete
from django.dispatch import receiver
from apps.leads.models import LeadAttachment
from apps.portfolio.models import Project, ProjectImage


@receiver(post_delete, sender=LeadAttachment)
@receiver(post_delete, sender=Project)
@receiver(post_delete, sender=ProjectImage)
def remove_files(sender, instance, **kwargs):
    for field_name in ("file", "cover", "thumbnail", "image", "model_file"):
        field = getattr(instance, field_name, None)
        if field and field.name:
            storage, name = field.storage, field.name
            transaction.on_commit(lambda storage=storage, name=name: storage.delete(name))
