# Public Evidence Index

<!-- public-claims: ARC-001 AUD-001 AUD-002 AUD-003 AUD-004 AUD-005 BND-001 GOV-001 GOV-002 OPS-001 OPS-002 REL-001 REL-002 REL-003 REV-001 SYS-001 SYS-002 TST-001 -->

## Purpose

This index states what the public record supports and what each statement does
not establish. It provides a readable view of the machine-readable register in
[`evidence/public-claims.json`](../evidence/public-claims.json).

## Private baseline commitment

| Field | Public value |
| --- | --- |
| Baseline ID | `PTE-2026-08-19-v1.0.1` |
| Baseline manifest SHA-256 | `ecd87eb9581e535c95dee1beb0871fa5fc1382c9d3847eb5ebba337bc5ef827f` |
| Disclosure | The underlying manifest and evidence remain private |

The digest can support later controlled comparison. It does not disclose the
private manifest or prove its substantive accuracy.

## Material claims

| ID | Public claim | Support | Important boundary |
| --- | --- | --- | --- |
| `SYS-001` | The system separates owner authority, implementation, read-only audit, evidence, and release. | `DESIGN-CONTRACT` | Operational separation is not external institutional independence. |
| `GOV-001` | Review is bound to exact source and durable transition records. | `DESIGN-CONTRACT` | The design does not prove every implementation is correct. |
| `GOV-002` | The final review was limited to two owner-authorized audit rounds. | `COMMITTED-RECORD` | Final-round fixes did not receive an unauthorized third round. |
| `AUD-001` | Seven audit reports were preserved across three governed reviews. | `BASELINE-GIT-VERIFIED` | One attempted round was explicitly not auditable. |
| `AUD-002` | The reports contain 33 findings: 11 HIGH and 22 MEDIUM; none is recorded as CRITICAL. | `BASELINE-GIT-VERIFIED` | This does not prove no undiscovered defect existed. |
| `AUD-003` | Resolution records mark 32 findings as fixed and one as settled through an owner-ratified criteria revision. | `COMMITTED-RECORD` | The revised criterion is not presented as originally met. |
| `AUD-004` | Three final-round findings were defects in earlier corrections. | `COMMITTED-RECORD` | This is a recorded remediation history, not proof that all later fixes were defect-free. |
| `AUD-005` | Each substantive audit report recorded a changes-required verdict. | `BASELINE-GIT-VERIFIED` | This does not mean remediation was never completed. |
| `TST-001` | The completion record reports 1,111 tests green in both test tiers. | `COMMITTED-RECORD` | The exact final raw run was not preserved in the private evidence set. |
| `OPS-001` | Existing project environments were recorded as migrated and locally connected without project-specific drift. | `COMMITTED-RECORD` | This does not establish future runtime state or application visibility. |
| `OPS-002` | The owner separately confirmed the final application-visible state. | `OWNER-CONFIRMED` | Human observation is not cryptographic remote attestation. |
| `REL-001` | Approval and release were modeled as separate controlled actions. | `DESIGN-CONTRACT` | Approval alone does not prove that a release occurred. |
| `REL-002` | The completion record reports a versioned correctness release. | `COMMITTED-RECORD` | The public repository does not independently reproduce the private release. |
| `REL-003` | The later publication record records the signed release commit, signed annotated tag, immutable GitHub Release, checksums, and artifact-attestation workflow for `v1.0.0`. | `COMMITTED-RECORD` | These controls establish identity, integrity, and provenance, not software correctness or independent review. |
| `ARC-001` | The later publication record identifies the version and concept DOI for this public record. | `COMMITTED-RECORD` | DOI persistence is not certification or proof that distinct archives are byte-identical. |
| `REV-001` | Independent technical review has not been performed and no external certification is claimed. | `LIMITATION` | A prepared review package is not a completed review or a predicted reviewer conclusion. |
| `BND-001` | The implemented assurance has explicit isolation, liveness, evidence, and review limits. | `LIMITATION` | The system is not presented as fully isolated, formally verified, or defect-free. |
| `SYS-002` | The completion record reports the capability categories summarized here. | `COMMITTED-RECORD` | The summary is not a public reconstruction of the private implementation. |

## Interpretation

The most important result is not the finding count by itself. It is the chain
connecting accountable scope, exact source identity, technical findings,
explicit dispositions, human decisions, release identity, and bounded
operational verification.

## Controlled independent access

A qualified reviewer may be given controlled access to the private baseline to
confirm selected public claims. Access does not grant publication or reuse
rights and should be governed by confidentiality and minimum-necessary scope.
