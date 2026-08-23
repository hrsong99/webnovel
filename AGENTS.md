# AGENTS.md

Operating instructions for any agent or author working in this repository. Read this before editing anything.

## What this repository is

A Korean-source web-novel library that is also its own publishing system. Canonical Markdown chapters plus one dependency-free Python generator (`scripts/novel.py`) produce the static reader, standalone HTML, TXT, Markdown, and EPUB editions. There is no database, no framework, no runtime CDN, and no login.

Two layers, and you must not confuse them:

- **Mechanical layer** — deterministic, enforced by `scripts/novel.py` and `scripts/release_check.py`. If it passes, it passes.
- **Editorial layer** — craft, causality, agency, continuity, translation quality. No script judges this. It is enforced by process and by reading.

## Non-negotiable rules

1. **Korean chapters are canon.** The generator implements one source language: headings must match `# 제N화. 제목`, lengths are counted in Korean characters, `en` is the only translation target. Another source language is a generator change, not a metadata setting.
2. **One integrated editor owns prose at a time.** Reviewers are read-only and may run in parallel. Never let two writers revise the same file.
3. **Revise macro to micro:** intent → causality → attention → agency → scene → language → continuity → proof. Do not polish sentences that may be cut.
4. **Protect strengths before editing.** Write down the lines, jokes, images, relationships, and surprises that must survive the revision.
5. **A reviewer report is evidence, not truth.** Verify every finding against the current files before changing prose. Quotations and line numbers go stale after edits.
6. **After any blocker fix, re-run the delta audit and the full release gate.** "A prior reviewer passed" is not a current verdict.
7. **Translation is a literary edition, not a sentence mapping.** Preserve canon and effect, then judge the target language as native fiction.
8. **Illustration is opt-in, and generated media is derived material.** Text is the product. Do not propose, generate, or plan images unless the author explicitly asks; a story is complete and releasable with none. When images are requested, they may enrich the reading experience but may never rewrite canon.
9. **Never publish a partial catalog.** All published stories validate before any of them build.
10. **Store process in the repository.** Chat transcripts, model memory, and one provider's prompt history are not durable sources of truth.

## Canon hierarchy

When two files disagree, the higher one wins:

1. `catalog.json` — lifecycle membership and public order
2. `stories/<slug>/story.json`, `locales/*.json` — publishing contract
3. `stories/<slug>/manuscript/story-bible.md` — premise, cast, power rules, prohibitions
4. `stories/<slug>/manuscript/outline.md` — causal chapter design
5. `stories/<slug>/manuscript/chapters/` — Korean source edition
6. `stories/<slug>/manuscript/translations/` — derived editions
7. `stories/<slug>/manuscript/reviewer-notes/` — editorial summaries, not story canon
8. `stories/<slug>/reference/`, `research/` — evidence and history, never canon

Never copy plans, change logs, prompt history, or editorial notes into publishable prose. Git stores history; `chapters/` contains only the book.

## Story lifecycle

`catalog.json` has three mutually exclusive buckets, each matching `story.json` → `status`:

| Bucket | Status | Meaning |
|---|---|---|
| `stories` | `published` | fully validated, in the public build |
| `projects` | `planning` | concept/outline/draft work, never silently published |
| `retired_stories` | `retired` | preserved source and release history, excluded from new builds |

Every new story starts in `projects`. Promotion is a release action, not the start of drafting. Before promoting, run `promote-check` (below). Before retiring or replacing a released story, push its exact baseline to a remote archive branch and record the replacement slug and reason in `story.json` and a `RETIRED.md`.

## Where to go for the task you have

