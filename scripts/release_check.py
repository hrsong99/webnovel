#!/usr/bin/env python3
"""Run the repository's deterministic release checks and fail closed."""
from __future__ import annotations

import argparse
import html.parser
import json
import shutil
import subprocess
import sys
import time
import urllib.parse
import urllib.request
import uuid
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(*command: str) -> str:
    print("+", " ".join(command), flush=True)
    completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    if completed.stdout.strip(): print(completed.stdout.rstrip())
    if completed.stderr.strip(): print(completed.stderr.rstrip(), file=sys.stderr)
    if completed.returncode:
        raise SystemExit(f"release check failed ({completed.returncode}): {' '.join(command)}")
    return completed.stdout


class ReferenceParser(html.parser.HTMLParser):
    def __init__(self) -> None:
        super().__init__(); self.references: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for key, value in attrs:
            if key in {"href", "src"} and value: self.references.append(value)


def check_reference_graph(dist: Path) -> dict[str, int]:
    html_files = sorted(dist.rglob("*.html")); missing: list[tuple[str, str]] = []; checked = 0
    for page in html_files:
        parser = ReferenceParser(); parser.feed(page.read_text(encoding="utf-8"))
        for reference in parser.references:
            parsed = urllib.parse.urlsplit(reference)
            if parsed.scheme or reference.startswith(("#", "data:", "mailto:")): continue
            checked += 1
            target = dist / parsed.path.lstrip("/") if parsed.path.startswith("/") else page.parent / parsed.path
            if not target.exists(): missing.append((str(page.relative_to(dist)), reference))
    if missing:
        raise SystemExit("missing generated references:\n" + "\n".join(f"- {page}: {ref}" for page, ref in missing[:30]))
    return {"html_files": len(html_files), "local_references": checked, "missing": 0}


def check_epubs(dist: Path) -> dict[str, int]:
    epubs = sorted(dist.rglob("*.epub")); xml_documents = 0
    for epub in epubs:
        with zipfile.ZipFile(epub) as archive:
            if archive.testzip() is not None: raise SystemExit(f"corrupt EPUB member: {epub}")
            first = archive.infolist()[0]
            if first.filename != "mimetype" or first.compress_type != zipfile.ZIP_STORED:
                raise SystemExit(f"invalid EPUB mimetype entry: {epub}")
            required = {"META-INF/container.xml", "OEBPS/content.opf", "OEBPS/nav.xhtml"}
            if not required.issubset(archive.namelist()): raise SystemExit(f"missing EPUB structure: {epub}")
            for name in archive.namelist():
                if name.endswith((".xml", ".opf", ".xhtml")):
                    ET.fromstring(archive.read(name)); xml_documents += 1
    return {"epubs": len(epubs), "xml_documents": xml_documents}


def published_smoke_routes(dist: Path) -> list[str]:
    routes = {"/", "/chapters/01.html"}
    stories_root = dist / "stories"
    if stories_root.is_dir():
        for story_root in sorted(path for path in stories_root.iterdir() if path.is_dir()):
            slug = story_root.name
            routes.add(f"/stories/{slug}/")
            for chapter_root in (story_root / "chapters", story_root / "en" / "chapters"):
                chapters = sorted(chapter_root.glob("*.html")) if chapter_root.is_dir() else []
                if chapters:
                    relative = chapters[-1].relative_to(dist).as_posix()
                    routes.add("/" + relative)
    return sorted(routes)


def docker_check(port: int, routes: list[str]) -> dict[str, object]:
    if not shutil.which("docker"): raise SystemExit("docker is required for --docker")
    tag = f"webnovel-release-check:{uuid.uuid4().hex[:8]}"; name = f"webnovel-release-{uuid.uuid4().hex[:8]}"
    docker = ["docker"] if subprocess.run(["docker", "info"], capture_output=True).returncode == 0 else ["sudo", "-n", "docker"]
    try:
        run(*docker, "build", "-t", tag, ".")
        run(*docker, "run", "-d", "--name", name, "-p", f"{port}:8080", tag)
        deadline = time.time() + 30; response = ""
        while time.time() < deadline:
            try:
                response = urllib.request.urlopen(f"http://127.0.0.1:{port}/healthz", timeout=2).read().decode().strip()
                if response == "ok": break
            except Exception: time.sleep(.5)
        if response != "ok": raise SystemExit("container health route did not return ok")
        state = ""
        health_deadline = time.time() + 45
        while time.time() < health_deadline:
            inspected = subprocess.run(
                [*docker, "inspect", name, "--format", "{{.State.Status}} {{.State.Health.Status}} user={{.Config.User}} image={{.Image}}"],
                text=True, capture_output=True, check=False,
            )
            state = inspected.stdout.strip()
            if inspected.returncode == 0 and "running healthy" in state:
                break
            time.sleep(.5)
        print(state)
        if "running healthy" not in state or "user=101" not in state: raise SystemExit(f"unexpected container state: {state}")
        for route in routes:
            urllib.request.urlopen(f"http://127.0.0.1:{port}{route}", timeout=5).read(1)
        return {"health": response, "state": state, "routes": routes}
    finally:
        subprocess.run([*docker, "rm", "-f", name], capture_output=True)
        subprocess.run([*docker, "image", "rm", tag], capture_output=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--docker", action="store_true", help="also build and smoke-test the production container")
    parser.add_argument("--port", type=int, default=18084)
    args = parser.parse_args()

    run(sys.executable, "-m", "py_compile", "scripts/novel.py", "tests/test_novel.py")
    if not shutil.which("node"): raise SystemExit("node is required for JavaScript syntax checks")
    run("node", "--check", "site/home.js"); run("node", "--check", "site/reader.js")
    run(sys.executable, "-m", "unittest", "-q")
    run(sys.executable, "scripts/novel.py", "validate")
    stats = json.loads(run(sys.executable, "scripts/novel.py", "stats"))
    run(sys.executable, "scripts/novel.py", "build")
    run("git", "diff", "--check")

    graph = check_reference_graph(ROOT / "dist")
    epub = check_epubs(ROOT / "dist")
    container = docker_check(args.port, published_smoke_routes(ROOT / "dist")) if args.docker else None
    print(json.dumps({"status": "PASS", "stats": stats, "reference_graph": graph, "epub": epub, "container": container}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
