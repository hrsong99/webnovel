#!/usr/bin/env python3
"""Validate and build the canonical web-novel manuscript (stdlib only)."""

from __future__ import annotations

import argparse
import collections
import datetime as _datetime
import html
import json
import re
import shutil
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


def site_head(meta: dict[str, Any], page_title: str, prefix: str = "") -> str:
    title = html.escape(page_title)
    description = html.escape(str(meta["description"]), quote=True)
    cover = f"{prefix}assets/cover.svg"
    return f'''<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="{description}">
<meta name="theme-color" content="#211c18">
<meta property="og:type" content="book">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:image" content="{cover}">
<meta name="twitter:card" content="summary_large_image">
<title>{title}</title>
<link rel="icon" href="{prefix}assets/favicon.svg" type="image/svg+xml">
<link rel="manifest" href="{prefix}manifest.webmanifest">
<link rel="stylesheet" href="{prefix}assets/styles.css">'''


def chapter_prose_html(body: str) -> str:
    rendered = []
    for paragraph in re.split(r"\n\s*\n", body.strip()):
        stripped = paragraph.strip()
        if stripped == "***":
            rendered.append('<hr class="scene-break" aria-label="장면 전환">')
            continue
        css_class = ' class="dialogue"' if stripped.startswith(("“", '"', "‘")) else ""
        rendered.append(f"<p{css_class}>{html.escape(stripped).replace(chr(10), '<br>')}</p>")
    return "\n".join(rendered)


def landing_html(manuscript: Manuscript) -> str:
    meta = manuscript.metadata
    stats = manuscript_stats(manuscript)
    cards = "\n".join(
        f'''<a class="chapter-card" href="chapters/{chapter.number:02d}.html" data-chapter-link="{chapter.number}">
<span class="chapter-no">CH. {chapter.number:02d}</span>
<span class="chapter-title">{html.escape(chapter.title)} <span class="progress-note">읽음</span></span>
<span class="chapter-length">{chapter.korean_chars:,}자</span>
</a>'''
        for chapter in manuscript.chapters
    )
    schema = json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "Book",
            "name": meta["title"],
            "alternateName": meta.get("subtitle", ""),
            "author": {"@type": "Organization", "name": meta["author"]},
            "inLanguage": meta["language"],
            "description": meta["description"],
            "bookFormat": "EBook",
            "numberOfPages": len(manuscript.chapters),
        },
        ensure_ascii=False,
    ).replace("</", "<\\/")
    return f'''<!doctype html>
<html lang="{html.escape(str(meta['language']), quote=True)}">
<head>
{site_head(meta, f"{meta['title']} — {meta.get('subtitle', '')}")}
<script type="application/ld+json">{schema}</script>
<script defer src="assets/home.js"></script>
</head>
<body>
<a class="skip-link" href="#chapters">본문으로 건너뛰기</a>
<header class="site-header">
  <a class="brand" href="/"><span class="brand-mark">無</span><span>{html.escape(str(meta['title']))}</span></a>
  <nav class="header-links" aria-label="주요 메뉴"><a href="#chapters">목차</a><a class="optional" href="#about">작품 소개</a><a href="{meta['slug']}.epub" download>EPUB</a></nav>
</header>
<main>
<section class="hero">
  <div class="cover-wrap"><img class="cover" src="assets/cover.svg" alt="{html.escape(str(meta['title']))} 표지" width="1200" height="1800"></div>
  <div class="hero-copy">
    <p class="eyebrow">Korean Murim Web Novel · Volume One</p>
    <h1>{html.escape(str(meta['title']))}</h1>
    <p class="subtitle">{html.escape(str(meta.get('subtitle', '')))}</p>
    <p class="synopsis">{html.escape(str(meta['description']))}</p>
    <div class="meta-row"><span>전 {stats['chapter_count']}화</span><span>{stats['korean_characters']:,}자</span><span>무협 · 성장 · 제도 혁명</span></div>
    <div class="actions"><a class="button primary" href="chapters/01.html" data-resume>첫 화 읽기 →</a><a class="button secondary" href="#chapters">목차 보기</a></div>
  </div>
</section>
<section class="section" id="chapters">
  <p class="section-kicker">VOLUME ONE</p><h2>검성의 사과</h2>
  <div class="chapter-list">{cards}</div>
</section>
<section class="section" id="about">
  <div class="about-grid">
    <blockquote>“무림을 없애려면,<br>먼저 무인이 되어야 했다.”</blockquote>
    <div class="about-copy"><p>고수의 깨달음 아래에서 평범한 사람의 삶은 얼마나 가벼운가. 대장장이 진철은 가족을 죽인 두 사람만이 아니라, 그들을 무죄로 만든 질서를 겨눈다. 그리고 모든 내공이 영혼에 낸 상처에서 시작된다는 사실을 알게 된다.</p><p>이 웹사이트는 정본 원고에서 자동으로 만들어집니다. 새 회차가 저장소에 추가되면 목차와 전자책, 독서 페이지가 함께 갱신됩니다.</p>
      <div class="downloads"><a href="{meta['slug']}.epub" download>EPUB 내려받기</a><a href="{meta['slug']}.txt" download>TXT 내려받기</a><a href="{meta['slug']}.md" download>Markdown</a></div>
    </div>
  </div>
</section>
</main>
<footer class="site-footer"><span>© {html.escape(str(meta['author']))}</span><span>로그인 없이, 브라우저에만 독서 기록을 저장합니다.</span></footer>
</body></html>'''


