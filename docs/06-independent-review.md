# Independent Review

> **Current status:** `NOT_PERFORMED`
>
> No external reviewer has been appointed, no independent conclusion has been
> issued, and this repository makes no claim of certification.

## Purpose

The planned engagement is a scoped independent technical review of Release
`v1.0.0`, selected supporting private evidence, and the later public record that
documents the observed Release and DOI.

The signed release commit and the later post-release publication-record commit
are different objects. The reviewer must bind the technical conclusion to the
commit reached by the signed `v1.0.0` tag and identify the later record only as
post-release evidence. Release and archival identities are recorded in
[`evidence/publication.json`](../evidence/publication.json); that file does not
identify the later publication-record commit, which the reviewer must derive
independently from Git history.

## Intended assurance level

The review is not automatically:

- an ISO certification;
- a SOC examination;
- a legal opinion;
- a penetration test;
- a full source-code audit; or
- a guarantee of defect-free operation.

## Review objective

The reviewer will assess whether:

1. the public system description is materially consistent with the selected
   private evidence;
2. aggregate findings and dispositions are accurately represented;
3. evidence qualifications and non-claims are preserved;
4. the public repository avoids prohibited private detail;
5. the signed release, digest manifest, and DOI identify the reviewed object;
   and
6. the limitations are sufficient for a reasonable reader to understand the
   assurance boundary.

## Evidence access

Private evidence access should be:

- read-only;
- limited to the minimum material needed for the review;
- time-bounded where practical;
- subject to confidentiality terms; and
- revoked after the review unless a different retention period is agreed.

## Required final statement

The public report must identify:

- reviewer name, organization, role, and relevant qualifications;
- conflict-of-interest declaration;
- exact repository, release commit, signed tag, tag object, Release, and
  version DOI;
- the later post-release publication-record commit as a separate object;
- review dates and methods;
- evidence inspected and independently selected samples;
- findings and qualifications;
- excluded scope;
- conclusion; and
- reviewer-controlled signature or independently verifiable digital approval.

The conclusion vocabulary is:

- `CONFIRMED`: sufficient evidence was obtained and no unresolved material
  inconsistency was identified within scope.
- `CONFIRMED WITH QUALIFICATIONS`: the core conclusion is supportable, but
  stated evidence or scope limitations materially narrow reliance.
- `NOT CONFIRMED`: evidence was insufficient or an unresolved material
  inconsistency was identified.

## Publication rule

The reviewer controls the wording and conclusion of the final statement. The
owner may publish an unmodified copy and a clearly separated owner response,
but may not edit the reviewer's report.

The public statement must have a stable URL and a reviewer-controlled signature
or independently verifiable approval. Its SHA-256 digest must be published
outside the report itself in a signed checksum, Git, release-manifest, detached
signature, or equivalent verification record. If a confidential annex affects
the conclusion, the public statement must disclose its existence and effect
without exposing sensitive evidence.

Only after that statement has been verified may a successor commit change the
machine-readable status from `NOT_PERFORMED`. Release `v1.0.0` remains
unchanged.
