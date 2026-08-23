# Web-novel production playbook

This document preserves the editorial and technical lessons learned while turning this repository into **《무림철폐론자》**. It belongs to the project—not to a particular model, agent, or private conversation—and should evolve with the manuscript.

## 1. Canon has layers

Treat these as the accepted sources of truth, in order:

1. `catalog.json`: published, planning, and retired lifecycle membership plus public story order.
2. `stories/<slug>/story.json` and locale metadata: each story’s publishing contract.
3. `stories/<slug>/manuscript/story-bible.md`: premise, cast, power rules, continuity, prohibited shortcuts.
4. `stories/<slug>/manuscript/outline.md`: causal chapter design and promised payoff.
5. `stories/<slug>/manuscript/chapters/`: Korean source edition.
6. `stories/<slug>/manuscript/translations/`: editions derived from the Korean source.
7. `stories/<slug>/manuscript/reviewer-notes/`: editorial summaries, not story canon.
8. `research/`: design evidence and history, not story canon.

Never copy plans, change logs, prompt history, or editorial notes into publishable prose. Git stores history; the manuscript should contain only the book.

Planning projects and retired stories may remain under `stories/<slug>/`, but only `catalog.json` → `stories` is publishable. Their primary metadata status must match their lifecycle bucket. Never use an incomplete draft as a public-catalog placeholder, and never delete a released predecessor merely to free its catalog position.

## 2. Reconstruct intent before drafting

When inheriting a fiction repository:

- inspect every relevant branch and recent commit;
- read raw conversations, but separate accepted choices from discarded ideas;
- identify the newest coherent direction rather than assuming the default branch is current;
- extract non-negotiable rules: point of view, progression ceiling, moral promise, chapter size, terminology, and language.

A long design transcript is evidence, not canon.

## 3. Genre rules belong to a story, not to this document

[`fiction-craft-standard.md`](fiction-craft-standard.md) is the genre-independent gate. Everything narrower than that — the per-chapter contract, progression-fairness ceiling, supporting-cast rules, reward cadence, prohibited shortcuts — belongs in the story's own `manuscript/craft-overlay.md`, copied from [`story-craft-overlay-template.md`](story-craft-overlay-template.md).

One serial's successful habits are not universal craft. Keeping them in the story that earned them is what lets a second story disagree without arguing with a repository-wide document.

Worked examples:

- [`stories/murim-abolitionist/manuscript/craft-overlay.md`](../stories/murim-abolitionist/manuscript/craft-overlay.md) — institutional wuxia: chapter gate, progression fairness, supporting-cast leverage.
- [`stories/seven-masters-returned/manuscript/craft-overlay.md`](../stories/seven-masters-returned/manuscript/craft-overlay.md) — reward-dense progression planning package.

## 4. Separate mechanical validation from editing

The build can reliably check:

- chapter count and numbering;
- heading form;
- source-language character bounds;
- placeholders and planning-note leakage;
- suspicious exact repetition;
- translation completeness;
- generated website and ebook structure.

It cannot score emotional truth, tension, dialogue, or prose quality. Do not invent a numerical literary-quality formula.

## 5. Three editorial passes

### Developmental and continuity

Check causality, stakes, timeline, travel, injuries, objects, death counts, information flow, agency, power legality, leverage, payoff, and hooks.

### Language and anti-pattern

Check natural syntax, sentence rhythm, repeated subject starts, slogan dialogue, abstract moralizing after scenes, translated collocations, vague pronouns, repeated metaphors, and exposition density. Protect a written list of excellent lines and scenes before revising.

### Independent release QA

After revision, verify every earlier blocker against the current files. Reviewers’ quotations become stale after edits; the present manuscript wins. A release PASS means no blocking defect remains, not that optional improvements are impossible.

## 6. Translation is a new edition

- Translate scenes, intent, hierarchy, and rhythm—not Korean word order.
- Maintain a project glossary and character-name policy.
- Keep cultivation terms stable across chapters.
- Do not add facts or clarify ambiguity that the Korean text intentionally preserves.
- Recheck injuries, objects, titles, place names, and power stages after translation.
- Have a separate editor read the English continuously for voice and repeated phrasing.

