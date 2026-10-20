import struct
import zipfile
from pathlib import PurePosixPath, Path
from django.conf import settings
from django.core.exceptions import ValidationError
from PIL import Image, UnidentifiedImageError

IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "webp", "avif"}
LEAD_EXTENSIONS = {"jpg", "jpeg", "png", "webp", "pdf", "stl", "step", "stp", "obj", "3mf", "zip"}
Image.MAX_IMAGE_PIXELS = 30_000_000


def validate_archive(file, is_3mf=False):
    try:
        with zipfile.ZipFile(file) as archive:
            entries = archive.infolist()
            if not entries or len(entries) > 200:
                raise ValidationError("В архиве должно быть от 1 до 200 файлов.")
            total = 0
            for entry in entries:
                path = PurePosixPath(entry.filename.replace("\\", "/"))
                total += entry.file_size
                if path.is_absolute() or ".." in path.parts or ":" in entry.filename:
                    raise ValidationError("Небезопасный путь внутри архива.")
                if entry.flag_bits & 1 or (entry.external_attr >> 16) & 0o170000 == 0o120000:
                    raise ValidationError("Зашифрованные архивы и символические ссылки не поддерживаются.")
                if entry.file_size > 50 * 1024 * 1024 or total > 100 * 1024 * 1024:
                    raise ValidationError("Слишком большой распакованный архив.")
                if entry.file_size / max(entry.compress_size, 1) > 100:
                    raise ValidationError("Слишком высокая степень сжатия архива.")
                allowed = ({"xml", "rels", "model", "png", "jpg", "jpeg"} if is_3mf
                           else LEAD_EXTENSIONS - {"zip", "3mf"})
                if not entry.is_dir() and path.suffix.lower().lstrip(".") not in allowed:
                    raise ValidationError("Архив содержит неподдерживаемый тип файла.")
            if is_3mf and not any(e.filename.lower().endswith(".model") for e in entries):
                raise ValidationError("В 3MF отсутствует модель.")
    except (zipfile.BadZipFile, RuntimeError, OSError):
        raise ValidationError("Повреждённый архив.")
    finally:
        file.seek(0)


def validate_file(file, allowed):
    ext = Path(file.name).suffix.lower().lstrip(".")
    if ext not in allowed:
        raise ValidationError("Недопустимый формат файла.")
    if not file.size or file.size > settings.MAX_FILE_SIZE:
        raise ValidationError("Размер файла должен быть от 1 байта до 20 МБ.")
    file.seek(0)
    head = file.read(1024)
    file.seek(0)
    try:
        if ext in IMAGE_EXTENSIONS:
            with Image.open(file) as image:
                if image.format not in {"JPEG", "PNG", "WEBP", "AVIF"}:
                    raise ValidationError("Недопустимый формат изображения.")
                expected = {"jpg": "JPEG", "jpeg": "JPEG", "png": "PNG", "webp": "WEBP", "avif": "AVIF"}
                if image.format != expected[ext] or image.width * image.height > 30_000_000:
                    raise ValidationError("Формат или размеры изображения не подходят.")
                image.verify()
        elif ext == "pdf" and not head.startswith(b"%PDF-"):
            raise ValidationError("Файл не является PDF.")
        elif ext in {"zip", "3mf"}:
            validate_archive(file, ext == "3mf")
        elif ext == "glb":
            if len(head) < 12 or head[:4] != b"glTF" or struct.unpack("<II", head[4:12]) != (2, file.size):
                raise ValidationError("Некорректная GLB-модель.")
        elif ext == "stl":
            binary = len(head) >= 84 and file.size == 84 + struct.unpack("<I", head[80:84])[0] * 50
            if not binary and not (head.lstrip().startswith(b"solid") and b"facet" in head):
                raise ValidationError("Некорректная STL-модель.")
        elif ext in {"step", "stp"} and b"ISO-10303-21" not in head.upper():
            raise ValidationError("Некорректный STEP-файл.")
        elif ext == "obj":
            text = file.read().decode("utf-8-sig")
            if not any(line.startswith("v ") for line in text.splitlines()) or "\x00" in text:
                raise ValidationError("Некорректный OBJ-файл.")
    except (UnidentifiedImageError, OSError, ValueError, UnicodeError, Image.DecompressionBombError):
        raise ValidationError("Файл повреждён или имеет неверный формат.")
    finally:
        file.seek(0)


def validate_image(file):
    validate_file(file, IMAGE_EXTENSIONS)


def validate_attachment(file):
    validate_file(file, LEAD_EXTENSIONS)


def validate_model(file):
    validate_file(file, {"stl", "glb"})
