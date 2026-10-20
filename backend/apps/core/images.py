from io import BytesIO
from pathlib import Path
from django.core.files.base import ContentFile
from PIL import Image, ImageOps


def make_thumbnail(source, target):
    source.open("rb")
    content = BytesIO(source.read())
    # An uncommitted upload must remain open until Django saves the original.
    if source._committed:
        source.close()
    else:
        source.seek(0)
    with Image.open(content) as original:
        image = ImageOps.exif_transpose(original).convert("RGB")
        image.thumbnail((1000, 750))
        output = BytesIO()
        image.save(output, format="WEBP", quality=84, method=6)
    target.save(f"{Path(source.name).stem}.webp", ContentFile(output.getvalue()), save=False)
