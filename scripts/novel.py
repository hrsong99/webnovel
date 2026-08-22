#!/usr/bin/env python3
"""Validate and build the canonical web-novel manuscript (stdlib only)."""

from __future__ import annotations

import argparse
import collections
import datetime as _datetime
import html
import json
import re
import sys
import uuid
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


HEADING_RE = re.compile(r"^# 제([1-9][0-9]*)화\.\s+(.+?)\s*$")
KOREAN_RE = re.compile(r"[가-힣ㄱ-ㅎㅏ-ㅣ]")
PLACEHOLDER_RE = re.compile(
    r"(?i)(?:\b(?:TODO|TBD|FIXME|XXX|PLACEHOLDER)\b|"
    r"(?:작성|집필|내용)\s*(?:예정|필요|추가)|추후\s*(?:작성|보강)|"
    r"여기에\s*작성|미완성\s*본문)"
)
EDITORIAL_RE = re.compile(
    r"(?im)(?:^---\s*$|<!--|-->|^\s*(?:[-*]\s*)?\[[ xX]\]\s+|"
    r"(?:편집\s*메모|작가\s*(?:노트|메모)|기획\s*(?:메모|의도)|"
    r"장면\s*(?:목적|요약)|시놉시스|복선|POV|관점|등장인물|키워드)\s*[:：])"
)
REQUIRED_TEXT_FIELDS = ("slug", "title", "author", "language", "description")
REQUIRED_INT_FIELDS = ("min_chapter_chars", "max_chapter_chars", "expected_chapters")


class NovelError(Exception):
    """A user-actionable manuscript or configuration error."""


@dataclass(frozen=True)
class Chapter:
    number: int
    title: str
    body: str
    path: Path
    korean_chars: int

    @property
    def heading(self) -> str:
        return f"제{self.number}화. {self.title}"


@dataclass(frozen=True)
class Manuscript:
    root: Path
    metadata: dict[str, Any]
    chapters: tuple[Chapter, ...]


def count_korean(text: str) -> int:
    return len(KOREAN_RE.findall(text))


def load_metadata(root: Path) -> tuple[dict[str, Any], list[str]]:
    path = root / "story.json"
    if not path.is_file():
        raise NovelError(f"missing canonical metadata file: {path}")
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except UnicodeDecodeError as exc:
        raise NovelError(f"story.json must be UTF-8: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise NovelError(f"invalid story.json: line {exc.lineno}, column {exc.colno}: {exc.msg}") from exc
    if not isinstance(raw, dict):
        raise NovelError("invalid story.json: top-level value must be an object")

    errors: list[str] = []
    for field in REQUIRED_TEXT_FIELDS:
        value = raw.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"story.json field {field!r} must be a non-empty string")
    for field in REQUIRED_INT_FIELDS:
        value = raw.get(field)
        if isinstance(value, bool) or not isinstance(value, int) or value < 1:
            errors.append(f"story.json field {field!r} must be a positive integer")
    if re.search(r"[\\/]", str(raw.get("slug", ""))) or raw.get("slug") in {".", ".."}:
        errors.append("story.json field 'slug' must be a safe filename without path separators")
    minimum = raw.get("min_chapter_chars")
    maximum = raw.get("max_chapter_chars")
    if isinstance(minimum, int) and isinstance(maximum, int) and minimum > maximum:
        errors.append("story.json min_chapter_chars must not exceed max_chapter_chars")
    return raw, errors


def repeated_phrases(body: str) -> list[str]:
    """Return strongly suspicious exact repetitions, avoiding common short phrases."""
    normalized_sentences = []
    for sentence in re.split(r"(?<=[.!?。！？])\s+|\n+", body):
        normalized = re.sub(r"\s+", " ", sentence).strip(" \t\"'“”‘’")
        if len(normalized) >= 12 and count_korean(normalized) >= 8:
            normalized_sentences.append(normalized)
    repeated = [
        phrase
        for phrase, occurrences in collections.Counter(normalized_sentences).items()
        if occurrences >= 3
    ]

    # Also catch a long copied phrase embedded in otherwise different sentences.
    tokens = re.findall(r"[가-힣A-Za-z0-9]+", body)
    if len(tokens) >= 20:
        windows = [" ".join(tokens[index : index + 6]) for index in range(len(tokens) - 5)]
        for phrase, occurrences in collections.Counter(windows).items():
            if occurrences >= 4 and count_korean(phrase) >= 10:
                repeated.append(phrase)
    return sorted(set(repeated), key=lambda value: (-len(value), value))


