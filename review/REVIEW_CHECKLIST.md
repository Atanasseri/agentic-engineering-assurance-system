# Independent Review Checklist

## Reviewer identity and independence

- [ ] Name, organization, role, and relevant qualifications recorded.
- [ ] Commercial, personal, authorship, and implementation relationships disclosed.
- [ ] Reviewer confirms no implementation responsibility for the reviewed release.
- [ ] Any limitation on independence is described.
- [ ] Compensation basis is disclosed.

## Object identity

- [ ] Canonical repository confirmed.
- [ ] Full release commit independently recorded.
- [ ] Later post-release publication-record commit recorded separately.
- [ ] Signed annotated tag and tag-object identity verified.
- [ ] Immutable GitHub Release verified.
- [ ] Release asset SHA-256 values verified.
- [ ] Artifact provenance verified.
- [ ] Version DOI `10.5281/zenodo.22019208` resolves to the `v1.0.0` record.
- [ ] The concept DOI is treated only as the all-versions identifier.
- [ ] The Zenodo-generated archive and attested GitHub bundle are not presented
      as byte-identical unless separately verified.

## Claim evaluation

- [ ] Every quantitative public claim in scope was independently recalculated.
- [ ] Every quantitative exception is listed as an evidence limitation.
- [ ] Non-quantitative samples were selected by the reviewer after reviewing
      the complete claim register.
- [ ] Unavailable, withheld, substituted, or ambiguous evidence is recorded.
- [ ] Audit-report count and severity totals independently recounted.
- [ ] Finding dispositions sampled against resolution records.
- [ ] Criteria revision remains distinguishable from a fix.
- [ ] Test language remains qualified as a committed record.
- [ ] Human-only observation remains separate from local technical evidence.
- [ ] Final-round review boundary is not omitted.

## Sanitization

- [ ] No private source locator is published.
- [ ] No operational path, account, host, session, or process identifier is published.
- [ ] No authority token, credential, key, or authentication material is published.
- [ ] No raw transcript, pane capture, or private decision text is published.
- [ ] Diagrams do not reconstruct private topology.

## Evidence handling record

- [ ] Access method and access dates recorded.
- [ ] Evidence categories inspected are listed using non-sensitive references.
- [ ] Confidentiality, retention, and deletion obligations recorded.
- [ ] No private evidence was uploaded to an external AI or cloud service
      without explicit authorization.
- [ ] Material automated assistance is disclosed.
- [ ] The final report SHA-256 is recorded outside the report in a signed or
      independently verifiable checksum record.

## Method and limitations

- [ ] Evidence classes are understandable and consistently applied.
- [ ] Non-claims are sufficient for a reasonable reader.
- [ ] Automated checks are not presented as independent judgment.
- [ ] Operational separation is not presented as institutional independence.
- [ ] External certification is not claimed.

## Finding classification

- `MATERIAL`: could change the conclusion or make a public claim misleading.
- `LIMITED`: requires correction or qualification but does not by itself change
  the core conclusion.
- `OBSERVATION`: improvement opportunity without a supported inconsistency.

## Conclusion

Select exactly one using the definitions in
[`docs/06-independent-review.md`](../docs/06-independent-review.md):

- [ ] `CONFIRMED`
- [ ] `CONFIRMED WITH QUALIFICATIONS`
- [ ] `NOT CONFIRMED`

Every qualification and unresolved finding must be listed in the final
statement or its referenced public annex.
