#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Offline verification for the public technical system record."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


REQUIRED_FILES = {
    ".gitattributes",
    ".github/CODEOWNERS",
    ".github/workflows/release-evidence.yml",
    ".github/workflows/verify.yml",
    ".gitignore",
    ".reuse/dep5",
    "CHANGELOG.md",
    "CITATION.cff",
    "LICENSE.md",
    "LICENSES/Apache-2.0.txt",
    "LICENSES/CC-BY-NC-4.0.txt",
    "NOTICE.md",
    "PUBLICATION_CHARTER.md",
    "PUBLICATION_GATE.md",
    "README.md",
    "SECURITY.md",
    "docs/01-system-overview.md",
    "docs/02-implementation-record.md",
    "docs/03-assurance-method.md",
    "docs/04-public-evidence-index.md",
    "docs/05-limitations-and-reassessment.md",
    "docs/06-independent-review.md",
    "docs/07-references.md",
    "evidence/public-claims.json",
    "evidence/publication.json",
    "release/DOI_AND_ARCHIVAL.md",
    "release/RELEASE_NOTES_TEMPLATE.md",
    "release/SIGNING_AND_RELEASE.md",
    "review/ASSURANCE_STATEMENT_TEMPLATE.md",
    "review/REVIEW_BRIEF.md",
    "review/REVIEW_CHECKLIST.md",
    "schemas/public-claims.schema.json",
    "tests/test_verify_publication.py",
    "tools/verify_publication.py",
}

TEXT_SUFFIXES = {".cff", ".json", ".md", ".py", ".txt", ".yaml", ".yml"}
EVIDENCE_CLASSES = {
    "COMMITTED-RECORD",
    "DESIGN-CONTRACT",
    "DIGEST-ANCHORED",
    "BASELINE-GIT-VERIFIED",
    "LIMITATION",
    "OWNER-CONFIRMED",
}
CLAIM_STATUSES = {"QUALIFIED", "SUPPORTED"}
PUBLICATION_STATUSES = {"DRAFT", "READY", "RELEASED", "SUPERSEDED"}
CLAIM_MARKER = re.compile(r"<!--\s*public-claims:\s*([A-Z0-9 -]+?)\s*-->")
PRIVATE_PATH = re.compile(
    r"(?<![A-Za-z0-9])/(?:home|root|srv)/(?:[^\s`'\"<>]+)", re.IGNORECASE
)
GITHUB_REPOSITORY_URL = re.compile(
    r"https://github\.com/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)", re.IGNORECASE
)
CANONICAL_REPOSITORY = "Atanasseri/agentic-engineering-assurance-system"


def _load_private_deny_list(path: Path | None) -> tuple[str, ...]:
    """Load private literals without embedding or echoing them in public code."""
    if path is None:
        return ()
    literals: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        value = line.strip()
        if not value or value.startswith("#"):
            continue
        if len(value) < 4:
            raise ValueError("private deny-list entries must be at least four characters")
        literals.append(value)
    return tuple(dict.fromkeys(literals))


def _iter_text_files(root: Path):
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if ".git" in path.parts or "__pycache__" in path.parts:
            continue
        if path.suffix.lower() in TEXT_SUFFIXES or path.name in {
            ".gitattributes",
            ".gitignore",
            "CODEOWNERS",
        }:
            yield path