def read_manuscript(root: Path) -> Manuscript:
    root = root.resolve()
    metadata, errors = load_metadata(root)
    chapter_dir = root / "manuscript" / "chapters"
    if not chapter_dir.is_dir():
        errors.append(f"missing chapter directory: {chapter_dir}")
        files: list[Path] = []
    else:
        files = sorted(chapter_dir.glob("*.md"))
        if not files:
            errors.append(f"no Markdown chapters found in {chapter_dir}")

    chapters: list[Chapter] = []
    for path in files:
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            errors.append(f"{path.name}: chapter must be UTF-8")
            continue
        lines = content.splitlines()
        if not lines:
            errors.append(f"{path.name}: chapter is empty")
            continue
        match = HEADING_RE.fullmatch(lines[0])
        if not match:
            errors.append(f"{path.name}: first line must match '# 제N화. 제목'")
            continue
        number = int(match.group(1))
        title = match.group(2).strip()
        body = "\n".join(lines[1:]).strip()
        if not body:
            errors.append(f"{path.name}: chapter body is empty")
        korean_chars = count_korean(body)
        minimum = metadata.get("min_chapter_chars")
        maximum = metadata.get("max_chapter_chars")
        if isinstance(minimum, int) and isinstance(maximum, int) and not (minimum <= korean_chars <= maximum):
            errors.append(
                f"{path.name}: {korean_chars} Korean characters; required range is {minimum}-{maximum}"
            )
        if PLACEHOLDER_RE.search(body):
            errors.append(f"{path.name}: placeholder text found in prose")
        if EDITORIAL_RE.search(body):
            errors.append(f"{path.name}: editorial/planning metadata found in prose")
        repetitions = repeated_phrases(body)
        if repetitions:
            preview = repetitions[0][:80]
            errors.append(f"{path.name}: suspicious repetition found: {preview!r}")
        chapters.append(Chapter(number, title, body, path, korean_chars))

    chapters.sort(key=lambda chapter: chapter.number)
    numbers = [chapter.number for chapter in chapters]
    duplicates = [number for number, count in collections.Counter(numbers).items() if count > 1]
    if duplicates:
        errors.append("duplicate chapter number(s): " + ", ".join(map(str, duplicates)))
    if numbers:
        expected_sequence = list(range(1, max(numbers) + 1))
        if numbers != expected_sequence:
            missing = sorted(set(expected_sequence) - set(numbers))
            errors.append(
                "chapter numbering gap or invalid starting number; "
                f"found {numbers}, missing {missing or '[chapter 1]'}"
            )
    expected_count = metadata.get("expected_chapters")
    if isinstance(expected_count, int) and len(chapters) != expected_count:
        errors.append(
            f"expected_chapters is {expected_count}, but found {len(chapters)} parseable chapter(s)"
        )

    if errors:
        raise NovelError("manuscript validation failed:\n" + "\n".join(f"- {error}" for error in errors))
    return Manuscript(root, metadata, tuple(chapters))


def manuscript_stats(manuscript: Manuscript) -> dict[str, Any]:
    chapter_stats = [
        {
            "number": chapter.number,
            "title": chapter.title,
            "korean_characters": chapter.korean_chars,
            "source": chapter.path.name,
        }
        for chapter in manuscript.chapters
    ]
    return {
        "slug": manuscript.metadata["slug"],
        "title": manuscript.metadata["title"],
        "chapter_count": len(manuscript.chapters),
        "korean_characters": sum(chapter.korean_chars for chapter in manuscript.chapters),
        "chapters": chapter_stats,
    }


def combined_markdown(manuscript: Manuscript) -> str:
    meta = manuscript.metadata
    parts = [f"# {meta['title']}"]
    if meta.get("subtitle"):
        parts.append(f"*{meta['subtitle']}*")
    parts.extend(
        [
            f"**저자:** {meta['author']}",
            str(meta["description"]),
        ]
    )
    parts.extend(f"## {chapter.heading}\n\n{chapter.body}" for chapter in manuscript.chapters)
    return "\n\n".join(parts).rstrip() + "\n"


