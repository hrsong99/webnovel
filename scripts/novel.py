#!/usr/bin/env python3
"""Validate and publish every story in the catalog (stdlib only)."""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import hashlib
import html
import json
import re
import shutil
import sys
import tempfile
import uuid
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

HEADING_RE = re.compile(r"^# 제([1-9][0-9]*)화\.\s+(.+?)\s*$")
EN_HEADING_RE = re.compile(r"^# Chapter ([1-9][0-9]*)\.\s+(.+?)\s*$")
WORD_RE = re.compile(r"\b[A-Za-z0-9]+(?:[’'-][A-Za-z0-9]+)*\b")
KOREAN_RE = re.compile(r"[가-힣ㄱ-ㅎㅏ-ㅣ]")
SAFE_SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
PLACEHOLDER_RE = re.compile(r"(?i)(?:\b(?:TODO|TBD|FIXME|XXX|PLACEHOLDER)\b|(?:작성|집필|내용)\s*(?:예정|필요|추가)|추후\s*(?:작성|보강)|여기에\s*작성|미완성\s*본문)")
EDITORIAL_RE = re.compile(r"(?im)(?:^---\s*$|<!--|-->|^\s*(?:[-*]\s*)?\[[ xX]\]\s+|(?:편집\s*메모|작가\s*(?:노트|메모)|기획\s*(?:메모|의도)|장면\s*(?:목적|요약)|시놉시스|복선|POV|관점|등장인물|키워드)\s*[:：])")
REQUIRED_TEXT_FIELDS = ("slug", "title", "author", "language", "description", "genre", "quote", "about", "completion_title", "completion_text")


class NovelError(Exception):
    """A user-actionable catalog, manuscript, or configuration error."""


@dataclass(frozen=True)
class Chapter:
    number: int
    title: str
    body: str
    path: Path
    korean_chars: int = 0
    language: str = "ko"
    word_count: int = 0

    @property
    def heading(self) -> str:
        return f"Chapter {self.number}. {self.title}" if self.language == "en" else f"제{self.number}화. {self.title}"


@dataclass(frozen=True)
class Manuscript:
    root: Path
    metadata: dict[str, Any]
    chapters: tuple[Chapter, ...]


@dataclass(frozen=True)
class Story:
    slug: str
    root: Path
    primary: Manuscript
    english: Manuscript | None


