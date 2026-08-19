# Signing and Release Guide

## Objective

Publish one exact, attributable, immutable public record. The release commit,
annotated tag, bundle, checksums, provenance attestation, and DOI must all refer
to the same content.

## 1. Configure signing

Use a dedicated SSH or GPG signing key controlled by the repository owner. Do
not store the private key in this repository, GitHub Actions, chat, or the
private evidence archive.

For SSH signing, the maintainer configures Git to use SSH signatures, uploads
the public key to GitHub as a **signing key**, and enables automatic commit and
tag signing. Confirm the setup on a disposable test repository before making
signature enforcement mandatory.

## 2. Freeze the candidate

1. Complete every content and disclosure check.
2. Record the owner's separate Release approval in `evidence/publication.json`.
3. Update `CHANGELOG.md` and `CITATION.cff`.
4. Run the local verifier and unit tests.
5. Review the rendered Markdown and diagrams.
6. Confirm that the explicit owner Release approval remains current.

## 3. Create the signed Git objects

Create a signed release commit and a signed annotated tag. The initial public
release tag is:

```text
v1.0.0
```

Verify that GitHub displays `Verified` for both the commit and tag before
continuing.

## 4. Generate release assets

The tag workflow creates:

```text
agentic-engineering-assurance-system-v1.0.0.tar.gz
SHA256SUMS
```

GitHub Actions then creates provenance attestations for those files. Download
the workflow artifact and verify the checksum before attaching it to the
release.

## 5. Publish immutably

1. Enable immutable releases before publication.
2. Push the signed tag.
3. Wait for the release workflow to pass.
4. Create a draft release for the existing signed tag.
5. Attach the bundle and `SHA256SUMS`.
6. Add the approved release notes.
7. Confirm that every asset is present.
8. Publish the release.
9. Verify that GitHub displays the release as immutable.

Never publish first and add evidence later. Immutability should close the
release only after the complete asset set is attached.

## 6. Verify the result

Record:

- full commit SHA;
- signed tag verification;
- immutable release verification;
- asset SHA-256 verification;
- artifact-attestation verification; and
- release URL.

The DOI and independent-review statement are added only after their own
verification succeeds.
