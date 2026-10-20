from pathlib import Path
from uuid import uuid4
from django.conf import settings
from django.core.files.storage import FileSystemStorage, storages
from storages.backends.s3 import S3Storage


class PrivateFileSystemStorage(FileSystemStorage):
    def __init__(self, *args, **kwargs):
        super().__init__(location=settings.PRIVATE_ROOT, base_url=None)

    def url(self, name):
        raise ValueError("Private files are only available to authorized staff.")


class PrivateS3Storage(S3Storage):
    def url(self, name, *args, **kwargs):
        raise ValueError("Private files are only available through the application.")


def private_storage():
    return storages["private"]


def unique_upload(instance, filename):
    suffix = Path(filename).suffix.lower()
    return f"{instance._meta.model_name}/{uuid4().hex}{suffix}"