def read_json(path: Path, label: str) -> Any:
    if not path.is_file():
        raise NovelError(f"missing {label}: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except UnicodeDecodeError as exc:
        raise NovelError(f"{label} must be UTF-8: {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise NovelError(f"invalid {label}: {path}: line {exc.lineno}, column {exc.colno}: {exc.msg}") from exc


def discover_catalog(root: Path) -> tuple[list[tuple[str, Path]], str]:
    root = root.resolve()
    raw = read_json(root / "catalog.json", "catalog.json")
    if not isinstance(raw, dict) or not isinstance(raw.get("stories"), list):
        raise NovelError("catalog.json must be an object with a 'stories' array")
    slugs = raw["stories"]
    legacy_slug = raw.get("legacy_alias_story")
    errors: list[str] = []
    if not slugs:
        errors.append("catalog.json 'stories' must not be empty")
    for slug in slugs:
        if not isinstance(slug, str) or not SAFE_SLUG_RE.fullmatch(slug):
            errors.append(f"invalid catalog story slug: {slug!r}")
    duplicates = [slug for slug, count in collections.Counter(slugs).items() if count > 1]
    if duplicates:
        errors.append("duplicate story slug(s) in catalog: " + ", ".join(map(str, duplicates)))
    if not isinstance(legacy_slug, str) or not SAFE_SLUG_RE.fullmatch(legacy_slug):
        errors.append("catalog.json 'legacy_alias_story' must be a path-safe story slug")
    elif legacy_slug not in slugs:
        errors.append(f"legacy alias story {legacy_slug!r} is not listed in catalog.json")
    discovered: list[tuple[str, Path]] = []
    for slug in slugs:
        if not isinstance(slug, str) or not SAFE_SLUG_RE.fullmatch(slug):
            continue
        story_root = root / "stories" / slug
        if not story_root.is_dir():
            errors.append(f"catalog story directory is missing: {story_root}")
        else:
            discovered.append((slug, story_root))
    listed = {slug for slug in slugs if isinstance(slug, str)}
    stories_root = root / "stories"
    if stories_root.is_dir():
        unlisted = sorted(path.parent.name for path in stories_root.glob("*/story.json") if path.parent.name not in listed)
        if unlisted:
            errors.append("unlisted story directory/directories with story.json: " + ", ".join(unlisted))
    if errors:
        raise NovelError("catalog validation failed:\n" + "\n".join(f"- {error}" for error in errors))
    assert isinstance(legacy_slug, str)
    return discovered, legacy_slug


def count_korean(text: str) -> int:
    return len(KOREAN_RE.findall(text))


def validate_metadata(raw: Any, path: Path, expected_slug: str, translation: bool = False) -> list[str]:
    if not isinstance(raw, dict):
        return [f"{path.name}: top-level value must be an object"]
    errors: list[str] = []
    for field in REQUIRED_TEXT_FIELDS:
        if not isinstance(raw.get(field), str) or not raw[field].strip():
            errors.append(f"{path.name} field {field!r} must be a non-empty string")
    if raw.get("slug") != expected_slug:
        errors.append(f"{path.name} slug {raw.get('slug')!r} does not match directory/catalog slug {expected_slug!r}")
    expected_language = "en" if translation else "ko"
    if raw.get("language") != expected_language:
        errors.append(f"{path.name} language must be {expected_language!r}, found {raw.get('language')!r}")
    int_fields = ("expected_chapters", "min_chapter_words", "max_chapter_words") if translation else ("expected_chapters", "min_chapter_chars", "max_chapter_chars")
    for field in int_fields:
        value = raw.get(field)
        if isinstance(value, bool) or not isinstance(value, int) or value < 1:
            errors.append(f"{path.name} field {field!r} must be a positive integer")
    low, high = ("min_chapter_words", "max_chapter_words") if translation else ("min_chapter_chars", "max_chapter_chars")
    if isinstance(raw.get(low), int) and isinstance(raw.get(high), int) and raw[low] > raw[high]:
        errors.append(f"{path.name} {low} must not exceed {high}")
    return errors


def repeated_phrases(body: str) -> list[str]:
    sentences = []
    for sentence in re.split(r"(?<=[.!?。！？])\s+|\n+", body):
        normalized = re.sub(r"\s+", " ", sentence).strip(" \t\"'“”‘’")
        if len(normalized) >= 12 and count_korean(normalized) >= 8:
            sentences.append(normalized)
    repeated = [text for text, count in collections.Counter(sentences).items() if count >= 3]
    tokens = re.findall(r"[가-힣A-Za-z0-9]+", body)
    windows = [" ".join(tokens[i:i + 6]) for i in range(max(0, len(tokens) - 5))]
    repeated.extend(text for text, count in collections.Counter(windows).items() if count >= 4 and count_korean(text) >= 10)
    return sorted(set(repeated), key=lambda value: (-len(value), value))


def read_manuscript(story_root: Path, expected_slug: str | None = None) -> Manuscript:
    story_root = story_root.resolve()
    expected_slug = expected_slug or story_root.name
    metadata_path = story_root / "story.json"
    metadata = read_json(metadata_path, "story.json")
    errors = validate_metadata(metadata, metadata_path, expected_slug)
    chapter_dir = story_root / "manuscript" / "chapters"
    files = sorted(chapter_dir.glob("*.md")) if chapter_dir.is_dir() else []
    if not files:
        errors.append(f"no Markdown chapters found in {chapter_dir}")
    chapters: list[Chapter] = []
    for path in files:
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            errors.append(f"{path.name}: chapter must be UTF-8")
            continue
        match = HEADING_RE.fullmatch(lines[0]) if lines else None
        if not match:
            errors.append(f"{path.name}: first line must match '# 제N화. 제목'")
            continue
        body = "\n".join(lines[1:]).strip()
        number = int(match.group(1))
        chars = count_korean(body)
        if not body:
            errors.append(f"{path.name}: chapter body is empty")
        low, high = metadata.get("min_chapter_chars"), metadata.get("max_chapter_chars")
        if isinstance(low, int) and isinstance(high, int) and not low <= chars <= high:
            errors.append(f"{path.name}: {chars} Korean characters; required range is {low}-{high}")
        if PLACEHOLDER_RE.search(body):
            errors.append(f"{path.name}: placeholder text found in prose")
        if EDITORIAL_RE.search(body):
            errors.append(f"{path.name}: editorial/planning metadata found in prose")
        repetitions = repeated_phrases(body)
        if repetitions:
            errors.append(f"{path.name}: suspicious repetition found: {repetitions[0][:80]!r}")
        chapters.append(Chapter(number, match.group(2).strip(), body, path, chars))
    _validate_sequence(chapters, metadata.get("expected_chapters"), errors, "")
    if errors:
        raise NovelError("manuscript validation failed:\n" + "\n".join(f"- {error}" for error in errors))
    return Manuscript(story_root, metadata, tuple(sorted(chapters, key=lambda chapter: chapter.number)))


def _validate_sequence(chapters: list[Chapter], expected: Any, errors: list[str], label: str) -> None:
    chapters.sort(key=lambda item: item.number)
    numbers = [item.number for item in chapters]
    duplicates = [number for number, count in collections.Counter(numbers).items() if count > 1]
    if duplicates:
        errors.append(f"{label}duplicate chapter number(s): " + ", ".join(map(str, duplicates)))
    if numbers and numbers != list(range(1, max(numbers) + 1)):
        errors.append(f"{label}chapter numbering gap or invalid starting number; found {numbers}")
    if isinstance(expected, int) and len(chapters) != expected:
        errors.append(f"{label}expected_chapters is {expected}, but found {len(chapters)}")


def read_translation(story_root: Path, language: str, expected_slug: str | None = None) -> Manuscript | None:
    expected_slug = expected_slug or story_root.name
    metadata_path = story_root / "locales" / f"{language}.json"
    if not metadata_path.is_file():
        return None
    metadata = read_json(metadata_path, f"translation metadata {metadata_path.name}")
    errors = validate_metadata(metadata, metadata_path, expected_slug, translation=True)
    chapter_dir = story_root / "manuscript" / "translations" / language / "chapters"
    files = sorted(chapter_dir.glob("*.md")) if chapter_dir.is_dir() else []
    if not files:
        errors.append(f"no translated chapters found in {chapter_dir}")
    chapters: list[Chapter] = []
    for path in files:
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            errors.append(f"{path.name}: translation must be UTF-8")
            continue
        match = EN_HEADING_RE.fullmatch(lines[0]) if lines else None
        if not match:
            errors.append(f"{path.name}: first line must match '# Chapter N. Title'")
            continue
        body = "\n".join(lines[1:]).strip()
        words = len(WORD_RE.findall(body))
        low, high = metadata.get("min_chapter_words"), metadata.get("max_chapter_words")
        if not body:
            errors.append(f"{path.name}: translated chapter body is empty")
        if isinstance(low, int) and isinstance(high, int) and not low <= words <= high:
            errors.append(f"{path.name}: {words} English words; required range is {low}-{high}")
        if PLACEHOLDER_RE.search(body) or re.search(r"(?i)\b(?:TODO|TBD|FIXME|translator(?:'s)? note)\b", body):
            errors.append(f"{path.name}: placeholder or translator note found in prose")
        sentences = [re.sub(r"\s+", " ", item).strip(" \t\"'“”‘’") for item in re.split(r"(?<=[.!?])\s+|\n+", body)]
        repeated = [item for item, count in collections.Counter(sentences).items() if count >= 3 and len(WORD_RE.findall(item)) >= 8]
        if repeated:
            errors.append(f"{path.name}: suspicious English repetition found: {repeated[0][:80]!r}")
        chapters.append(Chapter(int(match.group(1)), match.group(2).strip(), body, path, 0, language, words))
    _validate_sequence(chapters, metadata.get("expected_chapters"), errors, f"{language} ")
    if errors:
        raise NovelError("translation validation failed:\n" + "\n".join(f"- {error}" for error in errors))
    return Manuscript(story_root, metadata, tuple(chapters))


def load_reviewer_note(root: Path, language: str, number: int) -> str:
    path = root / "manuscript" / "reviewer-notes" / language / f"{number:02d}.md"
    if not path.is_file():
        raise NovelError(f"missing reviewer overview: {path}")
    lines = path.read_text(encoding="utf-8").splitlines()
    body = "\n".join(lines[1:]).strip() if lines and lines[0].startswith("# ") else ""
    if not body:
        raise NovelError(f"reviewer overview is empty or lacks a level-one heading: {path}")
    return body


def load_story(slug: str, story_root: Path) -> Story:
    primary = read_manuscript(story_root, slug)
    english = read_translation(story_root, "en", slug)
    if english and [chapter.number for chapter in english.chapters] != [chapter.number for chapter in primary.chapters]:
        raise NovelError(
            f"translation chapter numbers for {slug} must exactly match the Korean edition; "
            f"Korean={[chapter.number for chapter in primary.chapters]}, English={[chapter.number for chapter in english.chapters]}"
        )
    for edition in (primary, english):
        if edition:
            for chapter in edition.chapters:
                load_reviewer_note(story_root, edition.metadata["language"], chapter.number)
    assets = story_root / "assets"
    missing = [name for name in ("cover.svg",) if not (assets / name).is_file()]
    if english and not ((assets / "cover-en.svg").is_file() or (assets / "cover.svg").is_file()):
        missing.append("cover-en.svg or cover.svg")
    if missing:
        raise NovelError(f"missing story asset(s) for {slug}: " + ", ".join(missing))
    return Story(slug, story_root, primary, english)


def load_catalog(root: Path, selected: str | None = None) -> tuple[list[Story], str]:
    discovered, legacy_slug = discover_catalog(root)
    if selected and selected not in {slug for slug, _ in discovered}:
        raise NovelError(f"story {selected!r} is not listed in catalog.json")
    stories = [load_story(slug, path) for slug, path in discovered if not selected or slug == selected]
    return stories, legacy_slug


def manuscript_stats(manuscript: Manuscript) -> dict[str, Any]:
    chapters = [{"number": c.number, "title": c.title, "korean_characters": c.korean_chars, "words": c.word_count, "source": c.path.name} for c in manuscript.chapters]
    return {"slug": manuscript.metadata["slug"], "title": manuscript.metadata["title"], "language": manuscript.metadata["language"], "chapter_count": len(chapters), "korean_characters": sum(c.korean_chars for c in manuscript.chapters), "words": sum(c.word_count for c in manuscript.chapters), "chapters": chapters}


def story_stats(story: Story) -> dict[str, Any]:
    result = {"ko": manuscript_stats(story.primary)}
    if story.english:
        result["en"] = manuscript_stats(story.english)
    return result


def combined_markdown(manuscript: Manuscript) -> str:
    meta = manuscript.metadata
    parts = [f"# {meta['title']}"]
    if meta.get("subtitle"):
        parts.append(f"*{meta['subtitle']}*")
    parts += [f"**{'Author' if meta['language'] == 'en' else '저자'}:** {meta['author']}", str(meta["description"])]
    parts += [f"## {chapter.heading}\n\n{chapter.body}" for chapter in manuscript.chapters]
    return "\n\n".join(parts).rstrip() + "\n"


def plain_text(manuscript: Manuscript) -> str:
    meta = manuscript.metadata
    parts = [str(meta["title"])]
    if meta.get("subtitle"):
        parts.append(str(meta["subtitle"]))
    parts += [str(meta["author"]), str(meta["description"])]
    parts += [f"{chapter.heading}\n\n{chapter.body}" for chapter in manuscript.chapters]
    return "\n\n".join(parts).rstrip() + "\n"


def body_paragraphs(body: str) -> str:
    return "\n".join(f"<p>{html.escape(p).replace(chr(10), '<br />')}</p>" for p in re.split(r"\n\s*\n", body.strip()))


def standalone_html(manuscript: Manuscript) -> str:
    meta = manuscript.metadata
    toc = "".join(f'<li><a href="#chapter-{c.number}">{html.escape(c.heading)}</a></li>' for c in manuscript.chapters)
    chapters = "".join(f'<section id="chapter-{c.number}"><h2>{html.escape(c.heading)}</h2>{body_paragraphs(c.body)}</section>' for c in manuscript.chapters)
    return f'<!doctype html><html lang="{html.escape(meta["language"])}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>{html.escape(meta["title"])}</title><style>body{{font-family:serif;line-height:1.9;max-width:46rem;margin:auto;padding:2rem}}section{{margin:6rem 0}}p{{margin:.7em 0}}</style></head><body><header><h1>{html.escape(meta["title"])}</h1><p>{html.escape(meta["description"])}</p></header><nav><ol>{toc}</ol></nav><main>{chapters}</main></body></html>'


def build_epub(manuscript: Manuscript, destination: Path) -> None:
    meta = manuscript.metadata
    language = str(meta["language"])
    identifier_source = f"{meta['slug']}:{language}"
    identifier = f"urn:uuid:{uuid.uuid5(uuid.NAMESPACE_URL, identifier_source)}"
    modified = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    items = "".join(f'<item id="c{c.number}" href="chapter-{c.number:03d}.xhtml" media-type="application/xhtml+xml"/>' for c in manuscript.chapters)
    spine = "".join(f'<itemref idref="c{c.number}"/>' for c in manuscript.chapters)
    links = "".join(f'<li><a href="chapter-{c.number:03d}.xhtml">{html.escape(c.heading)}</a></li>' for c in manuscript.chapters)
    opf = f'<?xml version="1.0" encoding="utf-8"?><package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="book-id"><metadata xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:identifier id="book-id">{identifier}</dc:identifier><dc:title>{html.escape(meta["title"])}</dc:title><dc:creator>{html.escape(meta["author"])}</dc:creator><dc:language>{language}</dc:language><meta property="dcterms:modified">{modified}</meta></metadata><manifest><item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>{items}</manifest><spine>{spine}</spine></package>'
    nav = f'<?xml version="1.0" encoding="utf-8"?><html xmlns="http://www.w3.org/1999/xhtml"><head><title>{html.escape(meta["title"])}</title></head><body><nav xmlns:epub="http://www.idpf.org/2007/ops" epub:type="toc"><ol>{links}</ol></nav></body></html>'
    container = '<?xml version="1.0" encoding="UTF-8"?><container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles></container>'
    with zipfile.ZipFile(destination, "w") as archive:
        archive.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)
        archive.writestr("META-INF/container.xml", container, compress_type=zipfile.ZIP_DEFLATED)
        archive.writestr("OEBPS/content.opf", opf, compress_type=zipfile.ZIP_DEFLATED)
        archive.writestr("OEBPS/nav.xhtml", nav, compress_type=zipfile.ZIP_DEFLATED)
        for chapter in manuscript.chapters:
            document = f'<?xml version="1.0" encoding="utf-8"?><html xmlns="http://www.w3.org/1999/xhtml" lang="{language}"><head><title>{html.escape(chapter.heading)}</title></head><body><h1>{html.escape(chapter.heading)}</h1>{body_paragraphs(chapter.body)}</body></html>'
            archive.writestr(f"OEBPS/chapter-{chapter.number:03d}.xhtml", document, compress_type=zipfile.ZIP_DEFLATED)


def ui_copy(language: str) -> dict[str, str]:
    if language == "en":
        return {"catalog":"All stories", "chapters":"Chapters", "about":"About", "edition":"Read in Korean", "start":"Begin chapter one", "resume":"Continue reading", "read":"READ", "download":"Download", "previous":"Previous", "next":"Next", "home":"Book home", "overview":"Editorial chapter overview", "hint":"Spoilers · plot structure, decisions, and progression constraints", "unit":"words", "minutes":"min read", "language":"한국어"}
    return {"catalog":"전체 작품", "chapters":"목차", "about":"작품 소개", "edition":"Read in English", "start":"첫 화 읽기", "resume":"이어 읽기", "read":"읽음", "download":"내려받기", "previous":"이전화", "next":"다음화", "home":"작품 홈", "overview":"편집자용 회차 개요", "hint":"스포일러 · 주요 사건, 인물 선택, 성장 제약", "unit":"자", "minutes":"분", "language":"EN"}


def asset_url(name: str, versions: dict[str, str]) -> str:
    return f'/assets/{name}?v={versions[name]}' if name in versions else f"/assets/{name}"


def canonical_path(slug: str, language: str, chapter: int | None = None) -> str:
    base = f"/stories/{slug}/" + ("en/" if language == "en" else "")
    return base + (f"chapters/{chapter:02d}.html" if chapter else "")


def site_head(meta: dict[str, Any], title: str, canonical: str, versions: dict[str, str], cover: str) -> str:
    description = html.escape(meta["description"], quote=True)
    return f'<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="{description}"><meta property="og:type" content="book"><meta property="og:title" content="{html.escape(title, quote=True)}"><meta property="og:image" content="{cover}"><link rel="canonical" href="{canonical}"><link rel="icon" href="{asset_url("favicon.svg", versions)}"><link rel="stylesheet" href="{asset_url("styles.css", versions)}"><title>{html.escape(title)}</title>'


def simple_markdown_html(text: str) -> str:
    def inline(value: str) -> str:
        return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html.escape(value))
    blocks = []
    for block in re.split(r"\n\s*\n", text.strip()):
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        if lines and all(line.startswith(("- ", "* ")) for line in lines):
            blocks.append("<ul>" + "".join(f"<li>{inline(line[2:])}</li>" for line in lines) + "</ul>")
        else:
            blocks.append(f"<p>{inline(' '.join(lines))}</p>")
    return "".join(blocks)


