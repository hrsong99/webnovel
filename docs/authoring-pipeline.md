# Reusable fiction-production pipeline

**Purpose:** preserve the complete authoring, developmental editing, line editing, proofreading, localization, illustration, publication, and release process as a repository-owned operating system. It is deliberately model- and vendor-independent.

This document tells a future author or agent **what to do, in what order, what artifact to leave behind, and what must be true before advancing**. The craft principles live in [`fiction-craft-standard.md`](fiction-craft-standard.md); the technical details live in [`web-novel-production-playbook.md`](web-novel-production-playbook.md).

## The non-negotiable operating rules

1. **Korean chapters are canon** unless a story explicitly declares a different source language.
2. **One integrated editor owns prose changes at a time.** Independent reviewers are read-only and may work in parallel.
3. **Revise macro to micro:** intent → causality → attention → agency → scene → language → continuity → proof.
4. **Protect strengths before editing.** Record the lines, jokes, images, relationships, and surprises that must survive.
5. **A reviewer report is evidence, not truth.** Verify every finding against the current files before changing prose.
6. **After any blocker fix, run a delta audit and the complete release gate.** Earlier quotations and line numbers may be stale.
7. **Translation is a literary edition, not a sentence mapping.** Preserve canon and effect, then judge the target language as native fiction.
8. **Generated media is derived publication material.** It may enrich the reading experience but may not silently rewrite canon.
9. **Never publish a partial catalog.** Build all stories atomically after validating all of them.
10. **Store process in the repository.** Chat transcripts, private memory, and one provider’s prompt history are not the durable source of truth.

## Durable artifact map

Every story should converge on this structure:

```text
stories/<slug>/
  story.json
  locales/en.json                         # when localized
  assets/
    cover.svg
    cover-en.svg                          # optional
    scenes/                               # approved local illustrations
  manuscript/
    production-status.md                  # copied from docs/templates/
    story-bible.md                        # facts, limits, cast, continuity
    outline.md                            # causal chapter design
    craft-overlay.md                      # experience and genre-specific gate
    continuity-ledger.md                  # copied from docs/templates/
    visual-bible.md                       # copied from docs/templates/
    illustrations.json                   # approved placement/provenance manifest
    chapters/
    translations/en/
      STYLE-GUIDE.md
      chapters/
    reviewer-notes/ko/
    reviewer-notes/en/
```

Only publishable prose belongs in `chapters/`. Planning, prompts, QA findings, and visual specifications stay beside it.

### Story lifecycle

`catalog.json` has three mutually exclusive buckets:

- `stories`: `status: published`; fully validated and included in the public build;
- `projects`: `status: planning`; concept, outline, or draft work that is never silently published;
- `retired_stories`: `status: retired`; preserved source and release history excluded from new builds.

Start every new story in `projects`. A planning package may omit chapters, translations, covers, and publishable metadata that its current phase has not earned. Promotion to `stories` is a release action, not the start of drafting. Before replacement or retirement, preserve the exact released baseline on a remote archive branch and record the replacement slug and reason in `story.json`.

## Phase 0 — Start cleanly

### Inputs

- A goal, audience, language, genre, and intended experience.
- Existing repository state and any earlier canon.

### Actions

1. Pull the current default branch with fast-forward only.
2. Read repository instructions and the three governing docs.
3. Create a feature branch.
4. Register the slug in `catalog.json` → `projects` with `story.json` status `planning`.
5. Copy the production, continuity, and visual templates into the new story.
6. Record known constraints and open questions before drafting.

### Gate

- The worktree starts from an understood baseline.
- Canon and non-canon sources are explicitly ranked.
- The production checklist names the current phase.

## Phase 1 — Research and experience contract

Research only what can change a decision: audience expectations, genre promises, cultural terminology, legal examples, factual claims, and relevant reader-experience evidence.

### Required outputs

- A repository research note with sources, evidence boundaries, and operational consequences.
- A one-paragraph intended experience.
- A list of promises and anti-promises.

### Gate

- Every cited claim can be traced to a source.
- Research does not pretend to prove subjective enjoyment.
- The intended experience is specific enough to reject an attractive but wrong scene.

## Phase 2 — Concept selection

Generate several materially different premises. Compare them on:

- freshness of viewpoint;
- repeatable story engine;
- human center;
- escalating problem variety;
- genre payoff frequency;
- cost and limitation;
- ending proof;
- risk of cliché or moral evasion.

