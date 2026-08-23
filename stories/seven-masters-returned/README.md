# Seven Masters Returned — planning package

This folder is the canonical planning-stage replacement for `seven-regressors-fell`.

## Lifecycle

- Catalog bucket: `projects`
- `story.json` status: `planning`
- Source language: Korean
- Working Korean title: **칠대고수가 죽고 점소이만 회귀했다**
- Working English title: **Seven Masters Fell. The Inn Boy Returned.**
- Replaces: `stories/seven-regressors-fell` (retained under `retired_stories`)
- Released predecessor backup: remote branch `archive/seven-regressors-v1`

Planning and retirement are deliberate publication states. This package must not appear in `dist/`, EPUBs, or the public library until it is promoted to `catalog.json` → `stories` and its metadata status becomes `published`.

## Canon order inside this package

1. `story.json` — lifecycle and working publishing contract
2. `manuscript/concept-decision.md` — accepted premise and discarded alternatives
3. `manuscript/story-bible.md` — mechanics, cast, powers, timeline, and prohibitions
4. `manuscript/series-architecture.md` — fifteen-year serial engine and awakening arcs
5. `manuscript/outline.md` — current causal plan and its lock state
6. `manuscript/craft-overlay.md` — reader-experience and scene gates
7. `manuscript/continuity-ledger.md` — deterministic facts as drafting begins
8. `manuscript/visual-bible.md` — visual boundaries and future reference requirements
9. `manuscript/open-questions.md` — unresolved decisions only
10. `manuscript/production-status.md` — phase gates and evidence

The Korean chapters will become canon only after an approved outline and explicit draft start. No prose from the retired predecessor is automatically canon; scenes, jokes, characters, and assets may be adapted only after they pass the replacement story’s mechanics.

## Authoring promotion gate

Before creating `manuscript/chapters/01.md`:

1. Resolve every blocking item in `open-questions.md`.
2. Lock the seven younger/future character pairs and awakening order.
3. Finish the first-volume causal outline chapter by chapter.
4. Initialize object, knowledge, power, and relationship continuity.
5. Record protected predecessor strengths worth adapting.
6. Update `production-status.md` to authorize source drafting.

Before publication, add complete locale metadata and translations, finish all editorial and QA gates, change status to `published`, and move the slug from `projects` into the public `stories` array.