def chapter_prose_html(body: str, language: str) -> str:
    rendered = []
    for paragraph in re.split(r"\n\s*\n", body.strip()):
        if paragraph.strip() == "***":
            rendered.append('<hr class="scene-break">')
        else:
            css = ' class="dialogue"' if paragraph.strip().startswith(("“", '"', "‘")) else ""
            rendered.append(f"<p{css}>{html.escape(paragraph.strip()).replace(chr(10), '<br>')}</p>")
    return "".join(rendered)


def landing_html(story: Story, manuscript: Manuscript, versions: dict[str, str]) -> str:
    meta, language = manuscript.metadata, manuscript.metadata["language"]
    ui = ui_copy(language); slug = story.slug
    canonical = canonical_path(slug, language)
    other = canonical_path(slug, "ko" if language == "en" else "en") if story.english else ""
    cover_name = "cover-en.svg" if language == "en" and (story.root / "assets" / "cover-en.svg").is_file() else "cover.svg"
    cover = f"/stories/{slug}/assets/{cover_name}"
    stats = manuscript_stats(manuscript); total = stats["words"] if language == "en" else stats["korean_characters"]
    cards = "".join(f'<a class="chapter-card" href="{canonical_path(slug, language, c.number)}" data-chapter-link="{c.number}"><span class="chapter-index">{c.number:02d}</span><span class="chapter-copy"><strong>{html.escape(c.title)}</strong><small>{(c.word_count if language == "en" else c.korean_chars):,} {ui["unit"]}</small></span><span class="progress-note">{ui["read"]}</span></a>' for c in manuscript.chapters)
    alternate = f'<link rel="alternate" hreflang="{"ko" if language == "en" else "en"}" href="{other}">' if other else ""
    language_link = f'<a class="language-link" href="{other}">{ui["edition"]}</a>' if other else ""
    head = site_head(meta, f"{meta['title']} — {meta.get('subtitle', '')}", canonical, versions, cover)
    return f'<!doctype html><html lang="{language}"><head>{head}{alternate}<script defer src="{asset_url("home.js", versions)}"></script></head><body class="library-page" data-story-slug="{slug}" data-language="{language}"><header class="site-header"><a class="brand" href="/"><span class="brand-mark">冊</span><span>{ui["catalog"]}</span></a><nav class="header-links"><a href="#chapters">{ui["chapters"]}</a><a href="#about">{ui["about"]}</a>{language_link}</nav></header><main><section class="hero"><div class="hero-copy"><p class="eyebrow">{html.escape(meta.get("eyebrow", ""))}</p><h1>{html.escape(meta["title"])}</h1><p class="subtitle">{html.escape(meta.get("subtitle", ""))}</p><p class="synopsis">{html.escape(meta["description"])}</p><div class="meta-row"><span>{len(manuscript.chapters)} {"chapters" if language == "en" else "화"}</span><span>{total:,} {ui["unit"]}</span><span>{html.escape(meta["genre"])}</span></div><div class="actions"><a class="button primary" data-resume href="{canonical_path(slug, language, 1)}">{ui["start"]} →</a></div></div><div class="cover-stage"><img class="cover" src="{cover}" alt="{html.escape(meta["title"])}"></div></section><section class="chapter-section" id="chapters"><div class="section-heading"><div><p class="section-kicker">{html.escape(meta.get("volume_title", ""))}</p><h2>{ui["chapters"]}</h2></div></div><div class="chapter-list">{cards}</div></section><section class="manifesto" id="about"><p class="manifesto-mark">“</p><blockquote>{html.escape(meta["quote"])}</blockquote><div class="manifesto-copy"><p>{html.escape(meta["about"])}</p><div class="downloads"><span>{ui["download"]}</span><a href="{canonical}{slug}.epub">EPUB</a><a href="{canonical}{slug}.txt">TXT</a><a href="{canonical}{slug}.md">MD</a></div></div></section></main><footer class="site-footer"><span>© {html.escape(meta["author"])}</span><a href="/">{ui["catalog"]}</a></footer></body></html>'


