# Release report — Seven Masters Returned, Volume One

## Identity

- Story/edition: 칠대고수가 죽고 점소이만 회귀했다 / *Seven Masters Fell. The Inn Boy Returned.*
- Source branch: `feat/author-seven-masters-returned`
- PR: recorded after push
- Merge commit: recorded after merge
- Release date: 2026-08-23
- Rollback target: `c939db5b70b6c1997a6f3d938ba2b3a7b5861a54`; retired predecessor baseline also preserved at `archive/seven-regressors-v1`
- Public URL: deployment occurs after merge at `https://webnovel.134.185.109.169.sslip.io/`; verify before finalizing this report

## Editorial state

- Intended experience verdict: current Korean developmental delta has no blocker; earlier wrong-story PASS was rejected and not used
- Source canon/continuity verdict: PASS after Oh Gak, three-day timeline, shared-core, Myogak, Gwi, and Ma-agency fixes
- Target-language literary verdict: PASS after exact seven-item English copy delta
- Bilingual verdict: PASS after one-hour/two-hour timing correction; no other factual divergence found
- Visual verdict: illustration phase deliberately skipped; typographic SVG covers only
- Open revision opportunities: minor optional compression only; no release blocker
- Waived blockers: none

## Content totals

```text
Published stories: 2
Replacement Korean: 6 chapters / 25,141 Hangul characters
Replacement English: 6 chapters / 14,907 words
```

## Artifact verification

- Unit tests: 25/25 pass
- Validation: both bilingual published stories valid
- Atomic build: PASS, 53 tracked outputs
- Generated HTML/reference graph: 48 HTML files / 648 local references / 0 missing
- EPUB ZIP/XML: 6 EPUBs / 54 XML or XHTML documents parsed
- Browser QA: desktop catalog, Korean Ch1, English Ch1, and 390px English Ch6 pass; focus mode activates; no console errors or horizontal overflow
- Docker image: `sha256:7ee016d5674e830cf38c3a5d452272aad0de26a4bf89c94677f1919ed799f053`
- Runtime user and health: `running healthy user=101`; `/healthz` returns `ok`
- Representative routes: catalog, legacy aliases, both published stories, both languages, final chapters
- Secret/whitespace scan: PASS; zero secret-pattern findings and no diff whitespace errors
- Original-story preservation: no manuscript file under `stories/murim-abolitionist/` intentionally changed

## Media provenance

No generated illustration media was produced. `cover.svg` and `cover-en.svg` are repository-authored typographic/vector covers.

## Remote verification

- PR CI: recorded after push
- Post-merge CI: recorded after merge
- Remote `main` SHA: recorded after merge
- Deployment read-back: verify HTTPS catalog, Korean route, English route, and `/healthz` after deploying merged container

## Errata and correction route

New defects must be recorded as editorial findings, fixed on a branch, rechecked at the affected and adjacent gates, merged through CI, and appended here or in a linked correction report. Never rewrite this release record silently.
