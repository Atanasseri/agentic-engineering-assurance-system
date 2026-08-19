# DOI and Archival Guide

## Purpose

A DOI gives the public system record a persistent, citable identity. It improves
discovery and archival durability; it is not certification.

## Recommended process

1. Create or sign in to a Zenodo account owned by Ata Nasseri.
2. Link the GitHub account used for the public repository.
3. Link an ORCID identity if available.
4. Validate `CITATION.cff` before release.
5. Enable the public repository in Zenodo before creating the GitHub release.
6. Publish the immutable signed GitHub release.
7. Wait for Zenodo to ingest and archive the release.
8. Verify the title, author, affiliation, version, license, and release date.
9. Confirm that the DOI resolves to the exact archived version.
10. Add the version DOI to the public record in a documented successor commit.

## Version and concept DOI

Use the version DOI when identifying the object reviewed by an independent
assessor. A concept DOI may be used in general professional material when the
intent is to point to the project across versions.

## Metadata quality

Before confirming the Zenodo record, verify:

- title: `Agentic Engineering Assurance System`;
- creator: `Ata Nasseri`;
- affiliation: `Solofounders`;
- type: software or technical system record, as supported by the service;
- version: exact GitHub release version;
- license: consistent with the repository split-license notice;
- keywords: agentic engineering, AI governance, software assurance,
  auditability, and release integrity; and
- description: bounded, evidence-backed, and explicitly not certification.

## Archival boundary

Archive only the public release. Do not connect Zenodo, Software Heritage, or
another public preservation service to the private evidence or operational
repositories.