def chapter_page_html(story: Story, manuscript: Manuscript, chapter: Chapter, versions: dict[str, str]) -> str:
    meta, language, slug = manuscript.metadata, manuscript.metadata["language"], story.slug
    ui = ui_copy(language); canonical = canonical_path(slug, language, chapter.number)
    other = canonical_path(slug, "ko" if language == "en" else "en", chapter.number) if story.english else ""
    cover_name = "cover-en.svg" if language == "en" and (story.root / "assets" / "cover-en.svg").is_file() else "cover.svg"
    head = site_head(meta, f"{chapter.heading} | {meta['title']}", canonical, versions, f"/stories/{slug}/assets/{cover_name}")
    alternate = f'<link rel="alternate" hreflang="{"ko" if language == "en" else "en"}" href="{other}">' if other else ""
    toc_parts = []
    for item in manuscript.chapters:
        current = ' aria-current="page"' if item.number == chapter.number else ""
        toc_parts.append(f'<a href="{canonical_path(slug, language, item.number)}"{current}><span>{item.number:02d}</span>{html.escape(item.title)}</a>')
    toc = "".join(toc_parts)
    previous = next((c for c in manuscript.chapters if c.number == chapter.number - 1), None)
    following = next((c for c in manuscript.chapters if c.number == chapter.number + 1), None)
    home = canonical_path(slug, language)
    prev = f'<a class="prev" href="{canonical_path(slug, language, previous.number) if previous else home}"><small>{ui["previous"] if previous else ui["home"]}</small><span>← {html.escape(previous.title if previous else meta["title"])}</span></a>'
    nxt = f'<a class="next" href="{canonical_path(slug, language, following.number) if following else home}"><small>{ui["next"] if following else meta["completion_title"]}</small><span>{html.escape(following.title) if following else ui["home"]} →</span></a>'
    language_link = f'<a class="tool-button language-tool" href="{other}">{ui["language"]}</a>' if other else ""
    note = simple_markdown_html(load_reviewer_note(story.root, language, chapter.number))
    measure = chapter.word_count if language == "en" else chapter.korean_chars
    minutes = max(5, round(chapter.word_count / 220 if language == "en" else chapter.korean_chars / 500))
    end = "" if following else f'<div class="end-card"><strong>{html.escape(meta["completion_title"])}</strong><p>{html.escape(meta["completion_text"])}</p></div>'
    return f'<!doctype html><html lang="{language}"><head>{head}{alternate}<script defer src="{asset_url("reader.js", versions)}"></script></head><body class="reader-page" data-story-slug="{slug}" data-chapter="{chapter.number}" data-language="{language}"><div class="read-progress" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0"><span></span></div><header class="reader-bar"><div class="reader-bar-inner"><a class="reader-home" href="{home}"><span class="brand-mark">冊</span><span>{html.escape(meta["title"])}</span></a><span class="reader-position">{chapter.number:02d} / {len(manuscript.chapters):02d}</span><div class="reader-tools">{language_link}<button class="tool-button" data-font-step="-1">A−</button><button class="tool-button" data-font-step="1">A+</button><button class="tool-button" data-action="theme">◐</button><details class="toc-toggle"><summary>☰</summary><nav class="toc-panel">{toc}</nav></details></div></div></header><main class="reader-main"><header class="chapter-head"><p class="chapter-label">CHAPTER {chapter.number:02d}</p><h1>{html.escape(chapter.title)}</h1><p>{measure:,} {ui["unit"]} · {minutes} {ui["minutes"]}</p></header><details class="reviewer-overview"><summary><span><strong>{ui["overview"]}</strong><small>{ui["hint"]}</small></span></summary><div class="reviewer-body">{note}</div></details><article class="prose">{chapter_prose_html(chapter.body, language)}</article><nav class="chapter-nav">{prev}{nxt}</nav>{end}</main></body></html>'


