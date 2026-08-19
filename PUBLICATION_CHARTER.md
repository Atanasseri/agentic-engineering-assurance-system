# Publication Charter

> **Status:** Approved for public repository deployment
>
> **Public record:** Agentic Engineering Assurance System
>
> **Private source baseline:** `PTE-2026-08-19-v1.0.1`

## Purpose

This charter controls how a public technical system record may be derived from
a separate private evidence repository. Its objective is to make the work
understandable and professionally reviewable without exposing operational,
security-sensitive, personal, or authority-bearing information.

## Non-negotiable separation

The public repository is created from a clean history. It is not a fork,
history rewrite, filtered clone, or mirror of either the operational source or
the private evidence repository.

No public workflow may read, clone, modify, or automatically publish from the
private repositories. Derivation is a deliberate, owner-reviewed editorial
process.

## Permitted public content

- the engineering problem and system objective;
- the abstract responsibility and authority model;
- the bounded work-to-audit-to-release lifecycle;
- aggregate audit and disposition outcomes;
- selected engineering lessons;
- claim classifications and evidence limitations;
- the private baseline identifier and a non-reversible digest commitment;
- known limitations and reassessment triggers; and
- the owner's professional role and accountability.

## Content requiring sanitization

- tool-specific implementation details;
- internal workflow and document identifiers;
- internal repository, branch, path, and object locators;
- operational topology and environment-specific data;
- dates or names that reveal unnecessary internal context; and
- selected findings whose exact reproduction steps would weaken a control.

## Prohibited public content

- credentials, tokens, private keys, or authentication data;
- reusable authority tokens or decision secrets;
- session, bridge, pane, process, host, or account identifiers;
- filesystem paths from the operating environment;
- raw conversations, pane captures, or model transcripts;
- private audit, resolution, handoff, continuation, or decision records;
- source snapshots or manifests from the private evidence repository;
- personal or customer data unrelated to the public system record; and
- a moving branch reference presented as evidence.

## Claim rules

Every material public claim must state:

1. what is being claimed;
2. the kind of evidence supporting it;
3. whether the support is direct or qualified; and
4. what the evidence does not establish.

Use **verified** only for a directly reproduced or cryptographically checked
fact. Use **recorded** or **reported** for a result preserved in a committed
source record. Use **owner-confirmed** for a human-only observation. Use
**required** for a design contract.

Do not use *certified*, *formally verified*, *fully secure*, *zero risk*, or
*fully isolated* unless a qualified independent authority has established that
exact claim within an explicit scope.

## Release rule

A public release may be published only when:

- the local verifier passes;
- prohibited-content scanning passes;
- all material claims are present in the public evidence index;
- the owner approves the complete rendered content;
- the release commit and annotated tag are cryptographically signed;
- branch and tag protections are active;
- immutable releases are enabled before publication; and
- the release assets and their SHA-256 checksums are complete.

## Correction rule

A published release is never silently rewritten. A material correction creates
a successor release and explains what changed. The prior release remains
available unless it contains content whose continued publication creates a
security, privacy, or legal obligation to remove it.

## Approval record

Ata Nasseri approved public repository deployment on 2026-08-19. The approval
covers the complete sanitized content, professional identity and affiliation,
the split license model, and the disclosed aggregate audit figures.

This approval does not authorize creation of a release tag, publication of a
GitHub Release, or DOI archival. Those actions require a separate final owner
approval after repository controls and CI have been verified.
