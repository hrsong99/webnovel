import json
import re
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ElementTree
import zipfile
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "novel.py"
DISPLAY = {
    "genre": "시험 장르", "quote": "시험 인용문", "about": "시험 작품 소개",
    "completion_title": "완독", "completion_text": "완결 안내",
}


class NovelPipelineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "site").mkdir()
        for name in ("styles.css", "reader.js", "home.js"):
            (self.root / "site" / name).write_text(f"/* {name} */\n", encoding="utf-8")
        (self.root / "site" / "favicon.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg"/>', encoding="utf-8")
        self.make_story("test-novel")
        self.write_catalog(["test-novel"])

    def tearDown(self):
        self.temp.cleanup()

    def write_catalog(self, slugs, legacy="test-novel", projects=None, retired=None):
        if legacy not in slugs:
            legacy = slugs[0]
        payload = {
            "legacy_alias_story": legacy,
            "stories": slugs,
            "projects": projects or [],
            "retired_stories": retired or [],
        }
        (self.root / "catalog.json").write_text(json.dumps(payload), encoding="utf-8")

    def make_story(self, slug, title="시험 소설", english=False):
        story = self.root / "stories" / slug
        (story / "manuscript" / "chapters").mkdir(parents=True)
        (story / "manuscript" / "reviewer-notes" / "ko").mkdir(parents=True)
        (story / "assets").mkdir()
        self.write_artifacts(slug)
        (story / "assets" / "cover.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg"/>', encoding="utf-8")
        metadata = {
            "slug": slug, "title": title, "author": "테스트 작가", "language": "ko",
            "description": "빌드 검증용 소설", "volume_title": "시험 권",
            "min_chapter_chars": 20, "max_chapter_chars": 200, "expected_chapters": 2,
            **DISPLAY,
        }
        (story / "story.json").write_text(json.dumps(metadata, ensure_ascii=False), encoding="utf-8")
        bodies = ("가나다라마바사아자차카타파하 이야기가 조용히 시작되었다.", "새로운 인물들이 마을에 도착하고 오래된 문을 힘껏 열었다.")
        for number, (chapter_title, body) in enumerate(zip(("시작", "도착"), bodies), 1):
            self.write_chapter(slug, number, chapter_title, body)
            self.write_note(story, "ko", number, "주요 사건과 인물 선택을 설명하는 검증용 개요입니다.")
        if english:
            self.add_english(slug)
        return story

    def write_artifacts(self, slug, names=("story-bible.md", "outline.md", "craft-overlay.md", "continuity-ledger.md")):
        manuscript = self.root / "stories" / slug / "manuscript"
        manuscript.mkdir(parents=True, exist_ok=True)
        for name in names:
            (manuscript / name).write_text(f"# {name}\n\n검증용 기획 문서입니다.\n", encoding="utf-8")

    def add_english(self, slug):
        story = self.root / "stories" / slug
        (story / "assets" / "cover-en.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg"/>', encoding="utf-8")
        (story / "locales").mkdir(exist_ok=True)
        en_display = {"genre": "Test genre", "quote": "Test quote", "about": "Test about", "completion_title": "Complete", "completion_text": "Completion copy"}
        metadata = {"slug": slug, "title": "Test Novel", "subtitle": "English Edition", "author": "Test Author", "language": "en", "description": "A bilingual fixture.", "volume_title": "Test Volume", "expected_chapters": 2, "min_chapter_words": 5, "max_chapter_words": 100, **en_display}
        (story / "locales" / "en.json").write_text(json.dumps(metadata), encoding="utf-8")
        chapters = story / "manuscript" / "translations" / "en" / "chapters"
        notes = story / "manuscript" / "reviewer-notes" / "en"
        chapters.mkdir(parents=True); notes.mkdir(parents=True)
        for number, title in ((1, "Beginning"), (2, "Arrival")):
            (chapters / f"{number:02d}.md").write_text(f"# Chapter {number}. {title}\n\nThe translated chapter contains enough natural English words for validation.\n", encoding="utf-8")
            self.write_note(story, "en", number, "This explains the plot structure and the character decision.")

    def write_note(self, story, language, number, body):
        path = story / "manuscript" / "reviewer-notes" / language / f"{number:02d}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"# Chapter overview\n\n{body}\n", encoding="utf-8")

    def write_chapter(self, slug, number, title, body, filename=None):
        path = self.root / "stories" / slug / "manuscript" / "chapters" / (filename or f"{number:03d}.md")
        path.write_text(f"# 제{number}화. {title}\n\n{body}\n", encoding="utf-8")

    def add_illustration(self, slug="test-novel"):
        story = self.root / "stories" / slug
        scenes = story / "assets" / "scenes"; scenes.mkdir()
        (scenes / "chapter-one.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg"/>', encoding="utf-8")
        payload = {"version": 1, "illustrations": [{
            "id": "ch01-scene", "chapter": 1,
            "after_paragraph": {"ko": 1},
            "asset": "scenes/chapter-one.svg",
            "alt": {"ko": "시험 장면 삽화"},
            "caption": {"ko": "첫 장면"},
            "provenance": {"provider": "test", "model": "fixture", "prompt_id": "scene-1", "generated_at": "2026-01-01"},
        }]}
        (story / "manuscript" / "illustrations.json").write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        self.write_artifacts(slug, names=("visual-bible.md",))

    def add_glossary(self, slug="test-novel"):
        story = self.root / "stories" / slug
        payload = {"version": 1, "entries": [
            {"term": "이야기가", "translation": "the story", "note": "A longer matching phrase."},
            {"term": "이야기", "translation": "story"},
            {"term": "인물", "translation": "character", "note": "A person in a narrative."},
        ]}
        path = story / "manuscript" / "glossary.en.json"
        path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        return path

    def metadata(self, slug="test-novel"):
        path = self.root / "stories" / slug / "story.json"
        return path, json.loads(path.read_text(encoding="utf-8"))

    def run_cli(self, command, *args):
        return subprocess.run([sys.executable, str(SCRIPT), command, "--root", str(self.root), *args], text=True, capture_output=True, check=False)

    # Existing behavior coverage, adjusted to catalog fixtures.
    def test_validate_and_stats_succeed(self):
        result = self.run_cli("validate")
        self.assertEqual(result.returncode, 0, result.stderr)
        stats = self.run_cli("stats")
        payload = json.loads(stats.stdout)["stories"]["test-novel"]["ko"]
        self.assertEqual(payload["chapter_count"], 2)
        self.assertGreater(payload["korean_characters"], 40)

    def test_rejects_numbering_gap_and_expected_count_mismatch(self):
        path, metadata = self.metadata(); metadata["expected_chapters"] = 3
        path.write_text(json.dumps(metadata, ensure_ascii=False), encoding="utf-8")
        (path.parent / "manuscript" / "chapters" / "002.md").unlink()
        self.write_chapter("test-novel", 3, "건너뜀", "한글문자가충분히들어있는세번째장의본문입니다 새로운 사건이 일어났다.")
        result = self.run_cli("validate")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("numbering gap", result.stderr); self.assertIn("expected_chapters", result.stderr)

    def test_rejects_placeholders_and_editorial_metadata(self):
        self.write_chapter("test-novel", 1, "시작", "가나다라마바사아자차카타파하. TODO: 결말을 작성할 것.")
        self.write_chapter("test-novel", 2, "도착", "가나다라마바사아자차카타파하. 편집 메모: 시점을 바꿀 것.")
        result = self.run_cli("validate")
        self.assertIn("placeholder", result.stderr); self.assertIn("editorial/planning metadata", result.stderr)

    def test_rejects_korean_character_bounds(self):
        path, metadata = self.metadata(); metadata["min_chapter_chars"] = 80
        path.write_text(json.dumps(metadata, ensure_ascii=False), encoding="utf-8")
        self.assertIn("Korean characters", self.run_cli("validate").stderr)

    def test_optional_outline_contract_enforces_fields_and_chapter_parity(self):
        path = self.root / "stories" / "test-novel" / "manuscript" / "outline.json"
        fields = {
            "near_promise": "즉시 약속", "want": "현재 욕망", "pressure": "압박",
            "choice": "선택", "delta": "변화", "local_payoff": "현재 보상",
            "persistence": "지속 결과", "next_pressure": "다음 압박",
        }
        payload = {"version": 1, "chapters": [
            {"number": 1, "title": "시작", **fields},
            {"number": 2, "title": "도착", **fields},
        ]}
        path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        valid = self.run_cli("validate")
        self.assertEqual(valid.returncode, 0, valid.stderr)

        del payload["chapters"][0]["delta"]
        path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        missing = self.run_cli("validate")
        self.assertNotEqual(missing.returncode, 0)
        self.assertIn("delta must be a non-empty string", missing.stderr)

        payload["chapters"][0]["delta"] = "변화"
        payload["chapters"].pop()
        path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        parity = self.run_cli("validate")
        self.assertNotEqual(parity.returncode, 0)
        self.assertIn("chapter numbers must exactly match Korean chapters", parity.stderr)

        payload["chapters"].append({"number": 2, "title": "잘못된 제목", **fields})
        path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        title_mismatch = self.run_cli("validate")
        self.assertNotEqual(title_mismatch.returncode, 0)
        self.assertIn("does not match manuscript title", title_mismatch.stderr)

    def test_rejects_suspicious_phrase_repetition(self):
        phrase = "검은 문 너머에서 낯선 목소리가 들려왔다"
        self.write_chapter("test-novel", 1, "반복", ". ".join([phrase] * 4) + ".")
        self.assertIn("suspicious repetition", self.run_cli("validate").stderr)

    def test_build_creates_readable_outputs_and_valid_epub(self):
        result = self.run_cli("build")
        self.assertEqual(result.returncode, 0, result.stderr)
        canonical = self.root / "dist" / "stories" / "test-novel"
        expected = {"test-novel.md", "test-novel.html", "test-novel.txt", "test-novel.epub", "index.html"}
        self.assertTrue(expected.issubset({path.name for path in canonical.iterdir()}))
        home = canonical.joinpath("index.html").read_text(encoding="utf-8")
        self.assertRegex(home, r'/assets/styles\.css\?v=[0-9a-f]{12}')
        self.assertIn('rel="canonical" href="/stories/test-novel/"', home)
        chapter = canonical.joinpath("chapters/01.html").read_text(encoding="utf-8")
        self.assertIn("/stories/test-novel/chapters/02.html", chapter)
        self.assertIn('data-action="focus"', chapter)
        self.assertIn('data-focus-unit="1"', chapter)
        self.assertIn('class="focus-guide"', chapter)
        with zipfile.ZipFile(canonical / "test-novel.epub") as archive:
            self.assertIsNone(archive.testzip())
            self.assertEqual(archive.infolist()[0].filename, "mimetype")
            self.assertEqual(archive.infolist()[0].compress_type, zipfile.ZIP_STORED)
            for name in ("META-INF/container.xml", "OEBPS/content.opf", "OEBPS/nav.xhtml", "OEBPS/chapter-001.xhtml"):
                ElementTree.fromstring(archive.read(name))

    def test_asset_urls_change_when_contents_change(self):
        self.assertEqual(self.run_cli("build").returncode, 0)
        path = self.root / "dist" / "index.html"
        first_match = re.search(r'/assets/styles\.css\?v=([0-9a-f]{12})', path.read_text(encoding="utf-8"))
        self.assertIsNotNone(first_match)
        assert first_match is not None
        first = first_match.group(1)
        (self.root / "site" / "styles.css").write_text("body{color:rebeccapurple}", encoding="utf-8")
        self.assertEqual(self.run_cli("build").returncode, 0)
        second_match = re.search(r'/assets/styles\.css\?v=([0-9a-f]{12})', path.read_text(encoding="utf-8"))
        self.assertIsNotNone(second_match)
        assert second_match is not None
        second = second_match.group(1)
        self.assertNotEqual(first, second)

    def test_optional_illustrations_are_validated_copied_and_placed(self):
        self.add_illustration()
        result = self.run_cli("build")
        self.assertEqual(result.returncode, 0, result.stderr)
        chapter = (self.root / "dist" / "stories" / "test-novel" / "chapters" / "01.html").read_text(encoding="utf-8")
        self.assertIn('class="story-illustration"', chapter)
        self.assertIn('/stories/test-novel/assets/scenes/chapter-one.svg', chapter)
        self.assertLess(chapter.index('data-focus-unit="1"'), chapter.index('class="story-illustration"'))
        self.assertTrue((self.root / "dist" / "stories" / "test-novel" / "assets" / "scenes" / "chapter-one.svg").is_file())
        with zipfile.ZipFile(self.root / "dist" / "stories" / "test-novel" / "test-novel.epub") as archive:
            self.assertIn("OEBPS/images/scenes/chapter-one.svg", archive.namelist())
            self.assertIn(b"images/scenes/chapter-one.svg", archive.read("OEBPS/chapter-001.xhtml"))
            ElementTree.fromstring(archive.read("OEBPS/chapter-001.xhtml"))

    def test_optional_glossary_is_validated_and_only_annotates_korean_reader_pages(self):
        self.add_english("test-novel")
        self.add_glossary()
        result = self.run_cli("build")
        self.assertEqual(result.returncode, 0, result.stderr)
        ko_chapter = (self.root / "dist" / "stories" / "test-novel" / "chapters" / "01.html").read_text(encoding="utf-8")
        en_chapter = (self.root / "dist" / "stories" / "test-novel" / "en" / "chapters" / "01.html").read_text(encoding="utf-8")
        standalone = (self.root / "dist" / "stories" / "test-novel" / "test-novel.html").read_text(encoding="utf-8")
        self.assertIn('class="glossary-term"', ko_chapter)
        self.assertIn('data-term="이야기가"', ko_chapter)
        self.assertNotIn('data-term="이야기"', ko_chapter)
        self.assertEqual(ko_chapter.count('data-term="이야기가"'), 1)
        self.assertIn('class="glossary-dialog"', ko_chapter)
        self.assertNotIn('class="glossary-term"', en_chapter)
        self.assertNotIn('class="glossary-dialog"', en_chapter)
        self.assertNotIn('class="glossary-term"', standalone)

    def test_glossary_rejects_duplicates_empty_translations_and_unused_terms(self):
        path = self.add_glossary()
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["entries"] += [
            {"term": "인물", "translation": "duplicate"},
            {"term": "마교", "translation": ""},
        ]
        path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        result = self.run_cli("validate")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("duplicate glossary term", result.stderr)
        self.assertIn("translation must be a non-empty string", result.stderr)
        self.assertIn("unused glossary term", result.stderr)

    def test_illustration_manifest_rejects_missing_or_unsafe_assets(self):
        self.add_illustration()
        path = self.root / "stories" / "test-novel" / "manuscript" / "illustrations.json"
        payload = json.loads(path.read_text(encoding="utf-8")); payload["illustrations"][0]["asset"] = "../cover.svg"
        path.write_text(json.dumps(payload), encoding="utf-8")
        result = self.run_cli("validate")
        self.assertNotEqual(result.returncode, 0); self.assertIn("beneath assets/scenes", result.stderr)

    def test_bilingual_illustrations_require_and_render_both_languages(self):
        self.add_english("test-novel"); self.add_illustration()
        path = self.root / "stories" / "test-novel" / "manuscript" / "illustrations.json"
        missing = self.run_cli("validate")
        self.assertNotEqual(missing.returncode, 0); self.assertIn("after_paragraph.en", missing.stderr)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["illustrations"][0]["after_paragraph"]["en"] = 1
        payload["illustrations"][0]["alt"]["en"] = "Test scene illustration"
        path.write_text(json.dumps(payload), encoding="utf-8")
        result = self.run_cli("build")
        self.assertEqual(result.returncode, 0, result.stderr)
        chapter = (self.root / "dist" / "stories" / "test-novel" / "en" / "chapters" / "01.html").read_text(encoding="utf-8")
        self.assertIn('alt="Test scene illustration"', chapter)

    def test_bilingual_build_and_reviewer_overviews(self):
        self.add_english("test-novel")
        result = self.run_cli("build")
        self.assertEqual(result.returncode, 0, result.stderr)
        en = self.root / "dist" / "stories" / "test-novel" / "en"
        self.assertIn('lang="en"', (en / "index.html").read_text(encoding="utf-8"))
        chapter = (en / "chapters" / "01.html").read_text(encoding="utf-8")
        self.assertIn("Editorial chapter overview", chapter)
        self.assertIn("/stories/test-novel/chapters/01.html", chapter)
        self.assertTrue((en / "test-novel.epub").is_file())

    def test_missing_or_invalid_metadata_is_a_clear_cli_error(self):
        (self.root / "stories" / "test-novel" / "story.json").unlink()
        result = self.run_cli("validate")
        self.assertNotEqual(result.returncode, 0); self.assertIn("story.json", result.stderr); self.assertNotIn("Traceback", result.stderr)

    # Multi-story architecture coverage.
    def test_catalog_order_and_story_selection(self):
        self.make_story("second-story", "두 번째 이야기")
        self.write_catalog(["second-story", "test-novel"])
        result = self.run_cli("validate", "--story", "second-story")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("second-story", result.stdout); self.assertNotIn("test-novel", result.stdout)
        self.assertEqual(self.run_cli("build", "--story", "test-novel").returncode, 2)
        build = self.run_cli("build"); self.assertEqual(build.returncode, 0, build.stderr)
        catalog = (self.root / "dist" / "index.html").read_text(encoding="utf-8")
        self.assertLess(catalog.index("두 번째 이야기"), catalog.index("시험 소설"))
        self.assertTrue((self.root / "dist" / "stories" / "second-story" / "index.html").is_file())
        legacy = (self.root / "dist" / "chapters" / "01.html").read_text(encoding="utf-8")
        self.assertIn('/stories/test-novel/chapters/01.html', legacy)

    def test_two_story_validation_and_full_build(self):
        self.make_story("second-story", "두 번째 이야기", english=True)
        self.write_catalog(["test-novel", "second-story"])
        self.assertEqual(self.run_cli("validate").returncode, 0)
        self.assertEqual(self.run_cli("build").returncode, 0)
        self.assertTrue((self.root / "dist" / "stories" / "second-story" / "en" / "chapters" / "02.html").is_file())

    def test_legacy_aliases_are_primary_story_only_and_canonical(self):
        self.add_english("test-novel")
        self.make_story("second-story", "두 번째 이야기")
        self.write_catalog(["test-novel", "second-story"])
        self.assertEqual(self.run_cli("build").returncode, 0)
        dist = self.root / "dist"
        for path in (dist / "chapters" / "01.html", dist / "en" / "index.html", dist / "en" / "chapters" / "01.html", dist / "test-novel.md", dist / "test-novel.html", dist / "test-novel.txt", dist / "test-novel.epub", dist / "assets" / "cover.svg", dist / "assets" / "cover-en.svg"):
            self.assertTrue(path.is_file(), path)
        alias = (dist / "chapters" / "01.html").read_text(encoding="utf-8")
        self.assertIn('rel="canonical" href="/stories/test-novel/chapters/01.html"', alias)
        self.assertIn('/assets/reader.js?v=', alias)
        self.assertNotIn("second-story.md", {path.name for path in dist.iterdir()})

    def test_story_scoped_storage_keys_and_legacy_fallback(self):
        self.assertEqual(self.run_cli("build").returncode, 0)
        home = (self.root / "dist" / "stories" / "test-novel" / "index.html").read_text(encoding="utf-8")
        chapter = (self.root / "dist" / "stories" / "test-novel" / "chapters" / "01.html").read_text(encoding="utf-8")
        self.assertIn('data-story-slug="test-novel"', home); self.assertIn('data-story-slug="test-novel"', chapter)
        source_site = SCRIPT.parents[1] / "site"
        home_js = (source_site / "home.js").read_text(encoding="utf-8")
        reader_js = (source_site / "reader.js").read_text(encoding="utf-8")
        for source in (home_js, reader_js): self.assertIn("webnovel:${slug}", source)
        self.assertIn("slug === 'murim-abolitionist'", home_js); self.assertIn("murim-reader-settings", reader_js)

    def test_bad_catalog_duplicate_and_slug_mismatch_errors(self):
        self.write_catalog(["test-novel", "test-novel"])
        duplicate = self.run_cli("validate")
        self.assertNotEqual(duplicate.returncode, 0); self.assertIn("duplicate story slug", duplicate.stderr)
        self.write_catalog(["test-novel"])
        path, metadata = self.metadata(); metadata["slug"] = "wrong-slug"
        path.write_text(json.dumps(metadata, ensure_ascii=False), encoding="utf-8")
        mismatch = self.run_cli("validate")
        self.assertNotEqual(mismatch.returncode, 0); self.assertIn("does not match directory/catalog slug", mismatch.stderr)

    def test_unlisted_story_language_and_translation_parity_fail(self):
        self.make_story("unlisted-story")
        unlisted = self.run_cli("validate")
        self.assertNotEqual(unlisted.returncode, 0); self.assertIn("unlisted story", unlisted.stderr)
        self.write_catalog(["test-novel", "unlisted-story"])
        path, metadata = self.metadata(); metadata["language"] = "en"
        path.write_text(json.dumps(metadata, ensure_ascii=False), encoding="utf-8")
        wrong_language = self.run_cli("validate")
        self.assertNotEqual(wrong_language.returncode, 0); self.assertIn("language must be 'ko'", wrong_language.stderr)
        metadata["language"] = "ko"; path.write_text(json.dumps(metadata, ensure_ascii=False), encoding="utf-8")
        self.add_english("test-novel")
        en_path = self.root / "stories" / "test-novel" / "locales" / "en.json"
        en_meta = json.loads(en_path.read_text(encoding="utf-8")); en_meta["expected_chapters"] = 1
        en_path.write_text(json.dumps(en_meta), encoding="utf-8")
        (self.root / "stories" / "test-novel" / "manuscript" / "translations" / "en" / "chapters" / "02.md").unlink()
        (self.root / "stories" / "test-novel" / "manuscript" / "reviewer-notes" / "en" / "02.md").unlink()
        parity = self.run_cli("validate")
        self.assertNotEqual(parity.returncode, 0); self.assertIn("must exactly match", parity.stderr)

    def test_planning_and_retired_story_lifecycles_are_valid_but_not_published(self):
        planning = self.make_story("planning-story", "기획 이야기")
        retired = self.make_story("retired-story", "은퇴 이야기")
        for story, status in ((planning, "planning"), (retired, "retired")):
            metadata_path = story / "story.json"
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            metadata["status"] = status
            metadata_path.write_text(json.dumps(metadata, ensure_ascii=False), encoding="utf-8")
        self.write_catalog(["test-novel"], projects=["planning-story"], retired=["retired-story"])

        validation = self.run_cli("validate")
        self.assertEqual(validation.returncode, 0, validation.stderr)
        self.assertNotIn("planning-story", validation.stdout)
        self.assertNotIn("retired-story", validation.stdout)
        build = self.run_cli("build")
        self.assertEqual(build.returncode, 0, build.stderr)
        self.assertFalse((self.root / "dist" / "stories" / "planning-story").exists())
        self.assertFalse((self.root / "dist" / "stories" / "retired-story").exists())

        metadata_path = planning / "story.json"
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        metadata["status"] = "published"
        metadata_path.write_text(json.dumps(metadata, ensure_ascii=False), encoding="utf-8")
        mismatch = self.run_cli("validate")
        self.assertNotEqual(mismatch.returncode, 0)
        self.assertIn("status must be 'planning'", mismatch.stderr)

    def test_repository_catalog_records_published_planning_and_retired_stories(self):
        production = json.loads((SCRIPT.parents[1] / "catalog.json").read_text(encoding="utf-8"))
        self.assertEqual(production["legacy_alias_story"], "murim-abolitionist")
        self.assertEqual(production["stories"], ["murim-abolitionist", "seven-masters-returned"])
        self.assertEqual(production["projects"], [])
        self.assertEqual(production["retired_stories"], ["seven-regressors-fell"])

    def test_published_story_requires_planning_artifacts_or_a_recorded_exception(self):
        ledger = self.root / "stories" / "test-novel" / "manuscript" / "continuity-ledger.md"
        ledger.unlink()
        missing = self.run_cli("validate")
        self.assertNotEqual(missing.returncode, 0)
        self.assertIn("missing manuscript/continuity-ledger.md", missing.stderr)

        path, metadata = self.metadata()
        metadata["artifact_exceptions"] = {"continuity-ledger.md": ""}
        path.write_text(json.dumps(metadata, ensure_ascii=False), encoding="utf-8")
        empty_reason = self.run_cli("validate")
        self.assertNotEqual(empty_reason.returncode, 0)
        self.assertIn("must give a non-empty reason", empty_reason.stderr)

        metadata["artifact_exceptions"] = {"continuity-ledger.md": "Recorded gap: continuity lives in the story bible."}
        path.write_text(json.dumps(metadata, ensure_ascii=False), encoding="utf-8")
        recorded = self.run_cli("validate")
        self.assertEqual(recorded.returncode, 0, recorded.stderr)

        ledger.write_text("# ledger\n", encoding="utf-8")
        stale = self.run_cli("validate")
        self.assertNotEqual(stale.returncode, 0)
        self.assertIn("remove the exception", stale.stderr)

    def test_visual_bible_is_required_only_when_illustrations_exist(self):
        self.add_illustration()
        (self.root / "stories" / "test-novel" / "manuscript" / "visual-bible.md").unlink()
        result = self.run_cli("validate")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing manuscript/visual-bible.md", result.stderr)

    def test_promote_check_reports_blockers_then_passes(self):
        planning = self.make_story("planning-story", "기획 이야기")
        for path in (planning / "manuscript" / "chapters").glob("*.md"):
            path.unlink()
        (planning / "manuscript" / "craft-overlay.md").unlink()
        metadata_path = planning / "story.json"
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        metadata["status"] = "planning"
        metadata_path.write_text(json.dumps(metadata, ensure_ascii=False), encoding="utf-8")
        self.write_catalog(["test-novel"], projects=["planning-story"])

        blocked = self.run_cli("promote-check", "--story", "planning-story")
        self.assertNotEqual(blocked.returncode, 0)
        self.assertIn("NOT PROMOTABLE planning-story (currently in projects)", blocked.stderr)
        self.assertIn("missing manuscript/craft-overlay.md", blocked.stderr)
        self.assertIn("no Markdown chapters found", blocked.stderr)

        unknown = self.run_cli("promote-check", "--story", "absent-story")
        self.assertNotEqual(unknown.returncode, 0)
        self.assertIn("not listed in any catalog.json lifecycle bucket", unknown.stderr)

        ready = self.run_cli("promote-check", "--story", "test-novel")
        self.assertEqual(ready.returncode, 0, ready.stderr)
        self.assertIn("PROMOTABLE test-novel (currently in stories)", ready.stdout)

    def test_validation_failure_does_not_replace_existing_dist(self):
        dist = self.root / "dist"; dist.mkdir(); marker = dist / "keep.txt"; marker.write_text("old build", encoding="utf-8")
        self.make_story("broken-story", "망가진 이야기")
        self.write_catalog(["test-novel", "broken-story"])
        path, metadata = self.metadata("broken-story"); metadata["slug"] = "mismatch"
        path.write_text(json.dumps(metadata, ensure_ascii=False), encoding="utf-8")
        result = self.run_cli("build")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(marker.read_text(encoding="utf-8"), "old build")
        self.assertEqual({path.name for path in dist.iterdir()}, {"keep.txt"})


if __name__ == "__main__":
    unittest.main()
