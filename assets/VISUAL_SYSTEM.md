# AEAS Visual System

## Purpose

The AEAS visual system makes the public technical record faster to understand
without making its claims broader, stronger, or less qualified. Visuals are
editorial explanations of approved public content. They are not evidence,
runtime topology, external certification, or a substitute for the claim
register.

The visual language is designed around four ideas:

1. human authority remains visible and attributable;
2. implementation, audit, evidence, and release remain distinct;
3. the main reading path is clear before supporting detail is introduced; and
4. limitations remain visible wherever a visual could otherwise overstate the
   record.

## Design principles

### Meaning before decoration

Every node, connector, number, color, and annotation must explain a supported
relationship. Decorative infrastructure, invented topology, generic AI
imagery, and unreferenced metrics are excluded from explanatory diagrams.

### One focal decision

Each visual should use the authority accent for no more than one or two focal
elements. Color identifies semantic role; it is never applied merely to make
peer elements look different.

### Static first

Repository visuals are static, self-contained SVG files with a complete first
frame. They use no script, remote font, external stylesheet, embedded raster
image, or network dependency. Motion belongs only on the separate AEAS website
and must preserve an equivalent static state.

### Claim-governed visuals

Every public visual is registered in
[`visuals/manifest.json`](visuals/manifest.json) with:

- a stable visual identifier;
- its public claim identifiers;
- the public documents from which it is derived;
- concise non-claims;
- accessible alternative text;
- its approval status; and
- its intrinsic dimensions and view box.

Visual metadata records provenance and review boundaries. It does not turn an
illustration into evidence.

## Semantic color roles

The palette aligns with the existing AEAS social identity while using a quieter
editorial treatment for technical reading.

| Role | Light surface | Light ink/stroke | Dark surface | Dark ink/stroke | Meaning |
| --- | --- | --- | --- | --- | --- |
| Paper | `#F6F8FB` | `#101828` | `#07111F` | `#F2F4F7` | Canvas and primary text |
| Raised paper | `#FFFFFF` | `#344054` | `#0D1A2B` | `#D0D5DD` | Bounded nodes and tables |
| Muted | `#EEF1F5` | `#5F6B7A` | `#162337` | `#AEBAC9` | Supporting context |
| Structure | transparent | `#475467` | transparent | `#98A2B3` | Neutral implementation flow |
| Human authority | `#FFF3D6` | `#9A5B00` | `#2B2110` | `#F2B84B` | Owner decisions and authority gates |
| Audit | `#E7F8FB` | `#08798B` | `#0B2831` | `#45D3E8` | Read-only technical audit |
| Evidence | `#EAF1F8` | `#264B6B` | `#10283D` | `#88B8E0` | Durable records and evidence classes |
| Release | `#EDF1FF` | `#3548B5` | `#171F46` | `#9BACFF` | Release identity and archival path |
| Limitation | `#FFF0EE` | `#B42318` | `#351818` | `#FF8A80` | Qualification, exclusion, or unresolved boundary |

Color must always be paired with visible text, a line style, or a role label so
that meaning does not depend on color perception.

## Typography

- Primary family: `Segoe UI`, `Inter`, `Arial`, sans-serif.
- Technical labels: `SFMono-Regular`, `Consolas`, `Liberation Mono`, monospace.
- Maximum weights: 400, 600, and 700 for large numeric outcomes only.
- Sentence case is used for titles and labels.
- Acronyms and status vocabulary retain their canonical uppercase form.
- Text must remain readable when a wide visual is displayed at 720 CSS pixels.

No remote font is required. This removes a network dependency and keeps each
SVG self-contained.

## Geometry

- Base spacing unit: 8 pixels.
- Standard gaps: 16, 24, 32, 48, and 64 pixels.
- Standard node radius: 12 pixels.
- Structural border: 1.5 pixels.
- Primary connector: 2 pixels, solid.
- Evidence or reporting connector: 2 pixels, dashed.
- Maximum target density: approximately four out of ten.
- The normal repository view box is 960 units wide with height determined by
  the content.
- Explanatory layouts use no more than two content columns. Dense comparison
  structures must include a nearby Markdown table or list as a mobile and
  assistive-technology fallback.

Main flows read left to right and then top to bottom. Node titles are normally
22–26 SVG units and supporting copy 18–20 units at a 960-unit view box.
Vertical space is reserved for authority, evidence, qualifications, and
legends rather than for decorative whitespace.

## Connector grammar

| Connector | Meaning |
| --- | --- |
| Solid arrow | Authorized process or execution sequence |
| Dashed arrow | Reporting, recording, qualification, or evidence relationship |
| Amber line | Human authority entering a decision boundary |
| Cyan line | Read-only audit or evidence inspection |
| Neutral line | Implementation or structural flow |

Arrows never imply that approval automatically performs merge, publication,
deployment, or release. Those actions remain distinct.

## Status vocabulary

Visuals use the same bounded language as the public record:

- `SUPPORTED`
- `QUALIFIED`
- `DESIGN-CONTRACT`
- `COMMITTED-RECORD`
- `BASELINE-GIT-VERIFIED`
- `OWNER-CONFIRMED`
- `LIMITATION`
- `NOT_PERFORMED`

The words *certified*, *formally verified*, *fully secure*, *zero risk*, and
*fully isolated* are not used unless the corresponding claim is established by
an authorized independent source within an explicit scope.

## Accessibility contract

Every SVG must:

- declare `role="img"` and a resolving `aria-labelledby` value;
- begin with a non-empty `<title>` and `<desc>`;
- preserve a logical reading order in the document tree;
- use text labels in addition to color;
- avoid text smaller than 15 SVG units in a 960-unit view box;
- contain no flashing, autoplay, or time-dependent content; and
- remain understandable when printed in grayscale.

The Markdown page embedding the image must also provide concise alt text.

## Registered visual set

| Visual | Primary job | Default placement |
| --- | --- | --- |
| System map | Show the governed work-to-release path and evidence spine | Repository README |
| Recorded outcomes | Present bounded recorded results and their limitations | Repository README |
| Evidence and release chain | Separate claim discipline, release identity, persistence, and independent scrutiny | Repository README and Assurance Method |
| Authority matrix | Make non-interchangeable roles and decision rights explicit | System Overview |
| Social preview | Identify the work and accountable professional role when a repository link is shared | GitHub repository settings |

## Review and change control

1. Draft the visual only from approved public sources.
2. Register its claims, sources, non-claims, and alt text.
3. Run the publication verifier and visual-specific tests.
4. Render the complete SVG and inspect it at desktop and reduced width.
5. Obtain owner review before changing the metadata status to
   `OWNER_APPROVED`.
6. Treat a material visual correction as a new public change. Never rewrite the
   immutable `v1.0.0` Release or its archived assets.

The exact `v1.0.0` Release, signed release commit, signed annotated tag,
checksums, provenance, DOI records, and private evidence remain outside this
visual update.
