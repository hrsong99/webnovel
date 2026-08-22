# Visual bible — <title>

## Art direction

- **Style ID:** `<stable short id>`
- **One-line direction:**
- **Medium and texture:**
- **Line quality:**
- **Color palette:**
- **Lighting language:**
- **Composition:**
- **Emotional tone:**
- **Must avoid:** photoreal celebrity resemblance, generic game UI, fake text, signatures, watermarks, modern objects, anachronistic clothing, uncontrolled gore.

## Character identity anchors

Create one section per recurring character. Identity anchors should be visually checkable and stable across every scene.

### <Character>

- **Age and build:**
- **Face shape and features:**
- **Hair:**
- **Default expression and posture:**
- **Base clothing:**
- **Chapter-specific changes:**
- **Signature prop/weapon:**
- **Handedness:**
- **Relative height:**
- **Never show:**
- **Approved reference asset:** `assets/scenes/references/<file>`

## Locations

### <Location>

- **Architecture and materials:**
- **Layout anchors:**
- **Palette and lighting:**
- **Weather/season:**
- **Chapter-specific damage or change:**
- **Approved reference asset:**

## Props and symbols

| Prop/symbol | Shape/material | Scale | Ownership | Chapter state | Never confuse with |
|---|---|---|---|---|---|
|  |  |  |  |  |  |

## Scene shot list

Select at most one or two images per chapter.

| ID | Ch. | After paragraph | Narrative moment | Visual purpose | Spoiler risk | Aspect |
|---|---:|---:|---|---|---|---|
| ch01-01 | 1 |  |  |  | low/medium/high | 16:9 |

## Prompt contract

Every scene prompt should include:

1. the exact approved style ID and art direction;
2. only characters present, with immutable identity anchors repeated verbatim;
3. canon-correct clothing, injuries, objects, abilities, place, weather, and time;
4. one decisive action and one emotional relationship;
5. camera distance, lens/composition, and negative space for mobile cropping;
6. explicit negative constraints: no text, watermark, signature, modern objects, extra people, duplicate limbs, or wrong props.

Do not rely on a shared seed alone for identity. Use the approved character/style reference images through an edit-capable model whenever possible.

## Generation record

| ID | Provider | Model | Seed | Prompt version | Reference assets | Generated file | Review status |
|---|---|---|---:|---|---|---|---|
|  |  |  |  |  |  |  | candidate/approved/rejected |

## Visual QA

- [ ] Faces, age, build, hair, clothing, and handedness match references
- [ ] Person and object counts are correct
- [ ] Injuries and power effects are legal at this point
- [ ] Time of day and location state match canon
- [ ] No fake writing, watermark, signature, or modern artifact
- [ ] Hands, eyes, weapons, and contact points are anatomically legible
- [ ] Image remains clear at 360px width
- [ ] Crop does not remove the story-critical action
- [ ] Alt text describes narrative information without decorative prompt language
- [ ] Caption does not spoil unrevealed information
- [ ] Provider, model, seed, prompt, references, and date are recorded
