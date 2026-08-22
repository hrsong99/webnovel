# Illustration prompt book — `return-ink-v1`

Use with an authenticated image-editing model after the character and style references in `visual-bible.md` are approved. These are production briefs, not prose canon.

## Shared style block

> `return-ink-v1`: Korean wuxia graphic-novel illustration, disciplined ink wash and muted mineral pigment on warm mulberry paper, visible dry-brush texture, selective crisp detail at face/hands/decisive prop, charcoal and worn indigo palette with at most one restrained cinnabar accent, historically grounded Korean fantasy clothing and timber/stone architecture, cinematic 16:9 composition with mobile-safe central action and generous negative space, restrained emotion and readable silhouettes, not anime, not chibi, not glossy game splash art, not photoreal.

## Shared negative block

> No writing, subtitles, letters, calligraphy, logo, watermark, signature, UI, modern objects, extra people, duplicate limbs, malformed hands, fused weapons, wrong handedness, generic glowing eyes, ornate armor, oversized swords, random magic particles, gore, anachronistic palace decor, Chinese fantasy signage.

## Reference-generation briefs

### `ref-ryu-dan-v1`

Neutral full-body and head-turn reference sheet, one person only. Ryu Dan: lean 20-year-old Korean male inn servant, youthful oval face with slightly hollow cheeks, calm narrow dark eyes, straight brows, quiet mouth, black hair tied in a simple low practical knot with two short loose strands, faded charcoal-gray work hanbok, off-white inner collar, cream apron, cloth shoes, round wooden serving tray. Relaxed balanced stance, quick working hands, no heroic pose or muscular bulk. Plain warm-paper background. Front, three-quarter, and profile views without labels or writing.

### `ref-ma-yeongsun-v1`

Neutral full-body and head-turn reference sheet, one person only. Ma Yeongsun: sturdy 43-year-old Korean woman innkeeper, strong working forearms, angular practical face, alert dark eyes and smile lines, black hair with a few gray strands in a tight bun secured by one plain silver pin, worn indigo work hanbok, dark apron, faint flour on one sleeve, ledger and dishcloth as separate props. Planted unflustered posture, never delicate or youthful. Plain warm-paper background. Front, three-quarter, and profile views without labels or writing.

### `ref-nam-sogun-v1`

Neutral full-body and head-turn reference sheet, one person only. Nam Sogun: Korean male martial examiner in early thirties, trained lean build, sun-browned direct face, black hair in a high martial knot, dark Azure Peak blue uniform with exactly thirteen small cloud motifs running along one sleeve, practical wooden training sword and sheathed steel sword, precise disciplined posture. No villain expression. Plain warm-paper background, no labels or writing.

### `ref-myogak-v1`

Neutral turn reference, one formation-born figure only. Myogak: spare monk-like humanoid silhouette made from matte black sand and ash held by thin cinnabar formation seams, calm mask-like face with exactly seven small black eye-points arranged deliberately across it, no human skin, no horns, no robot parts, no Buddhist symbols. Front, three-quarter, and profile views without labels or writing.

## Chapter scene briefs

Each scene should use the approved style frame plus all recurring-character references present in the shot.

### `ch01-bowl-v1`

**References:** Ryu Dan, Ma Yeongsun, Return Inn style frame.
Inside the worn timber Return Inn at pale Day 31 dawn. Ryu Dan stands in economical three-quarter profile and extends his round serving tray. A white porcelain bowl has just completed half a turn around the raised rim and rests perfectly at center without spilling. One rough Black Tooth swordsman is frozen mid-draw opposite him; his aggression has become confusion. Ma Yeongsun stands behind the counter, sturdy and unimpressed, already reaching to reclaim the valuable bowl. Exactly three principal people. Medium-wide low camera, tray and bowl tack-sharp, dawn dust in side light, no magic.

### `ch02-six-men-v1`

**References:** Ryu Dan, Ma Yeongsun, Return Inn.
Return Inn common room on the same Day 31 evening. Six Black Tooth men collapse into one tangled heap after striking and tripping one another; their six bodies must remain individually readable and non-gory. Ryu Dan stands just beyond them in weighted black-iron Plum-Shadow shoes, relaxed and untouched, one foot planted as the axis of the motion. Ma Yeongsun sits at the counter opening her damage ledger instead of reacting with awe. Wide diagonal composition, physical comedy through cause and posture, broken chair and tilted table, no magic glow.

### `ch03-throat-touch-v1`