def catalog_html(stories: list[Story], versions: dict[str, str]) -> str:
    cards = []
    for story in stories:
        meta = story.primary.metadata
        languages = [f'<a href="/stories/{story.slug}/">한국어</a>']
        if story.english:
            languages.append(f'<a href="/stories/{story.slug}/en/">English</a>')
        cards.append(f'<article class="catalog-card"><a class="catalog-cover" href="/stories/{story.slug}/"><img src="/stories/{story.slug}/assets/cover.svg" alt="{html.escape(meta["title"])}"></a><div><p class="eyebrow">{html.escape(meta.get("genre", ""))}</p><h2><a href="/stories/{story.slug}/">{html.escape(meta["title"])}</a></h2><p>{html.escape(meta["description"])}</p><nav class="catalog-languages">{"".join(languages)}</nav></div></article>')
    head = f'<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="한국어와 영어로 읽는 웹소설 작품 목록"><link rel="canonical" href="/"><link rel="icon" href="{asset_url("favicon.svg", versions)}"><link rel="stylesheet" href="{asset_url("styles.css", versions)}"><title>웹소설 서가</title>'
    return f'<!doctype html><html lang="ko"><head>{head}</head><body class="catalog-page"><header class="catalog-header"><p class="eyebrow">WEB NOVEL CATALOG</p><h1>이야기 서가</h1><p>읽고 싶은 작품과 언어를 선택하세요.</p></header><main class="catalog-grid">{"".join(cards)}</main></body></html>'


