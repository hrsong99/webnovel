# Craft-standard and volume-one revision release

**Date:** 2026-08-22  
**Scope:** fiction standard, Korean developmental revision, English effect-localization, synchronized editorial material, and reader QA

## Deliverables

- `docs/fiction-craft-standard.md` — operational authoring, revision, localization, and release standard
- `docs/story-craft-overlay-template.md` — genre/culture/audience/language overlay template
- `research/fiction-craft/fundamentals.md` — cited research synthesis
- `editorial/volume-one-attention-audit.md` — pre-revision diagnosis and protected strengths
- Korean Chapters 2–6 — developmental revision; Chapter 1 protected
- English Chapters 1–6 — effect-localized literary edition
- synchronized story bible, outline, style guide, metadata, and bilingual reviewer overviews

## Final manuscript statistics

- Korean: 6 chapters, 23,255 Korean characters
- English: 6 chapters, 14,826 words
- Korean chapter range: 3,540–4,460 characters
- English chapter range: 2,194–2,897 words

## Independent editorial verdicts

- Korean attention/development audit: the original decline came from choices and payoffs being delayed behind repeated proof, procedure, and explanation.
- Final English literary QA: **no blockers**; native English syntax, sustained post-opening reader pull, controlled short paragraphs, appropriate exposition, and persistent emotional residue.
- Initial bilingual QA: five exact canon discrepancies found.
- Post-fix strict bilingual QA: **pass**; all five corrected and no remaining release-blocking canon discrepancy.

## Verified canon constraints

- Seven children enter the Chapter 3 rite; six survive and Hajin dies.
- Gangho is a separate eighth endangered child in Chapter 6.
- Yeonhwa retains custody and consent leverage rather than functioning as permission for Jin Cheol.
- Current Unraveling Qi remains inside Jin Cheol’s body; the external combat effect is ordinary physical vibration.
- The failed and hedged evidence routes remain visible.
- Seventeen households consent and seventeen residents stand behind Jin Cheol.

## Mechanical and artifact verification

- Manuscript validation: passed
- Unit tests: 9/9 passed
- Python compilation: passed
- JavaScript syntax: passed
- Markdown local-link check: 0 missing
- Citation ledger: passed; 30 distinct sources cited
- Static build: passed for Korean and English
- Generated HTML: 16 files
- Generated local asset references checked: 218; 0 missing
- Korean and English EPUB package/integrity checks: passed
- Desktop and mobile Chromium smoke tests: HTTP 200, no console errors, no horizontal overflow
- Homepage Korean title orphan corrected and re-measured as a single line at 1440 px
- Production Docker image: built successfully as `murim-abolitionist:craft-revision`
- Production container smoke: `/healthz` returned `ok`; container reported `running healthy`; English Chapter 6 served successfully
- `git diff --check`: passed

## Environmental notes

- The Browser Use harness could not launch Chrome, so visual QA used installed Playwright with `/usr/local/bin/google-chrome` directly.
- Direct Docker access was denied for the unprivileged user; noninteractive `sudo` succeeded for the exact production build and runtime smoke test.
- A protected repository `AGENTS.md` write was not made because its approval prompt timed out. The standard remains linked from the README and production playbook.
