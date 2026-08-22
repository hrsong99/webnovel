# Dopamine-first second-story release

## Scope

This release adds a deliberately reward-dense martial/progression story while converting the reader and build pipeline from one hardcoded book into a multi-story library.

New story:

- Korean title: **회귀자 일곱이 죽고 점소이만 남았다**
- English title: **Seven Regressors Fell. Only the Inn Boy Remained.**
- Volume: **처음 온 서른한 번째 날 / The First Thirty-First Day**
- Korean source edition: 6 chapters, 32,184 Korean characters
- English literary edition: 6 chapters, 18,875 words

The original **무림철폐론자** Korean and English manuscripts were migrated without prose changes.

## Research and design

`research/dopamine-serial-design.md` records the evidence boundary, official Korean progression-wuxia examples, reward and curiosity research, project-specific cadence, selected concept, and anti-pattern gate. “Dopamine” is used as reader shorthand, not as a claim that any plot device directly produces a measured neurotransmitter response.

The selected inversion preserves the familiar pleasures of regression fiction while bounding the answer key:

- Ryu Dan is the ignored recording vessel, not one of the seven regressors.
- The loop ends before Chapter 1.
- Knowledge covers only the repeated thirty days.
- His body must unlock capacity separately from remembered skill.
- From Chapter 4, altered consequences invalidate remembered solutions.
- The final victory requires an original present-tense action rather than another stored counter.

The story-specific operational contract lives in:

- `stories/seven-regressors-fell/manuscript/story-bible.md`
- `stories/seven-regressors-fell/manuscript/outline.md`
- `stories/seven-regressors-fell/manuscript/craft-overlay.md`
- `stories/seven-regressors-fell/manuscript/translations/en/STYLE-GUIDE.md`

## Editorial verification

An independent payoff audit returned **PASS**: every chapter delivers an earned major victory, visible progression, a specific forward hook, and rotating reward currencies rather than six larger versions of the same fight.

Integrated Korean editing corrected timeline transitions, injury and object custody, witness counts, terminology, and repeated tactical explanation while preserving the strong hooks and Ma Yeongsun’s practical humor.

Strict Korean and bilingual audits found and prompted correction of:

- the Day 31 → Day 32 timeline;
- Chapter 3’s duel win condition;
- the Azure Peak Token’s material, emblem, and name;
- Myogak’s recombination-versus-originality limit;
- fourth-node output legality;
- the Final Return Record’s seven engraved layers and contents;
- the Tomb of Seven Returns’ surviving outer storehouses and passages;
- Qingliu place-name consistency;
- the wounded eighth-regressor details;
- localized English object, number, time-unit, location, and sequence discrepancies.

## Multi-story publishing architecture

- Ordered root catalog with a fixed `legacy_alias_story` independent of display order.
- Canonical `/stories/<slug>/` and `/stories/<slug>/en/` routes.
- Existing Murim chapter, English, artifact, and cover aliases retained.
- Per-story metadata, covers, downloads, reading history, resume state, and settings.
- Exact Korean/English chapter-number parity.
- Strict `ko`/`en` language metadata validation.
- Unlisted story directories with `story.json` fail validation instead of disappearing silently.
- All stories validate before one atomic `dist/` replacement.
- Mutable legacy cover aliases are excluded from immutable caching.

## Mechanical evidence

Passed on the final local release candidate:

- Python compilation
- JavaScript syntax checks
- 17/17 unit tests
- Korean and English validation for both stories
- Two-story static build
- `git diff --check`
- Research citation-ledger verification at `--min-coverage 0.10`
- Secret-pattern scan: no findings
- 48 generated HTML files
- 648 local resource references checked, none missing
- Six generated/legacy EPUB packages checked as ZIP/XML, all valid
- Desktop catalog and new-story landing visual inspection
- Mobile Korean and English chapter visual inspection
- No browser errors or horizontal overflow in four representative Chromium cases
- Production Docker build
- `/healthz` returned `ok`
- Catalog, canonical Korean, canonical English, legacy chapter, and legacy cover routes returned HTTP 200
- Legacy cover response used `Cache-Control: no-cache`
- Runtime state: `running healthy`
- Runtime user: non-root UID 101
- Verified image: `sha256:dd8e85852ed27107ab8f995da6354c903f8828c880452c7c4f8efa9c58c66ef0`

## Deployment contract

- Branch: `main`
- Dockerfile: `Dockerfile`
- Port: `8080`
- Health route: `/healthz`
- Required environment variables: none
- Database or persistent volume: none