def body_paragraphs(body: str) -> str:
    paragraphs = re.split(r"\n\s*\n", body.strip())
    rendered = []
    for paragraph in paragraphs:
        rendered.append(f"<p>{html.escape(paragraph).replace(chr(10), '<br />')}</p>")
    return "\n".join(rendered)


def standalone_html(manuscript: Manuscript) -> str:
    meta = manuscript.metadata
    chapters = "\n".join(
        f'<section class="chapter" id="chapter-{chapter.number}">'
        f"<h2>{html.escape(chapter.heading)}</h2>{body_paragraphs(chapter.body)}</section>"
        for chapter in manuscript.chapters
    )
    toc = "".join(
        f'<li><a href="#chapter-{chapter.number}">{html.escape(chapter.heading)}</a></li>'
        for chapter in manuscript.chapters
    )
    subtitle = html.escape(str(meta.get("subtitle", "")))
    subtitle_html = f'<p class="subtitle">{subtitle}</p>' if subtitle else ""
    return f'''<!doctype html>
<html lang="{html.escape(meta['language'], quote=True)}">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(meta['title'])}</title>
<style>
:root{{--paper:#f7f3ea;--ink:#211d18;--muted:#746b60;--accent:#8b2f24;--rule:#d7cec0}}
*{{box-sizing:border-box}}html{{scroll-behavior:smooth}}body{{font-family:"Noto Serif KR","Nanum Myeongjo",serif;line-height:1.9;max-width:46rem;margin:0 auto;padding:clamp(1.25rem,4vw,3.5rem);background:var(--paper);color:var(--ink);word-break:keep-all}}header{{text-align:center;min-height:72vh;display:flex;flex-direction:column;justify-content:center;border-bottom:1px solid var(--rule)}}h1{{font-size:clamp(2.25rem,8vw,4.25rem);letter-spacing:-.06em;margin:.2em 0}}.subtitle{{color:var(--accent);font-size:1.15rem;letter-spacing:.08em}}.byline,.description{{color:var(--muted)}}.description{{max-width:34rem;margin:2rem auto 0}}nav{{padding:3rem 0;border-bottom:1px solid var(--rule)}}nav h2{{font-size:1rem;color:var(--muted);letter-spacing:.15em}}nav ol{{padding-left:1.4rem;columns:2;column-gap:2rem}}nav li{{margin:.55rem 0}}a{{color:var(--ink);text-decoration-color:var(--rule);text-underline-offset:.25em}}.chapter{{margin:7rem 0}}.chapter h2{{font-size:1.75rem;margin-bottom:3rem;padding-bottom:1rem;border-bottom:1px solid var(--rule)}}p{{margin:0;text-indent:1em}}p+p{{margin-top:.55em}}@media(max-width:34rem){{nav ol{{columns:1}}.chapter{{margin:5rem 0}}}}@media(prefers-color-scheme:dark){{:root{{--paper:#171513;--ink:#eee8dd;--muted:#aaa095;--accent:#dc8a7f;--rule:#3c3731}}}}
</style></head>
<body><header><p class="byline">{html.escape(meta['author'])}</p><h1>{html.escape(meta['title'])}</h1>{subtitle_html}<p class="description">{html.escape(meta['description'])}</p></header>
<nav aria-label="목차"><h2>차례</h2><ol>{toc}</ol></nav><main>{chapters}</main></body></html>
'''


def plain_text(manuscript: Manuscript) -> str:
    meta = manuscript.metadata
    parts = [str(meta["title"])]
    if meta.get("subtitle"):
        parts.append(str(meta["subtitle"]))
    parts.extend([str(meta["author"]), str(meta["description"])])
    parts.extend(f"{chapter.heading}\n\n{chapter.body}" for chapter in manuscript.chapters)
    return "\n\n".join(parts).rstrip() + "\n"


def xhtml_document(language: str, title: str, body: str) -> str:
    return f'''<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" lang="{html.escape(language, quote=True)}" xml:lang="{html.escape(language, quote=True)}"><head><meta charset="utf-8"/><title>{html.escape(title)}</title><link rel="stylesheet" type="text/css" href="style.css"/></head><body>{body}</body></html>'''


