"""Restore a verified backup into a local-volume Compose installation."""
import argparse
import hashlib
import json
import tarfile
from pathlib import Path, PurePosixPath
from backup import run, SERVICES


def main():
    parser = argparse.ArgumentParser(description="Replace database and restore files from a trusted backup.")
    parser.add_argument("backup", type=Path)
    parser.add_argument("--confirm", action="store_true", help="Confirm replacement of the target database.")
    args = parser.parse_args()
    if not args.confirm:
        parser.error("Restore replaces the database. Make a current backup first and pass --confirm.")
    source = args.backup.resolve(strict=True)
    manifest = json.loads((source / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("format") != 1:
        raise ValueError("Unknown backup format")
    for name in ["database.dump", "files.tar.gz"]:
        actual = hashlib.sha256((source / name).read_bytes()).hexdigest()
        if actual != manifest["sha256"].get(name):
            raise ValueError(f"Checksum mismatch: {name}")
    with tarfile.open(source / "files.tar.gz") as archive:
        for member in archive.getmembers():
            path = PurePosixPath(member.name)
            if path.is_absolute() or ".." in path.parts or path.parts[0] not in {"media", "private"}:
                raise ValueError("Unsafe backup path")
            if not (member.isfile() or member.isdir()):
                raise ValueError("Links and special files are not supported")
    run(["stop", *SERVICES])
    run(["up", "-d", "db"])
    try:
        with (source / "database.dump").open("rb") as file:
            run(["exec", "-T", "db", "sh", "-c",
                 'pg_restore -U "$POSTGRES_USER" -d "$POSTGRES_DB" --clean --if-exists --no-owner --single-transaction'], stdin=file)
        code = "import sys,tarfile; archive=tarfile.open(fileobj=sys.stdin.buffer,mode='r|gz'); archive.extractall('/app',filter='data')"
        with (source / "files.tar.gz").open("rb") as file:
            run(["run", "--rm", "--no-deps", "-T", "--entrypoint", "python", "backend", "-c", code], stdin=file)
    except Exception:
        print("Restore failed. Application remains stopped. Correct the cause before starting services.")
        raise
    run(["start", *SERVICES])
    print("Restore finished. Check the API, admin, images and a private attachment.")


if __name__ == "__main__":
    main()