Select one premise and record why the alternatives lost. Familiar devices are allowed when their function is explicit and the viewpoint or consequence is genuinely different.

### Gate

The selected premise can answer:

- Why this protagonist?
- Why now?
- What repeatedly creates new situations?
- What prevents the advantage from solving everything?
- What must the climax prove that Chapter 1 cannot?

## Phase 3 — Lock the story contract and canon

Complete `story-bible.md`, `craft-overlay.md`, and `continuity-ledger.md` before prose drafting.

Minimum canon:

- cast names, ages, roles, desires, leverage, and relationships;
- world and power rules;
- knowledge boundaries;
- timeline anchors;
- named objects and custody;
- injury and resource persistence;
- prohibited shortcuts;
- required end state.

### Gate

A skeptical reader can determine whether a proposed victory, reveal, travel time, or ability is legal without asking the original author.

## Phase 4 — Build a causal outline

For each chapter, record:

| Field | Question |
|---|---|
| Near promise | What pleasure or answer is offered early? |
| Want | Who wants what now? |
| Pressure | Why is the result uncertain or costly? |
| Choice | What closes another option? |
| Delta | What becomes materially, emotionally, or relationally true? |
| Local payoff | What does the reader receive before being asked to continue? |
| Persistence | What injury, object, status, debt, or relationship carries forward? |
| Next pressure | What specific changed question opens? |

Reverse-causality test every major beat: **because event happened and character chose action, new state is now true.**

### Gate

- Every chapter has a local payoff and irreversible delta.
- Obstacles adapt rather than repeat at higher volume.
- The ending pays the premise’s deepest promise.
- All required transitions fit the timeline.

## Phase 5 — Draft the source edition

Draft in bounded chapter groups only when their interfaces are explicit. One writer owns each file. Do not let concurrent writers revise the same prose.

After each chapter:

1. Run the one-page craft checklist.
2. Validate headings, length, placeholders, and repetition.
3. Update the continuity ledger with new facts.
4. Record protected strengths before any revision.
5. Check the promised local payoff and next pressure.

### Gate

```bash
python3 scripts/novel.py validate --story <slug>
python3 scripts/novel.py stats --story <slug>
```

The chapter is not “done” merely because it reaches its target length.

## Phase 6 — Integrated developmental revision

The integrated editor reads the full source edition and edits only after producing a reverse outline.

Pass order:

1. **Intent and strengths** — restate the contract and protect what already works.
2. **Causality and attention** — remove duplicate jobs and empty stretches.
3. **Agency and consequence** — track who chooses, benefits, pays, and can refuse.
4. **Scene and information** — attach exposition to decisions and pressure.
5. **Progression legality** — verify every ability, resource, and victory.
6. **Language and rhythm** — read aloud; repair syntax, voice, dialogue, and imagery.
7. **Continuity** — reconcile time, travel, wounds, objects, names, knowledge, counts, and custody.

### Gate

- Every scene has a job and delta.
- Each chapter still delivers its intended experience.
- No protected strength was flattened accidentally.
- The continuity ledger and manuscript agree.

## Phase 7 — Copyedit and proofread

Copyediting is not developmental editing. Do not reopen stable structure while correcting surface errors unless a genuine contradiction appears.

### Source-file proof

- grammar, particles, punctuation, typography, spacing;
- heading and chapter numbering;
- names, titles, terminology, and counters;
- repeated phrases, subjects, metaphors, and explanatory restatement;
- accidental editorial notes or placeholders.

### Rendered proof

Proof the actual website, mobile view, standalone HTML, TXT, Markdown, and EPUB:

- line breaks and paragraph order;
- clipping, overflow, contrast, and font fallback;
- previous/next and language routes;
- reviewer-note disclosure;
- covers and illustrations;
- focus mode and reduced-motion behavior.

### Gate

No blocking grammar, formatting, continuity, or rendered-reading defect remains.

## Phase 8 — Localize as a native edition

1. Lock the current source canon.
2. Create a target-language style guide and glossary.
3. Record each scene’s intended effect before translating it.
4. Translate by scene and effect, not sentence length or word order.
5. Read the entire edition continuously for voice.
6. Compare every chapter back to canon for facts and constraints.
7. Write synchronized reviewer summaries.

Required independent reviews:

