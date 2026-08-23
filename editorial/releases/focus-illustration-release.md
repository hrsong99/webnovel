# Focus reader and illustrated-edition release

**Scope:** reusable authoring pipeline, focus-reading interaction, reference-driven scene illustrations, bilingual web/EPUB integration, and release automation
**Branch:** `feat/focus-reader-illustration-pipeline`
**Source baseline:** `db16d7389cfcffd54b3031d8411352ca9858a75a`

## Source preservation

No Korean or English chapter file changed in this release. The work adds a reading mode and derived visual edition around the already approved manuscript.

## Durable production system

- `docs/authoring-pipeline.md` is the ordered lifecycle authority from research through archive/errata.
- `docs/templates/` now contains production state, continuity, editorial findings, rendered proof, translation, visual bible, illustration manifest, and release-report templates.
- `scripts/release_check.py` provides one fail-closed command for compilation, JavaScript syntax, unit tests, catalog validation, build, generated-reference crawl, EPUB XML parsing, whitespace, and optional container smoke testing.
- Story-specific production status, visual identity, prompts, rejected candidates, approved references, edits, and final placements remain in the repository.

## Focus-reading result

- Explicit `◎ Focus / 집중` toolbar control; ordinary scrolling remains the default.
- Active paragraph or figure is clear; surrounding context is muted without blur or layout scaling.
- Active tap advances; inactive tap jumps.
- Space/J/Down/PageDown advance; Shift+Space/K/Up/PageUp reverse; Escape exits.
- Selection and swipe guards prevent accidental advancement.
- Manual scrolling synchronizes after settling without fighting the reader.
- The final step reveals chapter navigation instead of auto-following.
- Focus mode resets per page to avoid surprising dimmed prose.
- Reduced-motion uses an instant guarded scroll and does not race with manual-scroll synchronization.
- Figures participate as a single focus unit.

## Illustrated edition

Initial release: one canon-safe illustration per chapter in both Korean and English reader pages and EPUBs.

| Chapter | Asset | Placement KO / EN | Final prompt |
|---:|---|---|---|
| 1 | `ch01-bowl.webp` | 51 / 46 | bowl and tray reversal |
| 2 | `ch02-six-men.webp` | 204 / 185 | exactly six tangled thugs |
| 3 | `ch03-throat-touch.webp` | 200 / 190 | correct weapon ownership and first touch |
| 4 | `ch04-returning-dish.webp` | 172 / 174 | Returning Dish Step in the blade corridor |
| 5 | `ch05-auction-win.webp` | 206 / 169 | white-jade key, badge, coalition, Ma’s ledger |
| 6 | `ch06-first-tomorrow.webp` | 221 / 205 | six-eye Myogak and First Tomorrow Step |

Four approved recurring-character references keep visual identity stable:

- Ryu Dan
- Ma Yeongsun
- Nam Sogun
- Myogak

References used GPT Image 2 Medium through Codex OAuth. Final scenes used GPT Image 2 High with reference-image inputs. Failed anonymous candidates were recorded and rejected. Nam/Myogak references and Chapters 2/3/4/6 received targeted image edits; no defective candidate was published.

## Asset checksums

```text
63a7090cb8a732176c909d400f6360c19b61e6673a9c106b0b615c058c3ab708  ch01-bowl.webp
3ad967956394c7755ac5095fbf170d2c1cdd4ae0f08acc50c64badcbba810cd6  ch02-six-men.webp
360909d2b39ef1ab3fe238a6d4a6041f8a723776134f858322e3d117766cd086  ch03-throat-touch.webp
9cfde818cd4b2118147c7a214bd7b67773a877cb50cf53b730c6cf581b0146ce  ch04-returning-dish.webp
b2317c1acda15f054f3530699c75e77a97c0c42d88f6ee5d40bca0c0af2bb47a  ch05-auction-win.webp
5a40eade27ea497547363b1ea343fd233b1490c64ae24b3a60cdb4635e42179a  ch06-first-tomorrow.webp
ff13d409d0c759810ea864e82cbf587f46239cdb66c3d7d66bcd5acdf6af03e9  ma-yeongsun-v1.webp
a7360ed2574429217d993e435c9c69f7a5f081632c78ac75e47681ed16a7b757  myogak-v1.webp
c0a91e46c35a0721d277506f496d4571663b0ee6b416890ffe6409a3a2669598  nam-sogun-v1.webp
c46365cc9af9b7521a7cdb350588cd0aed65e129d2f21a5223280e5443f1f509  ryu-dan-v1.webp
```

## Final local evidence

- 20/20 unit tests passed.
- Both Korean/English story pairs validated.
- 48 HTML pages and 660 local references checked; 0 missing.
- Six EPUBs and 54 XML/XHTML documents parsed successfully.
- All 12 illustrated chapter routes loaded exactly one localized figure with decoded pixels and no horizontal overflow.
- English and Korean focus-mode figure steps passed on 390px reduced-motion Chromium.
- Desktop and mobile screenshots were visually inspected after lazy image decoding.
- Secret-pattern scan returned 0 findings.
- Chapter diff returned empty.
- Docker image: `sha256:cb0c7defbc398f123c6c7a319230cc373cc03d4786037e31f613884f2bed8107`
- Runtime: `running healthy`, non-root UID `101`, `/healthz` → `ok`.

## Deployment contract

- Dockerfile: `Dockerfile`
- Port: `8080`
- Health route: `/healthz`
- Required environment variables: none
- Persistent volume: none

Remote PR, merge, and post-merge CI evidence are appended after release.