def chapter_page_html(manuscript: Manuscript, chapter: Chapter) -> str:
    meta = manuscript.metadata
    chapters = manuscript.chapters
    toc_parts = []
    for item in chapters:
        current = ' aria-current="page"' if item.number == chapter.number else ""
        toc_parts.append(
            f'<a href="{item.number:02d}.html"{current}>제{item.number}화. {html.escape(item.title)}</a>'
        )
    toc = "".join(toc_parts)
    previous = next((item for item in chapters if item.number == chapter.number - 1), None)
    following = next((item for item in chapters if item.number == chapter.number + 1), None)
    prev_html = (
        f'<a class="prev" href="{previous.number:02d}.html"><small>이전화</small>← {html.escape(previous.title)}</a>'
        if previous else '<a class="prev" href="../"><small>작품 홈</small>← 표지로</a>'
    )
    next_html = (
        f'<a class="next" href="{following.number:02d}.html"><small>다음화</small>{html.escape(following.title)} →</a>'
        if following else '<a class="next" href="../"><small>제1권 완독</small>작품 홈 →</a>'
    )
    end_card = "" if following else '''<div class="end-card"><strong>제1권을 모두 읽었습니다.</strong><p>진철의 첫 균열은 이제 무림맹의 시선과 마주합니다.</p><a class="button secondary" href="../">작품 홈으로</a></div>'''
    return f'''<!doctype html>
<html lang="{html.escape(str(meta['language']), quote=True)}">
<head>{site_head(meta, f"제{chapter.number}화. {chapter.title} | {meta['title']}", "../")}<script defer src="../assets/reader.js"></script></head>
<body class="reader-page" data-chapter="{chapter.number}">
<a class="skip-link" href="#chapter-text">본문으로 건너뛰기</a>
<div class="read-progress" role="progressbar" aria-label="회차 읽기 진행률" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0"><span></span></div>
<header class="reader-bar"><div class="reader-bar-inner">
  <a class="reader-home" href="../">{html.escape(str(meta['title']))}</a>
  <span class="reader-position">제{chapter.number}화 / 전 {len(chapters)}화</span>
  <div class="reader-tools"><button class="tool-button" type="button" data-font-step="-1" aria-label="글자 작게">가−</button><button class="tool-button" type="button" data-font-step="1" aria-label="글자 크게">가+</button><button class="tool-button" type="button" data-action="theme" aria-label="읽기 테마 바꾸기">◐</button>
    <details class="toc-toggle"><summary aria-label="목차 열기">목차</summary><nav class="toc-panel" aria-label="회차 목차">{toc}</nav></details>
  </div>
</div></header>
<main class="reader-main" id="chapter-text">
  <header class="chapter-head"><p class="chapter-label">CHAPTER {chapter.number:02d}</p><h1>{html.escape(chapter.title)}</h1><p>{chapter.korean_chars:,}자 · 예상 독서 시간 {max(5, round(chapter.korean_chars / 500))}분</p></header>
  <article class="prose">{chapter_prose_html(chapter.body)}</article>
  <nav class="chapter-nav" aria-label="이전 및 다음 회차">{prev_html}{next_html}</nav>{end_card}
</main>
</body></html>'''


def build_website(manuscript: Manuscript, dist: Path) -> list[Path]:
    site_source = manuscript.root / "site"
    required = ("styles.css", "reader.js", "home.js", "cover.svg", "favicon.svg")
    missing = [name for name in required if not (site_source / name).is_file()]
    if missing:
        raise NovelError("missing website asset(s): " + ", ".join(missing))
    assets = dist / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    for name in required:
        shutil.copy2(site_source / name, assets / name)

    index = dist / "index.html"
    index.write_text(landing_html(manuscript), encoding="utf-8")
    chapter_dir = dist / "chapters"
    chapter_dir.mkdir(parents=True, exist_ok=True)
    chapter_files = []
    for chapter in manuscript.chapters:
        path = chapter_dir / f"{chapter.number:02d}.html"
        path.write_text(chapter_page_html(manuscript, chapter), encoding="utf-8")
        chapter_files.append(path)

    manifest = {
        "name": manuscript.metadata["title"],
        "short_name": manuscript.metadata["title"],
        "description": manuscript.metadata["description"],
        "lang": manuscript.metadata["language"],
        "start_url": "/",
        "display": "standalone",
        "background_color": "#f3efe5",
        "theme_color": "#211c18",
        "icons": [{"src": "/assets/favicon.svg", "sizes": "any", "type": "image/svg+xml"}],
    }
    manifest_path = dist / "manifest.webmanifest"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    robots = dist / "robots.txt"
    robots.write_text("User-agent: *\nAllow: /\n", encoding="utf-8")
    health = dist / "health.txt"
    health.write_text("ok\n", encoding="utf-8")
    return [index, *chapter_files, manifest_path, robots, health, *(assets / name for name in required)]


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
    if dist.exists():
        shutil.rmtree(dist)
    dist.mkdir(parents=True, exist_ok=True)
    slug = manuscript.metadata["slug"]
    outputs = [dist / f"{slug}.{extension}" for extension in ("md", "html", "txt", "epub")]
    outputs[0].write_text(combined_markdown(manuscript), encoding="utf-8")
    outputs[1].write_text(standalone_html(manuscript), encoding="utf-8")
    outputs[2].write_text(plain_text(manuscript), encoding="utf-8")
    build_epub(manuscript, outputs[3])
    outputs.extend(build_website(manuscript, dist))
    return outputs


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    default_root = Path(__file__).resolve().parents[1]
    for command, help_text in (
        ("validate", "validate metadata and chapter sources"),
        ("stats", "validate and print manuscript statistics as JSON"),
        ("build", "validate and build the public website plus Markdown, HTML, TXT, and EPUB"),
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
