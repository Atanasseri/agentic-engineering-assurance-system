# Visual Assets

This directory contains the repository's public visual assets.

## Repository social preview

[`visuals/social-preview.png`](visuals/social-preview.png) is the primary
1280×640 social preview for the repository. It presents the system's governance,
audit, evidence, and release flow as a conceptual visual; it is not evidence and
does not reconstruct the private operating topology.

The composition identifies the accountable professional role used throughout
the public record:

> **Ata Nasseri, System Designer and Assurance Owner**

To activate it on GitHub, upload the PNG under **Settings → General → Social
preview** after the signed documentation change is merged.

## Implemented explanatory visuals

| Asset | Purpose | Primary placement |
| --- | --- | --- |
| [`visuals/system-map.svg`](visuals/system-map.svg) | Governed work-to-release lifecycle and durable-record spine | Repository README |
| [`visuals/recorded-outcomes.svg`](visuals/recorded-outcomes.svg) | Bounded recorded outcomes with evidence-class labels and visible non-claims | Repository README |
| [`visuals/evidence-release-chain.svg`](visuals/evidence-release-chain.svg) | Separation of claim discipline, the later public release record, and independent scrutiny | Repository README and Assurance Method |
| [`visuals/authority-matrix.svg`](visuals/authority-matrix.svg) | Decision rights, role limits, and durable controls | System Overview |

The [AEAS Visual System](VISUAL_SYSTEM.md) defines the semantic palette,
typography, connector grammar, accessibility contract, and change controls.
The machine-readable [`visuals/manifest.json`](visuals/manifest.json) registers
every PNG and SVG with its dimensions, claim identifiers, sources, explicit
non-claims, independent-review status, and owner-approval status.

Each explanatory visual has adjacent Markdown text or a table as a fallback.
New visuals enter the manifest as `DRAFT`. Only the Assurance Owner may change
their status to `OWNER_APPROVED` after reviewing the exact renders in an
authorized change.