**References:** Ryu Dan and Nam Sogun.
Azure Peak training court under late-evening gate lamps. During the thirteenth form, Nam Sogun’s wooden blade has grazed and torn Ryu Dan’s right shoulder, drawing one thin hot line, while Ryu Dan’s small broken wooden wedge has already reached Nam Sogun’s throat without pressing into the skin. Both men stop by choice. Show mutual skill and exact timing, not domination. Ryu wears charcoal work hanbok, weighted shoes, no apron; Nam wears dark Azure blue with thirteen cloud motifs. Watching applicants are soft distant silhouettes only. Medium-wide crossing diagonals with both contact points clearly readable.

### `ch04-returning-dish-v1`

**References:** Ryu Dan; Tomb of Seven Returns style frame.
Inside the unknown blade corridor. Ryu Dan’s sleeves are becoming shredded and his earlier shoulder injury remains visible. He turns crushing lateral force into the next step: one weighted shoe forms an axis, his torso follows the circular balance of carrying a tray, and dust plus thin pressure highlights reveal an invisible cut being redirected into the stone floor. He quietly names Returning Dish Step. No floating swords and no giant aura; the breakthrough is balance, circulation, and observation. Long corridor perspective, centered mobile-safe silhouette, companions held far behind in dim safety.

### `ch05-auction-win-v1`

**References:** Ryu Dan, Ma Yeongsun, Nam Sogun, So Yagran, U Chil, Return Inn.
Return Inn transformed into an improvised auction hall. Ryu Dan holds the separate white-jade Outer Gate Key as four restrained star-node echoes answer around his center. The crowd has opened a respectful path. Nam Sogun fastens the Outer Hall badge at Ryu’s waist, So Yagran marks his name inside a structured black medicine case, and older beggar U Chil ties one small information knot to an inn pillar. Ma Yeongsun remains at the counter counting profit. Emphasize earned coalition and ownership rather than spectacle. The blue-jade Azure Peak Token must not appear in Ryu’s hand. Wide balanced group scene; no faux writing.

### `ch06-first-tomorrow-v1`

**References:** Ryu Dan, Myogak, Ma Yeongsun, Nam Sogun, So Yagran, U Chil; tomb style frame.
Climax in the damaged central chamber. Ryu Dan, sleeves shredded and wounds present, stands deliberately in the untouched eighth place and names First Tomorrow Step. Myogak faces him with exactly six remaining black eye-points after one has fallen; the six points visibly fail to align with Ryu’s new direction. Ryu’s movement follows present details—tilted flagstone, thin water film, disturbed flour dust, and a crooked bell vibration—without a giant aura. Ma Yeongsun and the three allies remain active in the composition but secondary. Use one restrained cinnabar trace for the broken formation, strong negative space around the new step, and no image of the Day 32 woman to avoid spoiling the final paragraph.

## Candidate log

| Prompt ID | Provider/model | Seed | Result |
|---|---|---:|---|
| `style-frame-01` | Pollinations legacy / flux | 9431 | Rejected: ignored scene and identities; one generic woman; fake writing |
| `style-frame-03` | Pollinations legacy / zimage | 9432 | Rejected: wrong figures and action; fake writing; unusable as reference |
| `ref-ryu-dan-v1` | OpenAI Codex / GPT Image 2 Medium | n/a | Approved |
| `ref-ma-yeongsun-v1` | OpenAI Codex / GPT Image 2 Medium | n/a | Approved |
| `ref-nam-sogun-v1` | OpenAI Codex / GPT Image 2 Medium + edit | n/a | Approved after thirteen-motif correction |
| `ref-myogak-v1` | OpenAI Codex / GPT Image 2 Medium + edit | n/a | Approved after seven-eye correction |
| `ch01-bowl-v1` | OpenAI Codex / GPT Image 2 High | n/a | Approved |
| `ch02-six-men-v1` | OpenAI Codex / GPT Image 2 High + edit | n/a | Approved after exact six-thug correction |
| `ch03-throat-touch-v1` | OpenAI Codex / GPT Image 2 High + edit | n/a | Approved after weapon-ownership correction |
| `ch04-returning-dish-v1` | OpenAI Codex / GPT Image 2 High + edit | n/a | Approved after expedition clothing/party correction |
| `ch05-auction-win-v1` | OpenAI Codex / GPT Image 2 High | n/a | Approved |
| `ch06-first-tomorrow-v1` | OpenAI Codex / GPT Image 2 High + edit | n/a | Approved after eye-count, clothing, and prop correction |

## Completion record

Approved references and final WebP scenes are stored beneath `assets/scenes/`. Exact bilingual placement, alt text, captions, model, prompt IDs, dates, and references are recorded in `manuscript/illustrations.json`. Any future replacement must repeat reference-driven generation, visual QA, mobile crop proof, EPUB proof, and the full release gate rather than silently overwriting an approved file.
