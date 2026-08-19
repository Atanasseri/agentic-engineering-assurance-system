# Limitations and Reassessment

<!-- public-claims: BND-001 -->

## Why limitations are part of the result

Assurance is credible only when its boundary remains visible. The following
limitations are retained because omitting them would make the public record
stronger in appearance but weaker in substance.

## Known limitations

| Limitation | Practical meaning |
| --- | --- |
| Operational audit separation | The audit role was technically separated and read-only, but it was not an external certification body. |
| Shared implementation boundary | Project environments were logically and operationally separated, not isolated by a dedicated OS identity or container per project. |
| Narrow command control | A constrained source-control interface is not a general filesystem sandbox. |
| Local readiness evidence | Local operational indicators are not cryptographic server attestation. |
| Session liveness | An existing but unresponsive session may satisfy a structural indicator. |
| Content-blind diagnosis | Some trust, onboarding, authentication, and crash states can look similar without inspecting content. |
| Time-of-check boundary | Filesystem containment checks reduce risk but are not an atomic kernel-enforced boundary. |
| Opt-in operational testing | The default suite does not exercise every live-host control. |
| Maintained inventories | Versioned infrastructure inventories require disciplined manual maintenance. |
| Bounded audit rounds | Final-round fixes were not followed by an unauthorized third audit round within the same review. |
| Recovery scope | Not every stranded workflow state has a fully automated recovery path. |
| Source identity | Historical Git identities establish byte identity, not cryptographic proof of every author's identity. |
| Final test artifact | The completion record reports the final green runs, but their exact raw output was not retained in the sealed evidence set. |
| Trust revocation | The bounded trust flow does not provide a tool-level revocation mechanism for the user-level record. |

## Residual-risk interpretation

Owner approval records that known residual risks were considered within the
defined scope. Approval does not eliminate those risks or make them acceptable
for every future use.

## Reassessment triggers

A new private evidence baseline and public successor release should be
considered when:

- an audit, identity, trust, containment, or release boundary changes;
- the audit role or source-export mechanism changes;
- project environments gain stronger OS or container isolation;
- the workflow changes its audit-round model;
- remote-control tooling provides stronger server-side evidence;
- automated recovery or resident monitoring is added;
- reproducible raw test artifacts become part of the release; or
- an independent reviewer identifies a material qualification or inconsistency.

## Public correction policy

Published releases are historical records. A correction creates a successor
release and records:

- the affected public claim;
- the reason for correction;
- whether the private baseline changed;
- the replacement wording or evidence; and
- the continued validity, withdrawal, or qualification of the earlier release.