- target-language literary read;
- strict bilingual canon audit;
- source-language post-fix continuity audit.

### Gate

All three return PASS, or every blocker is fixed and a current delta audit returns PASS.

## Phase 9 — Visual development and illustration

Images should deepen a moment, not summarize every action or interrupt every page.

### 9.1 Lock a visual bible

Record:

- character identity anchors that must never drift;
- clothing and prop continuity by chapter;
- architecture, geography, season, and time-of-day palette;
- one named art direction with positive and negative traits;
- prohibited iconography, anachronisms, text, logos, and spoilers.

### 9.2 Build references before scenes

Generate and approve in this order:

1. neutral character sheets for recurring people;
2. location and prop sheets;
3. one style frame;
4. scene candidates using the approved references;
5. corrections via image editing or inpainting rather than restarting identity from text.

For every generation, record provider, model, prompt, negative prompt, seed, aspect ratio, source references, generation date, and review status. Save files locally; never hotlink temporary provider URLs.

### 9.3 Select scenes

Use at most one or two illustrations per chapter. Prefer:

- a strong chapter promise or first impossible image;
- a decisive reversal or original solution;
- an emotional aftermath that prose benefits from pausing on.

Avoid spoiling the final beat before the prose reaches it. Place illustrations after a stable paragraph number through `manuscript/illustrations.json`, never by embedding provider syntax into canonical prose.

### 9.4 Visual QA

Reject images with:

- face, age, hair, clothing, weapon, handedness, or body-shape drift;
- wrong number of people, fingers, eyes, objects, or symbols;
- illegal power effects or timeline lighting;
- modern objects, faux-Chinese text, signatures, or watermarks;
- generic poses that contradict the scene;
- composition that becomes illegible at mobile width.

### Gate

Every published image is canon-safe, locally stored, consistently art-directed, provenance-recorded, responsive, and useful at its exact placement.

## Phase 10 — Independent release QA

Run independent read-only reviews for:

- intended reader experience and chapter payoff;
- strict canon, timeline, power, object, and injury legality;
- target-language literary quality and bilingual fidelity;
- software architecture, accessibility, caching, paths, and state migration.

The integrated editor fixes verified blockers. Then ask a final reviewer to inspect only the changed deltas and any adjacent continuity.

### Gate

A final current-file verdict returns PASS. “A prior reviewer passed” is not sufficient after later edits.

## Phase 11 — Mechanical and experiential release

```bash
python3 -m py_compile scripts/novel.py tests/test_novel.py
node --check site/home.js
node --check site/reader.js
python3 -m unittest -v
python3 scripts/novel.py validate
python3 scripts/novel.py stats
python3 scripts/novel.py build
git diff --check
```

The repository-owned wrapper runs compilation, JavaScript syntax, tests, validation, the atomic build, generated-reference crawling, every EPUB XML document, and whitespace checks in one fail-closed command:

```bash
python3 scripts/release_check.py
python3 scripts/release_check.py --docker  # final candidate
```

Then verify:

- generated-link graph;
- EPUB ZIP/XML structure;
- desktop and mobile success paths;
- focus-mode tap, keyboard, theme, font, and reduced-motion behavior;
- console errors and horizontal overflow;
- Docker build, non-root runtime, `/healthz`, and representative routes;
- secret scan and complete staged diff;
- original published stories remain unchanged unless intentionally revised.

Push a feature branch, open a PR, wait for CI, merge, pull `main`, and verify post-merge CI. A deployment hook is not proof of a public deployment; verify the external URL separately.

## Phase 12 — Reader feedback and next edition

Keep raw reader feedback out of canon. Record:

- where readers stopped, skimmed, laughed, predicted, misunderstood, or cared;
- whether focus mode helped or distracted;
- whether images clarified identity or interrupted imagination;
- actual continuity defects versus taste preferences.

Classify each item as blocker, revision opportunity, or experiment. Start a new branch and repeat the same gates. Never silently revise a released source edition without a release record.

## Minimal reusable command brief

A future agent can begin with:

> Follow `docs/authoring-pipeline.md`, `docs/fiction-craft-standard.md`, and the story’s own bible/overlay. Preserve canon hierarchy. Produce every required artifact, use one integrated editor, run independent read-only QA, verify all blockers against current files, and do not call the work complete until the rendered reader, EPUB, Docker image, PR CI, merge, and post-merge CI have passed.
