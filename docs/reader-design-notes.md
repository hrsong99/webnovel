# Reader redesign notes

## Direction

The second-pass reader uses the visual idea **“fractured iron, surviving record.”** It should feel like a small, carefully made edition of a novel rather than a publishing dashboard.

The interface borrows proven interaction patterns—not branding—from established long-form and serial readers:

- Kindle-style distraction-free prose and persistent local reading settings.
- Royal Road-style obvious chapter order and previous/next movement.
- Medium/Substack-style narrow text measure, quiet metadata, and typography-led pages.
- Wattpad’s mobile-first emphasis, while deliberately avoiding social and engagement clutter.

Research references consulted in August 2026:

- [Wattpad Redesign — Figma Community](https://www.figma.com/community/file/1543897749264917406/wattpad-redesign)
- [Royal Road design feedback: theme and contrast mistakes](https://www.royalroad.com/ideas/2917)
- [Long-form web typography recommendations](https://www.onething.design/post/best-fonts-for-websites)
- [Maru Buri font archive](https://github.com/fonts-archive/MaruBuri)
- [Pretendard](https://github.com/orioncactus/pretendard)

## Decisions

- Self-host Maru Buri for Korean prose and Pretendard for controls. No runtime font CDN.
- Keep body text around 41.5rem and 19px with generous leading.
- Do not indent every paragraph; spacing gives the eye a clearer mobile rhythm.
- Use one copper-red accent, warm paper, charcoal, and ruled lines.
- Preserve theme and font settings in `localStorage` only.
- Switch language without losing the current chapter.
- Keep reviewer notes collapsed by default because they intentionally reveal spoilers and structural analysis.
- Give Korean and English editions their own covers and downloadable ebooks.
- Avoid ratings, feeds, comments, login prompts, animated decoration, and generic card dashboards.

## Accessibility checks

- Semantic headings, navigation, `details`/`summary`, and progressbar roles.
- Keyboard-visible skip links and arrow-key chapter movement.
- Reduced-motion support.
- Controls retain text alternatives.
- Mobile layout at 390px has no horizontal scrolling.
- Themes maintain high text/background contrast.
