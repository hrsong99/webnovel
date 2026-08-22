# Bilingual reader release review

## Verdict

**PASS.** The second reader-design pass, complete English edition, and bilingual editorial-summary system are ready for deployment.

## Editions

- Korean source edition: 6 chapters, 25,385 Korean characters
- English translated edition: 6 chapters, 16,005 words
- English translation contract: `manuscript/translations/en/STYLE-GUIDE.md`
- Reviewer overviews: 6 Korean and 6 English files, collapsed by default above each chapter

## Editorial process

The English edition received:

1. Independent chapter translation in three batches
2. Bilingual fidelity and continuity review
3. Continuous English speculative-fiction line edit
4. Integrated harmonization/copyedit across all six chapters
5. Reviewer-summary fact check in both languages

Resolved issues included name romanization, one false master-disciple implication, an unsupported payment fraction, martial-cadence consistency, realm terminology, a brief POV breach, Korean calques, and repetitive continuity-defense phrasing.

Chapter 6 still obeys the canonical power limit: Unraveling Qi stays inside Jin Cheol’s body, and Do Changsu loses his timing because physical vibration travels through the well stone, chisel, saber guard, and wrist.

## Reader design

The reader was rebuilt around long-form reading patterns used by established ebook and serial-fiction products while retaining a project-specific forged-iron and ledger identity.

- Self-hosted Maru Buri and Pretendard fonts
- Separate Korean and English covers
- Korean home at `/` and English home at `/en/`
- Chapter-preserving language links
- Responsive chapter navigation and table of contents
- Light, sepia, and dark themes
- Adjustable type size
- Local-only progress and preferences
- Spoiler-marked editorial overviews using native `details`/`summary`
- No login, database, cookies, or external runtime font dependency

Desktop English landing, mobile English reader, mobile Korean reader, and open-summary states were rendered and inspected. No release-blocking clipping, overflow, contrast, or control defects remained.

## Mechanical verification

- Unit tests: 8/8 passed
- Python compile: passed
- JavaScript syntax: passed
- Korean and English manuscript validation: passed
- Bilingual internal HTTP graph: 27 resources, all HTTP 200
- Korean and English EPUB ZIP/XML checks: passed
- Secret scan: no findings
- Git whitespace check: passed
- Production Docker build: passed
- Container health: healthy
- Runtime user: non-root UID 101
- Container health endpoint: `GET /healthz` → `200 ok`
- Final image: `sha256:677e111c04df0159fe1caa9e013574a9a32831e2ff4befe7664723951e5f9b3f`
