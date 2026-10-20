"""Non-destructive persistence smoke test against an existing local demo stack."""
import json
import subprocess
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = "http://localhost:8080"


def snapshot():
    with urllib.request.urlopen(f"{BASE}/api/projects/") as response:
        projects = json.load(response)
    with urllib.request.urlopen(f"{BASE}/api/settings/") as response:
        settings = json.load(response)
    return {"projects": [(p["id"], p["slug"], p["cover"]) for p in projects["results"]],
            "count": projects["count"], "company": settings["company_name"]}


def main():
    before = snapshot()
    subprocess.run(["docker", "compose", "restart", "db", "backend", "notifications", "frontend", "nginx"], cwd=ROOT, check=True)
    deadline = time.monotonic() + 120
    while time.monotonic() < deadline:
        try:
            after = snapshot()
            assert after == before, "Data changed after container restart"
            for _, _, cover in after["projects"]:
                if cover:
                    with urllib.request.urlopen(cover if cover.startswith("http") else BASE + cover) as response:
                        assert response.status == 200
            print("Project records, settings and images survived container restart.")
            return
        except (OSError, TimeoutError):
            time.sleep(2)
    raise RuntimeError("Stack did not recover within 120 seconds")


if __name__ == "__main__":
    main()