def _load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def _relative(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def verify_required_files(root: Path, errors: list[str]) -> None:
    missing = sorted(path for path in REQUIRED_FILES if not (root / path).is_file())
    for path in missing:
        errors.append(f"missing required file: {path}")


def verify_claims(root: Path, errors: list[str]) -> None:
    path = root / "evidence/public-claims.json"
    if not path.is_file():
        return
    try:
        data = _load_json(path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        errors.append(f"invalid public claims JSON: {exc}")
        return

    if data.get("schema_version") != "1.0.0":
        errors.append("public claims schema_version must be 1.0.0")

    commitment = data.get("source_commitment")
    if not isinstance(commitment, dict):
        errors.append("public claims source_commitment must be an object")
        commitment = {}
    digest = commitment.get("manifest_sha256")
    if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
        errors.append("source commitment must contain a lowercase SHA-256 digest")
    if commitment.get("access") != "CONTROLLED_PRIVATE":
        errors.append("source commitment access must be CONTROLLED_PRIVATE")

    claims = data.get("claims")
    if not isinstance(claims, list) or not claims:
        errors.append("public claims must be a non-empty list")
        return

    ids: list[str] = []
    for index, claim in enumerate(claims):
        label = f"claim[{index}]"
        if not isinstance(claim, dict):
            errors.append(f"{label} must be an object")
            continue
        claim_id = claim.get("id")
        if not isinstance(claim_id, str) or not re.fullmatch(r"[A-Z]{3}-[0-9]{3}", claim_id):
            errors.append(f"{label} has an invalid id")
        else:
            ids.append(claim_id)
            label = claim_id
        if not isinstance(claim.get("statement"), str) or not claim["statement"].strip():
            errors.append(f"{label} has no statement")
        if claim.get("evidence_class") not in EVIDENCE_CLASSES:
            errors.append(f"{label} has an invalid evidence_class")
        if claim.get("status") not in CLAIM_STATUSES:
            errors.append(f"{label} has an invalid status")
        sources = claim.get("public_sources")
        if not isinstance(sources, list) or not sources:
            errors.append(f"{label} has no public_sources")
        else:
            if sources != sorted(set(sources)):
                errors.append(f"{label} public_sources must be unique and sorted")
            for source in sources:
                if not isinstance(source, str) or not (root / source).is_file():
                    errors.append(f"{label} references missing public source: {source!r}")
        boundaries = claim.get("does_not_establish")
        if not isinstance(boundaries, list) or not boundaries:
            errors.append(f"{label} must state at least one non-claim")

    if ids != sorted(ids):
        errors.append("public claims must be sorted by id")
    if len(ids) != len(set(ids)):
        errors.append("public claim ids must be unique")

    registered = set(ids)
    markers_by_source: dict[str, set[str]] = {}
    for source_path in sorted({source for claim in claims for source in claim.get("public_sources", [])}):
        if not isinstance(source_path, str) or not (root / source_path).is_file():
            continue
        text = (root / source_path).read_text(encoding="utf-8")
        markers: set[str] = set()
        for match in CLAIM_MARKER.finditer(text):
            marker_ids = match.group(1).split()
            if marker_ids != sorted(set(marker_ids)):
                errors.append(f"public claim marker must be unique and sorted: {source_path}")
            markers.update(marker_ids)
        markers_by_source[source_path] = markers
        for marker_id in sorted(markers - registered):
            errors.append(f"unregistered public claim marker in {source_path}: {marker_id}")

    for claim in claims:
        if not isinstance(claim, dict) or not isinstance(claim.get("id"), str):
            continue
        claim_id = claim["id"]
        for source_path in claim.get("public_sources", []):
            if isinstance(source_path, str) and claim_id not in markers_by_source.get(source_path, set()):
                errors.append(f"{claim_id} is not marked in declared public source: {source_path}")


def verify_publication_record(root: Path, errors: list[str], release: bool = False) -> None:
    path = root / "evidence/publication.json"
    if not path.is_file():
        return
    try:
        data = _load_json(path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        errors.append(f"invalid publication JSON: {exc}")
        return

    if data.get("schema_version") != "1.0.0":
        errors.append("publication schema_version must be 1.0.0")
    if data.get("status") not in PUBLICATION_STATUSES:
        errors.append("publication status is invalid")
    controls = data.get("publication_controls")
    repository_approval = (
        controls.get("repository_publication_approval")
        if isinstance(controls, dict)
        else None
    )
    if data.get("status") in {"READY", "RELEASED"}:
        if not isinstance(repository_approval, dict) or repository_approval.get("status") != "APPROVED":
            errors.append("READY or RELEASED status requires repository publication approval")
    if isinstance(controls, dict) and controls.get("release_approval") not in {"PENDING", "APPROVED"}:
        errors.append("release_approval must be PENDING or APPROVED")
    if release:
        if data.get("status") not in {"READY", "RELEASED"}:
            errors.append("release verification requires publication status READY or RELEASED")
        if not isinstance(controls, dict) or controls.get("release_approval") != "APPROVED":
            errors.append("release verification requires explicit release approval")

    derived = data.get("derived_from")
    if not isinstance(derived, dict):
        errors.append("publication derived_from must be an object")
        return
    digest = derived.get("baseline_manifest_sha256")
    if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
        errors.append("publication baseline commitment must be a lowercase SHA-256 digest")

    claims_path = root / "evidence/public-claims.json"
    if claims_path.is_file():
        try:
            claims = _load_json(claims_path)
            source = claims.get("source_commitment", {})
            if source.get("baseline_id") != derived.get("baseline_id"):
                errors.append("baseline id differs between publication and claims records")
            if source.get("manifest_sha256") != digest:
                errors.append("baseline digest differs between publication and claims records")
        except (OSError, ValueError, json.JSONDecodeError):
            pass


def verify_sensitive_content(
    root: Path,
    errors: list[str],
    private_deny_list: tuple[str, ...] = (),
) -> None:
    full_sha = re.compile(r"(?<![0-9a-f])[0-9a-f]{40}(?![0-9a-f])", re.IGNORECASE)
    internal_id = re.compile(r"\b(?:RV-[0-9]{4}-[0-9]+|WP-[0-9]{2}[A-Z])\b")
    secret_patterns = (
        re.compile(r"-----BEGIN (?:OPENSSH|RSA|EC|DSA) PRIVATE KEY-----"),
        re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
        re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    )
    disallowed_phrase = "case" + " study"

    for path in _iter_text_files(root):
        relative = _relative(root, path)
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            errors.append(f"non-UTF-8 text file: {relative}")
            continue

        lowered = text.casefold()
        for literal in private_deny_list:
            if literal.casefold() in lowered:
                errors.append(f"external private deny-list match in {relative}")
        if disallowed_phrase in lowered:
            errors.append(f"disallowed positioning phrase in {relative}")
        if PRIVATE_PATH.search(text):
            errors.append(f"operational-style absolute path found in {relative}")
        for repository in GITHUB_REPOSITORY_URL.findall(text):
            if repository.casefold() != CANONICAL_REPOSITORY.casefold():
                errors.append(f"non-canonical GitHub repository URL found in {relative}")

        # Workflow actions are intentionally pinned to full upstream SHAs.
        workflow_source = relative.startswith(".github/workflows/")
        if not workflow_source and full_sha.search(text):
            errors.append(f"full private-style Git SHA found in {relative}")
        if internal_id.search(text):
            errors.append(f"private workflow identifier found in {relative}")
        for pattern in secret_patterns:
            if pattern.search(text):
                errors.append(f"possible secret material found in {relative}")


def verify_markdown_links(root: Path, errors: list[str]) -> None:
    link_pattern = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
    for path in _iter_text_files(root):
        if path.suffix.lower() != ".md":
            continue
        text = path.read_text(encoding="utf-8")
        for target in link_pattern.findall(text):
            target = target.strip().split("#", 1)[0]
            if not target or target.startswith(("http://", "https://", "mailto:")):
                continue
            resolved = (path.parent / target).resolve()
            try:
                resolved.relative_to(root.resolve())
            except ValueError:
                errors.append(f"link escapes repository in {_relative(root, path)}: {target}")
                continue
            if not resolved.exists():
                errors.append(f"broken local link in {_relative(root, path)}: {target}")


def verify_citation(root: Path, errors: list[str]) -> None:
    path = root / "CITATION.cff"
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8")
    required = (
        "cff-version: 1.2.0",
        'title: "Agentic Engineering Assurance System"',
        "family-names: Nasseri",
        "given-names: Ata",
        "affiliation: Solofounders",
        "license: CC-BY-NC-4.0",
    )
    for value in required:
        if value not in text:
            errors.append(f"CITATION.cff missing required value: {value}")
    if "  - Apache-2.0" in text:
        errors.append(
            "CITATION.cff must not advertise Apache-2.0 as an alternative "
            "license for the complete cited record"
        )


def verify(
    root: Path,
    release: bool = False,
    private_deny_list: Path | None = None,
) -> list[str]:
    root = root.resolve()
    errors: list[str] = []
    verify_required_files(root, errors)
    verify_claims(root, errors)
    verify_publication_record(root, errors, release=release)
    try:
        private_literals = _load_private_deny_list(private_deny_list)
    except (OSError, ValueError) as exc:
        errors.append(f"invalid external private deny-list: {exc}")
        private_literals = ()
    verify_sensitive_content(root, errors, private_literals)
    verify_markdown_links(root, errors)
    verify_citation(root, errors)
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".", type=Path)
    parser.add_argument(
        "--release",
        action="store_true",
        help="require a separately owner-approved release publication record",
    )
    parser.add_argument(
        "--private-deny-list",
        type=Path,
        help="optional uncommitted newline-delimited private literals for publisher preflight",
    )
    args = parser.parse_args()
    errors = verify(
        args.root,
        release=args.release,
        private_deny_list=args.private_deny_list,
    )
    if errors:
        print("PUBLICATION VERIFICATION: FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    print("PUBLICATION VERIFICATION: PASSED")
    print("- required structure present")
    print("- public claim register and source markers consistent")
    print("- private locator and secret scan passed")
    print("- local Markdown links resolved")
    print("- citation metadata present")
    return 0


if __name__ == "__main__":
    sys.exit(main())