| Task | Read |
|---|---|
| Any new story, any phase | [`docs/authoring-pipeline.md`](docs/authoring-pipeline.md) — Phases 0–12, with gates |
| Drafting or revising prose | [`docs/fiction-craft-standard.md`](docs/fiction-craft-standard.md) + that story's `manuscript/craft-overlay.md` |
| Genre/audience-specific rules | the story's own `craft-overlay.md`. Never generalize one serial's habits into a repo-wide rule |
| Translating | pipeline Phase 8 + the edition's `translations/<lang>/STYLE-GUIDE.md` |
| Illustrations (**only when explicitly asked**) | pipeline Phase 9 + the story's `visual-bible.md` + `manuscript/illustrations.json` |
| Reader/site/build changes | [`docs/web-novel-production-playbook.md`](docs/web-novel-production-playbook.md) §8–§11 + [`docs/reader-design-notes.md`](docs/reader-design-notes.md) |
| Releasing | pipeline Phases 10–11 |
| New artifact of any kind | [`docs/templates/`](docs/templates) — copy the template, do not invent a shape |
| Wondering why something obvious is missing | [`docs/planned-work.md`](docs/planned-work.md) — deferred items, with the reason and the trigger |

## Commands

```bash
python3 -m unittest -v                                  # generator unit tests
python3 scripts/novel.py validate                       # all published stories (--story <slug> for one)
python3 scripts/novel.py stats                          # chapter/length statistics as JSON
python3 scripts/novel.py build                          # validate everything, then replace dist/ atomically
python3 scripts/novel.py promote-check --story <slug>   # what still blocks publication; changes nothing
python3 scripts/release_check.py                        # the full fail-closed gate (also what CI runs)
python3 scripts/release_check.py --docker               # final candidate: adds container build and smoke test
```

`release_check.py` runs compilation, `node --check` on the reader JavaScript, unit tests, catalog validation, stats, the atomic build, the generated-link crawl, EPUB ZIP/XML parsing, and whitespace checks. Run it before opening a PR.

## What the machine checks

Chapter numbering and gaps, `expected_chapters`, heading form, Korean-character and English-word bounds, placeholder and planning-note leakage into prose, suspicious exact repetition, KO/EN chapter parity, mandatory reviewer notes per chapter per language, illustration path safety / alt text / provenance, required manuscript artifacts, lifecycle/status agreement, generated link graph, EPUB structure.

Required artifacts per **published** story: `story-bible.md`, `outline.md`, `craft-overlay.md`, `continuity-ledger.md`, plus `visual-bible.md` when `illustrations.json` exists. A deliberate gap is recorded, not hidden:

```json
"artifact_exceptions": { "continuity-ledger.md": "why, and what holds the information instead" }
```

## What the machine cannot check

Emotional truth, tension, causality, agency, whether a chapter pays the reader now, whether a power-system victory is legal, whether the English reads as native fiction, whether a premise contradicts itself. Do not invent a numeric literary-quality score. These are caught by reading, by the craft standard, and by independent read-only review — or they are not caught at all.

A premise-level contradiction survived six drafted chapters, a full developmental pass, a Korean line edit, an English edition, illustrations, and release before it was found. See [`stories/seven-regressors-fell/RETIRED.md`](stories/seven-regressors-fell/RETIRED.md). Check the premise against itself early, in writing.

## Working discipline

- Work on a feature branch. Commit or push only when asked.
- Concurrent reviewers may read the same manuscript; only one editor writes to it.
- A timed-out or interrupted writer may still have changed files — inspect the worktree, do not trust its summary.
- Re-run every check in the parent context. Treat any subagent report as advice until current files and executable output confirm it.
- A configured deploy hook is not proof of deployment. Verify the public URL separately.

## Repository map

```text
catalog.json                     lifecycle buckets and public order
stories/<slug>/
  story.json                     publishing contract + status + artifact_exceptions
  locales/en.json                English edition metadata
  manuscript/                    bible, outline, overlay, ledger, chapters, translations, reviewer notes
  reference/                     long-range world material — reference, not canon
  editorial/                     that story's reviews and audits
  assets/                        covers and approved illustrations
site/                            shared CSS, JS, fonts, favicon
scripts/novel.py                 validate / stats / build / promote-check
scripts/release_check.py         the fail-closed release gate
docs/                            pipeline, craft standard, playbook, reader notes, templates
editorial/                       repository audit and per-release records
research/                        craft research, design notes, and archived history
tests/                           stdlib unittest
dist/                            build output (git-ignored)
```
