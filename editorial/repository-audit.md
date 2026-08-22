# Repository audit and redesign rationale

## Inferred purpose

The repository was an experiment in using conversational AI as a web-novel room: brainstorm a premise, expand a setting, create character and chapter templates, generate chapter plans, then turn those plans into Korean prose while carrying forward a glossary and character updates.

The commit history shows three story directions:

1. an isekai programmer in Murim (`initial-attempt`);
2. a physician who diagnoses martial arts (`main`), with ten drafted episodes;
3. a blacksmith who wants to abolish Murim (`new-story`), with a stronger thematic power system but no manuscript.

The latest design conversation explicitly chose the third direction and required a traditional wuxia progression based on internal-energy accumulation, physical thresholds, insight, minor breakthroughs, and hard realm gaps.

## What was worth preserving

- The abolitionist premise has a clear conflict that can scale from one village to the entire social order.
- “A dantian is a spiritual wound” connects the protagonist’s politics, the sect economy, child recruitment, medicine, cultivation, and eventual power in one rule.
- The five-stage 해리심경 progression ties insight to actual energy and physical capability rather than letting intelligence ignore speed and strength.
- The main-branch physician concept demonstrated two useful serial engines: a protagonist who solves fights through observation, and debts/records that turn individual encounters into a network.
- The source conversation records valuable intent and is preserved verbatim under `research/source/`.

## Why the previous workflow failed

### Inert schemas

The five YAML templates were instructions, not executable schemas. Nothing parsed them, assembled context, generated files, checked references, or built a book. One template listed an editable section named `chapters` that did not exist. The content template gave conflicting targets of 2,000–3,000 words and 3,000–4,000 characters.

### Duplicated truth

Chapter plans were stored once in `chapters/` and pasted again above the prose in `content/`. Character summaries, excerpts, author notes, and per-file change logs repeated information already available in source files and Git. Every duplicate created another place for canon to drift.

### Prompt history mistaken for canon

The 1,260-line Gemini export contains alternatives, superseded answers, and contradictions. Later consolidated files also disagree: the plot describes insight-led progression while the power document requires Mind, Energy, and Body to advance together. A future writer could choose either and still appear to follow the repository.

### No quality gate

There was no test, validator, renderer, or CI-like command. The old ten-chapter draft therefore shipped planning metadata as part of each chapter, contained unresolved `??` glossary references, and shortened from roughly 3,000–3,500 story characters in early episodes to roughly 1,950–2,260 in the back half.

Across the old draft, a few motifs became defaults rather than meaning:

- `혀끝`: 28 uses
- `종이`: 40 uses
- `장부`: 26 uses
- `세진은`: 98 uses

The same breath correction solved patients, ambushes, abduction, crowd control, and structural collapse. Supporting characters mostly acted as supply, records, force, prestige, archive access, or information delivery rather than people with incompatible wants.

### Scope outran causality

Ten short episodes attempted to launch a clinic, recruit a supplier and assistant, negotiate with three factions, stage a public duel, discover a hereditary disease, survive abduction, resolve simultaneous crises, create a neutrality charter, access sealed files, and begin research. Events followed the outline but did not have enough aftermath to cause one another emotionally.

## Simplest robust replacement

The replacement has four layers:

1. `story.json`: machine-readable publishing and validation contract.
2. `manuscript/story-bible.md`: one short canonical source for promise, characters, power limits, voice, and forbidden shortcuts.
3. `manuscript/outline.md`: causal episode design; each episode specifies a concrete reader payoff and irreversible turn.
4. `manuscript/chapters/*.md`: publishable prose only.

Everything else is either immutable research history or generated output.

`scripts/novel.py` is stdlib-only and provider-agnostic. It validates chapter sequence, count, headings, Korean-character bounds, placeholders, editorial leakage, and suspicious exact repetition. It builds Markdown, styled standalone HTML, TXT, and EPUB 3. Tests use temporary fixtures and parse the generated EPUB XML.

This is intentionally not an automated “write me a novel” API. Creative generation remains replaceable; deterministic validation and packaging remain stable. Quality comes from a bounded story contract followed by independent developmental, continuity, and Korean line-edit passes—not from sending the entire repository back to one model repeatedly.

## Story implementation choice

The six-episode first volume compresses the old 30-chapter runway without removing progression:

- catastrophe and the hollow apology;
- the failure of law and the creation of a victim ledger;
- discovery that sects deliberately traumatize children to open dantians;
- proof that internal energy exploits a wound;
- acquisition of 해리심경 and the protagonist’s decision to become what he opposes;
- a first victory at 삼류 초입 against a 삼류 후반 opponent through preparation, perception, 해기, and efficient movement.

The protagonist cannot cross a full realm gap through cleverness. Smithing and communal rhythm create conditions; cultivation supplies the perception, energy, and body needed to act. Permanent deconstruction remains a distant transcendent ability and an unresolved political danger.