The Korean manuscript remains the source edition. English corrections that reveal a source contradiction should be fixed in Korean first.

## 7. Reviewer summaries are not blurbs

A reviewer overview should explain:

- the opening situation;
- major causal turns and revelations;
- each principal character’s decision and leverage;
- the chapter’s thematic or structural job;
- the ending state and next pressure;
- any deliberate limitation on victory or progression.

It may discuss spoilers. Keep it collapsible and visually distinct so ordinary readers are not exposed accidentally.

## 8. The repository is also the publication system

The deterministic build should generate from canonical files:

- a library/landing page;
- stable per-language, per-chapter URLs;
- previous/next navigation and a table of contents;
- local-only progress, theme, and typography preferences;
- a language switch that preserves chapter position;
- reviewer summaries;
- cover art and metadata;
- EPUB, TXT, Markdown, and standalone HTML;
- health and crawler files.

Avoid external font/CDN dependencies. Escape manuscript content before putting it in HTML. No login is needed for a public first release.

## 9. Reader-design principles

Successful long-form readers such as Kindle Cloud Reader, Royal Road, Medium, and Substack converge on a few useful patterns:

- the chapter text is the dominant object;
- line length is roughly 35–45rem, with generous leading;
- controls are quiet, stable, and available without becoming a dashboard;
- previous/next actions are obvious at the end;
- progress and preferences are remembered locally;
- mobile controls fit one row and text never requires horizontal scrolling;
- theme, font size, and language are user choices;
- metadata and community chrome stay away from the prose.

This reader also offers an optional focus mode. It is not auto-scroll: the reader controls each step. Activating `◎` centers the nearest paragraph, de-emphasizes surrounding units, and advances only on an explicit tap, Space, or arrow key. Escape exits immediately. Motion must honor `prefers-reduced-motion`, ordinary scrolling must remain available, and images may participate as focus units without trapping keyboard or touch users.

Borrow patterns, not branding or ornamental clutter.

The concrete values, sources, and accessibility checks actually adopted for this repository's reader are recorded in [`reader-design-notes.md`](reader-design-notes.md).

## 10. Illustration publishing contract

Illustration is an opt-in track. This contract governs stories that have requested images; it is not a checklist every story must satisfy.

- Keep canonical prose free of provider-specific image syntax.
- Define approved scenes in `manuscript/illustrations.json` with language-specific paragraph placement.
- Store final files beneath `assets/scenes/`; never hotlink expiring provider URLs.
- Require non-empty alt text for every published language.
- Record provider, model, prompt ID, generation date, seed, and reference assets in repository-owned visual material.
- Build character and location references before recurring scenes; a shared seed alone is not identity control.
- Reject watermarks, fake writing, anatomy defects, character drift, illegal power effects, wrong injuries, and spoiler-heavy placement.
- Prove the image remains legible at mobile width and does not create horizontal overflow.

## 11. Docker and deployment

Use a multi-stage image:

1. Python builder copies canon, translations, summaries, generator, assets, and tests.
2. Tests, manuscript validation, and site generation run during image build.
3. Only generated `dist/` enters an unprivileged Nginx runtime.
4. Serve on explicit port `8080` with `/healthz`.
5. Cache fingerprint-stable assets aggressively and HTML conservatively.
6. Require no database, environment variable, login secret, or persistent volume for the static reader.

Before release, genuinely build and run the container. Verify every internal link, health state, non-root user, headers, EPUB ZIP/XML, and rendered desktop/mobile screenshots.

## 12. Safe release procedure

- Run tests, validation, build, link crawl, browser screenshots, Docker build/run, whitespace checks, and a secret scan.
- Preserve an old default-branch story with a remote backup branch before replacing it.
- Push a feature branch, let CI pass, merge, and verify the exact remote `main` SHA.
- A configured deploy hook is not proof of deployment. Verify the public HTTPS site separately when its URL is available.

## 13. Subagent discipline

- Concurrent reviewers may inspect the same manuscript, but only one integrated editor should revise it.
- A timed-out writer may still have changed files; inspect the worktree rather than trusting its status summary.
- Re-run all checks in the parent context.
- Treat every subagent report as advice until current files and executable output confirm it.