def write_edition(story: Story, manuscript: Manuscript, root: Path, versions: dict[str, str]) -> list[Path]:
    root.mkdir(parents=True, exist_ok=True); slug = story.slug
    outputs = [root / f"{slug}.{ext}" for ext in ("md", "html", "txt", "epub")]
    outputs[0].write_text(combined_markdown(manuscript), encoding="utf-8")
    outputs[1].write_text(standalone_html(manuscript), encoding="utf-8")
    outputs[2].write_text(plain_text(manuscript), encoding="utf-8")
    build_epub(manuscript, outputs[3])
    index = root / "index.html"; index.write_text(landing_html(story, manuscript, versions), encoding="utf-8"); outputs.append(index)
    chapter_root = root / "chapters"; chapter_root.mkdir()
    for chapter in manuscript.chapters:
        path = chapter_root / f"{chapter.number:02d}.html"; path.write_text(chapter_page_html(story, manuscript, chapter, versions), encoding="utf-8"); outputs.append(path)
    return outputs


def copy_legacy_aliases(story: Story, canonical: Path, dist: Path) -> list[Path]:
    outputs: list[Path] = []
    shutil.copytree(canonical / "chapters", dist / "chapters"); outputs.append(dist / "chapters")
    for ext in ("md", "html", "txt", "epub"):
        target = dist / f"{story.slug}.{ext}"; shutil.copy2(canonical / f"{story.slug}.{ext}", target); outputs.append(target)
    if story.english:
        shutil.copytree(canonical / "en", dist / "en"); outputs.append(dist / "en")
    shared_assets = dist / "assets"
    shutil.copy2(canonical / "assets" / "cover.svg", shared_assets / "cover.svg")
    outputs.append(shared_assets / "cover.svg")
    if (canonical / "assets" / "cover-en.svg").is_file():
        shutil.copy2(canonical / "assets" / "cover-en.svg", shared_assets / "cover-en.svg")
        outputs.append(shared_assets / "cover-en.svg")
    return outputs


