# Web-novel production playbook

This document preserves the editorial and technical lessons learned while turning this repository into **《무림철폐론자》**. It belongs to the project—not to a particular model, agent, or private conversation—and should evolve with the manuscript.

## 1. Canon has layers

Treat these as the accepted sources of truth, in order:

1. `story.json` and locale metadata: publishing contract.
2. `manuscript/story-bible.md`: premise, cast, power rules, continuity, prohibited shortcuts.
3. `manuscript/outline.md`: causal chapter design and promised payoff.
4. `manuscript/chapters/`: Korean source edition.
5. `manuscript/translations/`: editions derived from the Korean source.
6. `manuscript/reviewer-notes/`: editorial summaries, not story canon.
7. `research/source/`: design history only.

Never copy plans, change logs, prompt history, or editorial notes into publishable prose. Git stores history; the manuscript should contain only the book.

## 2. Reconstruct intent before drafting

When inheriting a fiction repository:

- inspect every relevant branch and recent commit;
- read raw conversations, but separate accepted choices from discarded ideas;
- identify the newest coherent direction rather than assuming the default branch is current;
- extract non-negotiable rules: point of view, progression ceiling, moral promise, chapter size, terminology, and language.

A long design transcript is evidence, not canon.

## 3. What makes a chapter work

Every chapter should contain:

- a concrete discovery;
- a decision that closes another option;
- a cost or changed relationship;
- a reader payoff in the present chapter;
- a forward turn that makes the next action unavoidable.

If a chapter is too short, deepen causality, choices, aftermath, relationships, and physical action. Do not pad scenery or repeat the premise.

## 4. Progression-fantasy fairness

Intelligence cannot erase declared differences in speed, body, internal energy, or realm.

- State exactly what the protagonist can perceive and physically do at the current stage.
- Keep future-stage abilities unavailable even at the climax.
- Let preparation, terrain, allies, records, and opponent incentives matter.
- Institutional antagonists need a rational reason to retreat: contract loss, exposed evidence, desertion, political cost, or material danger.
- A victory is stronger when it proves the theme without breaking the power system.

For this series, tools amplify training and observation; they do not replace 해기, 심안, or 이형신법.

## 5. Supporting characters must have incompatible needs

Do not reduce supporting characters to supplies, archives, muscle, prestige, or exposition.

- Give each person something they protect that the protagonist might endanger.
- Let partners impose enforceable limits, not merely offer advice.
- Make disagreements change custody, access, money, shelter, records, or consent.
- Villains should pursue loss avoidance according to their own position in the system.

Yeonhwa works because she converts Jin Cheol’s anger into governance and can deny him resources. Preserve that level of agency.

## 6. Separate mechanical validation from editing

The build can reliably check:

- chapter count and numbering;
- heading form;
- source-language character bounds;
- placeholders and planning-note leakage;
- suspicious exact repetition;
- translation completeness;
- generated website and ebook structure.

It cannot score emotional truth, tension, dialogue, or prose quality. Do not invent a numerical literary-quality formula.

## 7. Three editorial passes

### Developmental and continuity

Check causality, stakes, timeline, travel, injuries, objects, death counts, information flow, agency, power legality, leverage, payoff, and hooks.

### Language and anti-pattern

Check natural syntax, sentence rhythm, repeated subject starts, slogan dialogue, abstract moralizing after scenes, translated collocations, vague pronouns, repeated metaphors, and exposition density. Protect a written list of excellent lines and scenes before revising.

### Independent release QA

After revision, verify every earlier blocker against the current files. Reviewers’ quotations become stale after edits; the present manuscript wins. A release PASS means no blocking defect remains, not that optional improvements are impossible.

## 8. Translation is a new edition

- Translate scenes, intent, hierarchy, and rhythm—not Korean word order.
- Maintain a project glossary and character-name policy.
- Keep cultivation terms stable across chapters.
- Do not add facts or clarify ambiguity that the Korean text intentionally preserves.
- Recheck injuries, objects, titles, place names, and power stages after translation.
- Have a separate editor read the English continuously for voice and repeated phrasing.

The Korean manuscript remains the source edition. English corrections that reveal a source contradiction should be fixed in Korean first.

## 9. Reviewer summaries are not blurbs

A reviewer overview should explain:

- the opening situation;
- major causal turns and revelations;
- each principal character’s decision and leverage;
- the chapter’s thematic or structural job;
- the ending state and next pressure;
- any deliberate limitation on victory or progression.

It may discuss spoilers. Keep it collapsible and visually distinct so ordinary readers are not exposed accidentally.

## 10. The repository is also the publication system

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

## 11. Reader-design principles

Successful long-form readers such as Kindle Cloud Reader, Royal Road, Medium, and Substack converge on a few useful patterns:

- the chapter text is the dominant object;
- line length is roughly 35–45rem, with generous leading;
- controls are quiet, stable, and available without becoming a dashboard;
- previous/next actions are obvious at the end;
- progress and preferences are remembered locally;
- mobile controls fit one row and text never requires horizontal scrolling;
- theme, font size, and language are user choices;
- metadata and community chrome stay away from the prose.

Borrow patterns, not branding or ornamental clutter.

## 12. Docker and deployment

Use a multi-stage image:

1. Python builder copies canon, translations, summaries, generator, assets, and tests.
2. Tests, manuscript validation, and site generation run during image build.
3. Only generated `dist/` enters an unprivileged Nginx runtime.
4. Serve on explicit port `8080` with `/healthz`.
5. Cache fingerprint-stable assets aggressively and HTML conservatively.
6. Require no database, environment variable, login secret, or persistent volume for the static reader.

Before release, genuinely build and run the container. Verify every internal link, health state, non-root user, headers, EPUB ZIP/XML, and rendered desktop/mobile screenshots.

## 13. Safe release procedure

- Run tests, validation, build, link crawl, browser screenshots, Docker build/run, whitespace checks, and a secret scan.
- Preserve an old default-branch story with a remote backup branch before replacing it.
- Push a feature branch, let CI pass, merge, and verify the exact remote `main` SHA.
- A configured deploy hook is not proof of deployment. Verify the public HTTPS site separately when its URL is available.

## 14. Subagent discipline

- Concurrent reviewers may inspect the same manuscript, but only one integrated editor should revise it.
- A timed-out writer may still have changed files; inspect the worktree rather than trusting its status summary.
- Re-run all checks in the parent context.
- Treat every subagent report as advice until current files and executable output confirm it.
