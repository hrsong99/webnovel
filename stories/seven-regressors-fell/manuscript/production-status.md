# Production status — 회귀자 일곱이 죽고 점소이만 남았다

**Slug:** `seven-regressors-fell`
**Source language:** Korean
**Current phase:** retired and preserved
**Branch:** historical release on `main`; archive `archive/seven-regressors-v1`
**Last updated:** 2026-08-23

The completed novel release remains at PR #7 plus the Chapter 3 wording fix in PR #8. This file records the completed historical release. The story was retired on 2026-08-23 because its first-ever Day 31 was incorrectly treated as an event Ryu had rehearsed in earlier loops. Its files remain intact for history and selective adaptation. The canonical replacement planning package is `stories/seven-masters-returned/`; no predecessor prose or mechanics transfer automatically.

## Completed source and edition gates

- [x] Experience contract, research note, story bible, causal outline, and craft overlay
- [x] Six source chapters drafted and mechanically validated
- [x] Integrated developmental, attention, agency, language, progression, and continuity passes
- [x] Copyedit and rendered proof
- [x] Six English chapters localized as a native edition
- [x] Korean and English reviewer summaries
- [x] Independent payoff, source canon, target-language literary, and bilingual canon audits
- [x] All reported blockers fixed and current delta audit passed
- [x] Unit, catalog, build, link, EPUB, browser, container, PR CI, merge, and post-merge CI gates

## Release evidence

- Main story PR: https://github.com/hrsong99/webnovel/pull/7
- Duel-recap correction PR: https://github.com/hrsong99/webnovel/pull/8
- Current released baseline before this enhancement: `db16d7389cfcffd54b3031d8411352ca9858a75a`
- Korean source: 6 chapters / 32,184 Korean characters
- English edition: 6 chapters / 18,875 words

## Current reader enhancement

- [x] Optional focus-reading interaction designed
- [x] Tap active paragraph to advance
- [x] Tap another paragraph to jump
- [x] Space, PageUp/Down, and arrow-key controls
- [x] Escape exit
- [x] Surrounding units de-emphasized; active unit remains fully readable
- [x] 0.2–0.4 second distance-aware easing
- [x] `prefers-reduced-motion` honored
- [x] Focus mode deliberately resets per page to avoid surprising dimmed prose
- [x] Desktop and 390px mobile automated interaction smoke test
- [x] No console errors or horizontal overflow in tested routes
- [x] Independent UX review reconciled
- [x] Final local, EPUB, browser, and container release gate
- [ ] PR, merge, and post-merge CI

## Current illustration enhancement

- [x] Repository-wide illustration production and provenance contract
- [x] Optional bilingual `illustrations.json` validator
- [x] Safe local `assets/scenes/` copying
- [x] Language-specific paragraph placement
- [x] Responsive web figures and focus-unit behavior
- [x] EPUB image packaging and XHTML placement
- [x] Alt-text and provenance validation
- [x] Story-specific visual bible
- [x] Six-scene initial shot list with exact Korean/English placement
- [x] Character/style/scene prompt book
- [x] Two anonymous fallback generations visually inspected
- [x] Both fallback generations rejected rather than published
- [x] Authenticated Codex edit-capable generation backend ready
- [x] Ryu Dan, Ma Yeongsun, Nam Sogun, and Myogak references approved
- [x] Six final scene illustrations generated and visually approved
- [x] Approved files optimized and entered into `illustrations.json`
- [x] Final illustrated web/EPUB/mobile proof

## Current release gate

All creative and pipeline artifacts are complete. Remaining work is deterministic proof: rebuild the illustrated site and EPUBs, exercise focus-mode figures on desktop/mobile/reduced-motion, run the container gate, review the final diff, and release through PR plus post-merge CI.