def build_all(root: Path, stories: list[Story], legacy_slug: str) -> list[Path]:
    site = root / "site"
    required = ("styles.css", "reader.js", "home.js", "favicon.svg")
    missing = [name for name in required if not (site / name).is_file()]
    if missing:
        raise NovelError("missing shared website asset(s): " + ", ".join(missing))
    dist = root / "dist"
    temp = Path(tempfile.mkdtemp(prefix=".dist-build-", dir=root))
    outputs: list[Path] = []
    try:
        assets = temp / "assets"; shutil.copytree(site, assets)
        versions = {name: hashlib.sha256((assets / name).read_bytes()).hexdigest()[:12] for name in required}
        index = temp / "index.html"; index.write_text(catalog_html(stories, versions), encoding="utf-8"); outputs.append(index)
        for story in stories:
            story_dist = temp / "stories" / story.slug
            (story_dist / "assets").mkdir(parents=True)
            for cover in story.root.joinpath("assets").iterdir():
                if cover.is_file(): shutil.copy2(cover, story_dist / "assets" / cover.name)
            outputs.extend(write_edition(story, story.primary, story_dist, versions))
            if story.english:
                outputs.extend(write_edition(story, story.english, story_dist / "en", versions))
        legacy_story = next((story for story in stories if story.slug == legacy_slug), None)
        if legacy_story is None:
            raise NovelError(f"legacy alias story {legacy_slug!r} was not loaded")
        outputs.extend(copy_legacy_aliases(legacy_story, temp / "stories" / legacy_story.slug, temp))
        (temp / "manifest.webmanifest").write_text(json.dumps({"name":"웹소설 서가","short_name":"웹소설","start_url":"/","display":"standalone"}, ensure_ascii=False), encoding="utf-8")
        (temp / "robots.txt").write_text("User-agent: *\nAllow: /\n", encoding="utf-8")
        (temp / "health.txt").write_text("ok\n", encoding="utf-8")
        backup = root / ".dist-backup"
        if backup.exists(): shutil.rmtree(backup)
        if dist.exists(): dist.rename(backup)
        try:
            temp.rename(dist)
        except Exception:
            if backup.exists(): backup.rename(dist)
            raise
        if backup.exists(): shutil.rmtree(backup)
        return [dist / path.relative_to(temp) if path.is_relative_to(temp) else path for path in outputs]
    except Exception:
        if temp.exists(): shutil.rmtree(temp)
        raise


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    default_root = Path(__file__).resolve().parents[1]
    for name, help_text in (("validate", "validate catalog stories"), ("stats", "print catalog story statistics"), ("build", "build the complete catalog atomically")):
        sub = commands.add_parser(name, help=help_text); sub.add_argument("--root", type=Path, default=default_root, help=argparse.SUPPRESS)
        if name != "build": sub.add_argument("--story", help="select one catalog slug")
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = make_parser().parse_args(argv)
    try:
        stories, legacy_slug = load_catalog(args.root, getattr(args, "story", None))
        if args.command == "validate":
            for story in stories:
                stats = story_stats(story); message = f"VALID {story.slug}: {stats['ko']['chapter_count']} Korean chapter(s), {stats['ko']['korean_characters']} Korean characters"
                if "en" in stats: message += f"; {stats['en']['chapter_count']} English chapter(s), {stats['en']['words']} words"
                print(message)
        elif args.command == "stats":
            payload = {"stories": {story.slug: story_stats(story) for story in stories}}
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            outputs = build_all(args.root.resolve(), stories, legacy_slug)
            print(f"BUILT {len(stories)} story/stories, {len(outputs)} tracked output(s): {args.root.resolve() / 'dist'}")
        return 0
    except (NovelError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr); return 1


if __name__ == "__main__":
    raise SystemExit(main())
