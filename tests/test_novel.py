import json
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ElementTree
import zipfile
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "novel.py"


class NovelPipelineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "manuscript" / "chapters").mkdir(parents=True)
        (self.root / "site").mkdir()
        for name in ("styles.css", "reader.js", "home.js"):
            (self.root / "site" / name).write_text(f"/* {name} */\n", encoding="utf-8")
        for name in ("cover.svg", "favicon.svg"):
            (self.root / "site" / name).write_text(
                '<svg xmlns="http://www.w3.org/2000/svg"></svg>\n', encoding="utf-8"
            )
        self.metadata = {
            "slug": "test-novel",
            "title": "시험 소설",
            "author": "테스트 작가",
            "language": "ko",
            "description": "빌드 검증용 소설",
            "min_chapter_chars": 20,
            "max_chapter_chars": 200,
            "expected_chapters": 2,
        }
        self.write_metadata()
        self.write_chapter(1, "시작", "가나다라마바사아자차카타파하 이야기가 조용히 시작되었다.")
        self.write_chapter(2, "도착", "새로운 인물들이 마을에 도착하고 오래된 문을 힘껏 열었다.")

    def tearDown(self):
        self.temp.cleanup()

    def write_metadata(self):
        (self.root / "story.json").write_text(
            json.dumps(self.metadata, ensure_ascii=False), encoding="utf-8"
        )

    def write_chapter(self, number, title, body, filename=None):
        name = filename or f"{number:03d}.md"
        (self.root / "manuscript" / "chapters" / name).write_text(
            f"# 제{number}화. {title}\n\n{body}\n", encoding="utf-8"
        )

    def run_cli(self, command):
        return subprocess.run(
            [sys.executable, str(SCRIPT), command, "--root", str(self.root)],
            text=True,
            capture_output=True,
            check=False,
        )

    def test_validate_and_stats_succeed(self):
        result = self.run_cli("validate")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("VALID", result.stdout)
        stats = self.run_cli("stats")
        self.assertEqual(stats.returncode, 0, stats.stderr)
        payload = json.loads(stats.stdout)
        self.assertEqual(payload["chapter_count"], 2)
        self.assertGreater(payload["korean_characters"], 40)
        self.assertEqual([c["number"] for c in payload["chapters"]], [1, 2])

    def test_rejects_numbering_gap_and_expected_count_mismatch(self):
        self.metadata["expected_chapters"] = 3
        self.write_metadata()
        (self.root / "manuscript" / "chapters" / "002.md").unlink()
        self.write_chapter(3, "건너뜀", "한글문자가충분히들어있는세번째장의본문입니다 새로운 사건이 일어났다.")
        result = self.run_cli("validate")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("numbering gap", result.stderr)
        self.assertIn("expected_chapters", result.stderr)

    def test_rejects_placeholders_and_editorial_metadata(self):
        self.write_chapter(1, "시작", "가나다라마바사아자차카타파하. TODO: 결말을 작성할 것.")
        self.write_chapter(2, "도착", "가나다라마바사아자차카타파하. 편집 메모: 시점을 바꿀 것.")
        result = self.run_cli("validate")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("placeholder", result.stderr)
        self.assertIn("editorial/planning metadata", result.stderr)

    def test_rejects_korean_character_bounds(self):
        self.metadata["min_chapter_chars"] = 40
        self.write_metadata()
        result = self.run_cli("validate")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Korean characters", result.stderr)

    def test_rejects_suspicious_phrase_repetition(self):
        phrase = "검은 문 너머에서 낯선 목소리가 들려왔다"
        body = ". ".join([phrase] * 4) + "."
        self.write_chapter(1, "반복", body)
        result = self.run_cli("validate")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("suspicious repetition", result.stderr)

    def test_build_creates_readable_outputs_and_valid_epub(self):
        result = self.run_cli("build")
        self.assertEqual(result.returncode, 0, result.stderr)
        dist = self.root / "dist"
        expected = {"test-novel.md", "test-novel.html", "test-novel.txt", "test-novel.epub", "index.html"}
        self.assertTrue(expected.issubset({p.name for p in dist.iterdir()}))
        self.assertIn("제1화. 시작", (dist / "test-novel.md").read_text(encoding="utf-8"))
        html = (dist / "test-novel.html").read_text(encoding="utf-8")
        self.assertIn("<!doctype html>", html.lower())
        self.assertIn("lang=\"ko\"", html)
        home = (dist / "index.html").read_text(encoding="utf-8")
        self.assertIn("chapters/01.html", home)
        self.assertIn("시험 소설", home)
        self.assertNotRegex(home.lower(), r"login|password|sign[ -]?in")
        chapter = (dist / "chapters" / "01.html").read_text(encoding="utf-8")
        self.assertIn("제1화", chapter)
        self.assertIn("02.html", chapter)
        self.assertTrue((dist / "assets" / "cover.svg").is_file())
        self.assertEqual((dist / "health.txt").read_text(encoding="utf-8"), "ok\n")
        self.assertIn("제2화. 도착", (dist / "test-novel.txt").read_text(encoding="utf-8"))
        with zipfile.ZipFile(dist / "test-novel.epub") as archive:
            self.assertEqual(archive.testzip(), None)
            self.assertEqual(archive.infolist()[0].filename, "mimetype")
            self.assertEqual(archive.infolist()[0].compress_type, zipfile.ZIP_STORED)
            self.assertEqual(archive.read("mimetype"), b"application/epub+zip")
            names = set(archive.namelist())
            self.assertIn("META-INF/container.xml", names)
            self.assertIn("OEBPS/content.opf", names)
            self.assertIn("OEBPS/nav.xhtml", names)
            self.assertIn("OEBPS/chapter-001.xhtml", names)
            for xml_name in (
                "META-INF/container.xml",
                "OEBPS/content.opf",
                "OEBPS/nav.xhtml",
                "OEBPS/chapter-001.xhtml",
            ):
                ElementTree.fromstring(archive.read(xml_name))

    def test_missing_or_invalid_metadata_is_a_clear_cli_error(self):
        (self.root / "story.json").unlink()
        result = self.run_cli("validate")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("story.json", result.stderr)
        self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
