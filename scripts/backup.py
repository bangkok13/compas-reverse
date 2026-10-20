"""Consistent local-volume backup. Run from any directory; requires Docker Compose."""
import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SERVICES = ["nginx", "backend", "notifications"]


def run(args, **kwargs):
    return subprocess.run(["docker", "compose", *args], cwd=ROOT, check=True, **kwargs)


def main():
    parser = argparse.ArgumentParser(description="Backup PostgreSQL and local media with a brief maintenance stop.")
    parser.add_argument("--output", type=Path, default=ROOT / "backups")
    args = parser.parse_args()
    destination = args.output.resolve() / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    destination.mkdir(parents=True, exist_ok=False)
    stopped = False
    try:
        stopped = True
        run(["stop", *SERVICES])
        with (destination / "database.dump").open("wb") as file:
            run(["exec", "-T", "db", "sh", "-c", 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc'], stdout=file)
        code = (
            "import os,sys,tarfile; "
            "assert os.environ.get('USE_S3','false').lower() != 'true', 'For S3 back up buckets separately'; "
            "archive=tarfile.open(fileobj=sys.stdout.buffer, mode='w|gz'); "
            "archive.add('/app/media',arcname='media'); archive.add('/app/private',arcname='private'); archive.close()"
        )
        with (destination / "files.tar.gz").open("wb") as file:
            run(["run", "--rm", "--no-deps", "-T", "--entrypoint", "python", "backend", "-c", code], stdout=file)
        files = {name: hashlib.sha256((destination / name).read_bytes()).hexdigest()
                 for name in ["database.dump", "files.tar.gz"]}
        (destination / "manifest.json").write_text(json.dumps({"format": 1, "sha256": files}, indent=2), encoding="utf-8")
        print(f"Backup ready: {destination}")
    finally:
        if stopped:
            run(["start", *SERVICES])


if __name__ == "__main__":
    main()
