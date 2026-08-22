# Rendered proof log — <title / release candidate>

**Commit/worktree:**
**Proofreader:**
**Date:**
**Source edition(s):**

## Artifact matrix

| Artifact | Route/file | Viewport/device/app | Checks | Result | Evidence/finding IDs |
|---|---|---|---|---|---|
| Catalog | `/` | desktop + mobile | cards, covers, language links, overflow |  |  |
| Story home |  | desktop + mobile | title, cover, metadata, resume |  |  |
| Chapter |  | desktop + mobile | prose, focus mode, images, navigation |  |  |
| Standalone HTML |  | browser | order, headings, escaping |  |  |
| EPUB |  | EPUB reader + ZIP/XML | TOC, chapters, images, alt/caption |  |  |
| TXT/MD |  | text editor | completeness, order, encoding |  |  |

## Interaction proof

- [ ] Focus toggle has a clear accessible name and `aria-pressed`
- [ ] Active tap advances; inactive tap jumps
- [ ] Selection and swipe do not advance
- [ ] Space/J/Down and Shift+Space/K/Up behave correctly
- [ ] Escape exits
- [ ] Final paragraph reveals navigation without auto-following
- [ ] Manual scroll does not fight programmatic scroll
- [ ] Reduced-motion mode moves instantly
- [ ] Theme, font size, language, previous/next, and TOC remain functional

## Visual and accessibility proof

- [ ] No horizontal overflow at 360px, 390px, tablet, and desktop widths
- [ ] Active and ordinary prose have readable contrast in light, sepia, and dark themes
- [ ] Images preserve aspect ratio and critical crop at mobile width
- [ ] Every meaningful image has localized alt text
- [ ] Captions do not reveal premature spoilers
- [ ] No font fallback, clipping, overlap, fake writing, watermark, or broken anatomy escaped review

## Freeze policy

After rendered proof begins, fix typographic, continuity, accessibility, or release-blocking issues only. If a fix changes scene structure, canon, paragraph numbering, or image placement, reopen the relevant editorial gate and rerun this proof.

## Signoff

- [ ] All blockers closed and verified
- [ ] Final generated artifacts match the recorded source commit