def build_epub(manuscript: Manuscript, destination: Path) -> None:
    meta = manuscript.metadata
    language = str(meta["language"])
    identifier = f"urn:uuid:{uuid.uuid5(uuid.NAMESPACE_URL, str(meta['slug']))}"
    modified = _datetime.datetime.now(_datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    chapter_items = "\n".join(
        f'<item id="chapter-{c.number}" href="chapter-{c.number:03d}.xhtml" media-type="application/xhtml+xml"/>'
        for c in manuscript.chapters
    )
    spine = "\n".join(f'<itemref idref="chapter-{c.number}"/>' for c in manuscript.chapters)
    nav_links = "".join(
        f'<li><a href="chapter-{c.number:03d}.xhtml">{html.escape(c.heading)}</a></li>'
        for c in manuscript.chapters
    )
    opf = f'''<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="book-id" xml:lang="{html.escape(language, quote=True)}"><metadata xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:identifier id="book-id">{identifier}</dc:identifier><dc:title>{html.escape(meta['title'])}</dc:title><dc:creator>{html.escape(meta['author'])}</dc:creator><dc:language>{html.escape(language)}</dc:language><dc:description>{html.escape(meta['description'])}</dc:description><meta property="dcterms:modified">{modified}</meta></metadata><manifest><item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/><item id="style" href="style.css" media-type="text/css"/>{chapter_items}</manifest><spine>{spine}</spine></package>'''
    nav = xhtml_document(
        language,
        str(meta["title"]),
        f'<nav xmlns:epub="http://www.idpf.org/2007/ops" epub:type="toc" id="toc"><h1>{html.escape(meta["title"])}</h1><ol>{nav_links}</ol></nav>',
    )
    container = '''<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles></container>'''
    style = "body{font-family:serif;line-height:1.8;margin:5%;} h1{text-align:center;} p{text-indent:1em;margin:.8em 0;}"

    with zipfile.ZipFile(destination, "w") as archive:
        archive.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)
        archive.writestr("META-INF/container.xml", container, compress_type=zipfile.ZIP_DEFLATED)
        archive.writestr("OEBPS/content.opf", opf, compress_type=zipfile.ZIP_DEFLATED)
        archive.writestr("OEBPS/nav.xhtml", nav, compress_type=zipfile.ZIP_DEFLATED)
        archive.writestr("OEBPS/style.css", style, compress_type=zipfile.ZIP_DEFLATED)
        for chapter in manuscript.chapters:
            chapter_xhtml = xhtml_document(
                language,
                chapter.heading,
                f"<h1>{html.escape(chapter.heading)}</h1>{body_paragraphs(chapter.body)}",
            )
            archive.writestr(
                f"OEBPS/chapter-{chapter.number:03d}.xhtml",
                chapter_xhtml,
                compress_type=zipfile.ZIP_DEFLATED,
            )


def build(manuscript: Manuscript) -> list[Path]:
    dist = manuscript.root / "dist"
    dist.mkdir(parents=True, exist_ok=True)
    slug = manuscript.metadata["slug"]
    outputs = [dist / f"{slug}.{extension}" for extension in ("md", "html", "txt", "epub")]
    outputs[0].write_text(combined_markdown(manuscript), encoding="utf-8")
    outputs[1].write_text(standalone_html(manuscript), encoding="utf-8")
    outputs[2].write_text(plain_text(manuscript), encoding="utf-8")
    build_epub(manuscript, outputs[3])
    return outputs


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    default_root = Path(__file__).resolve().parents[1]
    for command, help_text in (
        ("validate", "validate metadata and chapter sources"),
        ("stats", "validate and print manuscript statistics as JSON"),
        ("build", "validate and build Markdown, HTML, TXT, and EPUB"),
    ):
        subparser = subparsers.add_parser(command, help=help_text)
        subparser.add_argument("--root", type=Path, default=default_root, help=argparse.SUPPRESS)
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = make_parser().parse_args(argv)
    try:
        manuscript = read_manuscript(args.root)
        if args.command == "validate":
            stats = manuscript_stats(manuscript)
            print(
                f"VALID: {stats['chapter_count']} chapter(s), "
                f"{stats['korean_characters']} Korean characters"
            )
        elif args.command == "stats":
            print(json.dumps(manuscript_stats(manuscript), ensure_ascii=False, indent=2))
        elif args.command == "build":
            outputs = build(manuscript)
            print("BUILT:")
            for output in outputs:
                print(f"- {output}")
        return 0
    except (NovelError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
