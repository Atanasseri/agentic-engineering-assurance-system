# Publication Gate

> **Repository decision:** AUTHORIZED FOR PUBLIC REPOSITORY DEPLOYMENT
>
> **Release decision:** APPROVED FOR PUBLICATION OF `v1.0.0`
> **Release authority:** Ata Nasseri, Assurance Owner
> **Approval date:** 2026-08-19
>
> Repository deployment and Release publication were authorized as separate
> owner-controlled actions. Release publication remains subject to the technical
> conditions below; outcome checks remain pending until they are observed.

## A. Repository-deployment authorization

- [x] Public content was written from an allow-list, not copied from private Git history.
- [x] Private repository names and URLs are absent.
- [x] Operational paths, accounts, hosts, sessions, processes, and authority tokens are absent.
- [x] Raw audit, decision, handoff, resolution, and conversation records are absent.
- [x] Material public claims retain evidence qualifications and non-claims.
- [x] Owner has reviewed the complete rendered repository.
- [x] Owner has approved the public use of name and affiliation.
- [x] Owner has approved the split license.

## B. Local deployment verification

- [x] `python tools/verify_publication.py .` passes on the final candidate.
- [x] `python -m unittest discover -s tests -v` passes on the final candidate.
- [x] The private, uncommitted deny-list preflight passes.
- [x] A final metadata and secret scan passes on the complete Git history.

## C. Remote controls required before Release publication

- [ ] GitHub Actions passes on the exact release commit.
- [x] The public repository has a protected `main` branch.
- [x] Force-push and branch deletion are blocked.
- [x] The `verify` status check is required.
- [x] Release-tag updates and deletion are blocked.
- [x] Immutable releases are enabled before the first release is published.
- [x] GitHub private vulnerability reporting is enabled.
- [x] GitHub verified the owner's dedicated SSH signing identity.

## D. Release authorization and identity

- [x] Owner has explicitly approved publication of Release `v1.0.0`.
- [ ] The release commit has a GitHub `Verified` signature.
- [ ] The annotated release tag has a GitHub `Verified` signature.
- [ ] Release assets and SHA-256 checksums are complete.
- [ ] GitHub artifact provenance is generated for the release bundle.

## E. Post-release validation and archival

- [ ] The immutable release is verified after publication.
- [ ] `CITATION.cff` validates and matches the released version.
- [x] Zenodo integration is enabled before the release event.
- [ ] A version DOI is issued and recorded.

## F. Independent-review follow-up

- [ ] Independent review scope and reviewer are approved.
- [ ] The final public assurance statement references the exact commit, tag, release, and DOI.

## Gate authority

Only Ata Nasseri, as Assurance Owner, may authorize repository deployment or
Release publication. Automation may report control status; it cannot issue
either authority. The repository approval and Release approval remain separate
authorities. The Release approval recorded here applies only to `v1.0.0` and
does not establish completion of any unchecked technical, archival, or
independent-review outcome.
