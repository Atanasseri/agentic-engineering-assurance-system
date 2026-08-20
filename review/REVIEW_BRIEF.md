# Independent Technical Review Brief

## Commissioning objective

Assess whether the signed public release of the Agentic Engineering Assurance
System is materially consistent with selected sealed private evidence and
whether its claims, qualifications, and limitations are professionally
supportable.

## Engagement record

| Field | Value |
| --- | --- |
| Commissioner | Ata Nasseri, Solofounders |
| Target Release | `v1.0.0` |
| Expected effort | To be agreed after conflict and evidence-access review |
| Commercial basis | `[paid, pro bono, or other — disclose in final report]` |
| Target dates | `[start]` to `[completion]` |
| Contact | Arranged through direct professional outreach |

## Object identity

| Object | Canonical reference |
| --- | --- |
| Repository | `https://github.com/Atanasseri/agentic-engineering-assurance-system` |
| Release | `v1.0.0` |
| Immutable GitHub Release | `https://github.com/Atanasseri/agentic-engineering-assurance-system/releases/tag/v1.0.0` |
| Release-evidence workflow | `https://github.com/Atanasseri/agentic-engineering-assurance-system/actions/runs/32308546078` |
| Release bundle SHA-256 | `598ca929037c78b856297143c932b54900cdc02ec99d36fb7dd132be2c7b10a9` |
| `SHA256SUMS` SHA-256 | `bc903bdbd0810e3800e0ebf3762c5a45b6ccfbe5a27380ee220a4e29b8d35d73` |
| Version DOI | `10.5281/zenodo.22019208` |
| Zenodo record | `https://zenodo.org/records/22019208` |
| Concept DOI, all versions | `10.5281/zenodo.22019207` |
| Machine-readable release identities | [`evidence/publication.json`](../evidence/publication.json) |

The reviewer must independently record the full release commit, annotated-tag
object, and later post-release publication-record commit. These are distinct
objects and must not be substituted for one another.

Zenodo's automatically generated source ZIP and the attested GitHub release
bundle are also distinct artifacts. The DOI establishes archival identity; it
does not establish that the two archives are byte-identical unless the reviewer
separately demonstrates that fact.

## Intended reviewer

A senior reviewer with relevant experience in at least two of the following:

- software assurance or secure software delivery;
- DevSecOps and release provenance;
- AI governance or agentic engineering;
- technical audit and evidence evaluation; or
- systems architecture and operational risk.

Professional certifications may support reviewer credibility, but relevant
experience, independence, disclosed methodology, and evidence-based reasoning
are more important than credentials alone.

## In-scope questions

1. Is the public system description materially consistent with the sampled
   private evidence?
2. Are audit counts, finding dispositions, and test statements represented
   accurately?
3. Are evidence classes and non-claims applied consistently?
4. Does the public record avoid material private or security-sensitive detail?
5. Are the signed release, checksums, provenance attestation, and DOI internally
   consistent?
6. Are limitations adequate for a reasonable technical or professional reader?

## Review method

The reviewer is expected to:

1. verify the public object identities and signatures independently;
2. inspect the complete public claim register;
3. independently recalculate every quantitative claim in scope, or identify
   each unverified claim as a limitation;
4. select non-quantitative evidence samples independently rather than accept
   only owner-selected examples;
5. record unavailable, withheld, substituted, or ambiguous evidence;
6. distinguish the attested GitHub release bundle from Zenodo's generated
   source archive; and
7. retain sole control over the final conclusion.

Owner responses and later corrections may be published separately. They do not
rewrite the reviewed historical Release or the reviewer's conclusion.

## Independence and tool disclosure

The reviewer must disclose prior work, personal or commercial relationships,
authorship, implementation involvement, compensation, and any other condition
that could reasonably affect perceived independence. A paid engagement is not
automatically disqualifying, but it must be disclosed.

Any material use of automated or AI-assisted review tools must be disclosed.
Private evidence must not be submitted to an external AI service or other third
party without explicit written authorization.

## Out of scope unless separately commissioned

- full source-code audit;
- penetration testing;
- live infrastructure assessment;
- legal or regulatory opinion;
- ISO or SOC conformity assessment;
- model safety evaluation;
- verification of every private evidence artifact; and
- a warranty of defect-free operation.

## Expected deliverables

- completed review checklist;
- findings with classification and evidence references;
- independence and conflict-of-interest declaration;
- signed public technical review statement; and
- optional confidential annex for sensitive observations.

## Evidence handling

The reviewer receives the minimum private evidence required for each sampled
claim. Access is read-only, confidential, and does not grant reuse or
publication rights. Raw evidence should not be copied into the public report.
