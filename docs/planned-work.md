# Planned work

Deliberately deferred items. Each one is understood and wanted; none is started. Nothing here is a blocker for the current release state.

Keep this file honest: delete an entry when it ships, and add the reason if one is abandoned.

---

## 1. Korean AI-tell linter — `novel.py lint`

**Want:** convert the repeatable parts of the manual line-edit pass into a mechanical check, so the most expensive review stops being the one most likely to be skipped.

**Why not yet:** the value is certain; the thresholds are not. A regex set that fires on ordinary good prose gets disabled within a week, so this needs calibration against both existing manuscripts before it can be trusted in `validate`.

**Source material:** [`stories/murim-abolitionist/editorial/korean-line-edit.md`](../stories/murim-abolitionist/editorial/korean-line-edit.md) diagnoses the concrete recurring patterns — scene-closing 대구형 경구, 표어형 대사, `A가 아니라 B`, 선언형 마감, craft metaphors bleeding into every character's voice, repeated subject starts.

**Acceptance:**
- runs as a separate `lint` subcommand, never inside `build`;
- per-story thresholds live in `story.json`, not in the script;
- measured against the current Korean chapters of both stories, with the false-positive rate written down;
- reports counts and locations; it does not produce a quality score.

---

## 2. Machine-readable chapter contract — `outline.json`

**Want:** the Phase 4 fields (near promise / want / pressure / choice / delta / local payoff / persistence / next pressure) as data rather than prose, so `validate` can assert that every chapter file has an approved contract and every contract has a chapter.

**Why not yet:** premature. `murim-abolitionist`'s outline is prose that would need conversion, and [`stories/seven-masters-returned/manuscript/outline.md`](../stories/seven-masters-returned/manuscript/outline.md) explicitly says its chapter-level outline is not locked. Shipping a validator with no users is dead code.

**Trigger:** when `seven-masters-returned` locks its volume-one causal outline. That file already enumerates the required fields.

**Acceptance:**
- schema mirrors the Phase 4 table exactly;
- `validate` checks chapter/contract parity and non-empty fields — never literary quality;
- adopting it is per-story, so the published story is not forced to convert.

---

## 3. Source-language generalization in the generator

**Want:** support a story whose source edition is not Korean.

**Why not yet:** nothing needs it, and it is not a small change — `HEADING_RE`, `count_korean`, the length-bound fields, and the hardcoded `("ko", "en")` language tuple all assume one source language. Operating rule 1 now states this constraint plainly instead of implying it is configurable.

**Trigger:** an actual non-Korean story being planned. Not before.

---

## 4. Retired-story assets in the working tree

**Want:** decide whether `stories/seven-regressors-fell/assets/scenes/` (about 4.8 MB of approved illustrations for retired prose) stays in the working tree.

**Why not yet:** it is a judgment call, not a defect. The exact released baseline is preserved on remote branch `archive/seven-regressors-v1`, and [`RETIRED.md`](../stories/seven-regressors-fell/RETIRED.md) lists the `return-ink-v1` direction as adaptable — so the character references may still earn their place even though the six scene images are tied to chapters that will not be republished.

**Decide when:** the replacement story reaches its own visual phase, if it ever does.

---

## 5. Split `murim-abolitionist`'s continuity ledger out of the story bible

**Want:** a real `manuscript/continuity-ledger.md` instead of the recorded exception in `story.json`.

**Why not yet:** volume-one continuity is genuinely canonical inside `story-bible.md` → 「제1권 핵심 연속성」. Copying it into a second file today creates two sources that can drift, with no second volume to justify the split.

**Trigger:** authorizing Volume 2 drafting. At that point extract the section, make the ledger canonical, and delete the `artifact_exceptions` entry — `validate` will fail until the exception is removed, which is the intended reminder.

---

## 6. Rename `planned_volume_chapters` at promotion

**Want:** `seven-masters-returned/story.json` uses `planned_volume_chapters`; publication requires `expected_chapters`, plus the full display metadata set.

**Why not yet:** it is planning-stage metadata and the chapter count is not locked.

**Trigger:** promotion. `python3 scripts/novel.py promote-check --story seven-masters-returned` already reports this and everything else that blocks the move.
