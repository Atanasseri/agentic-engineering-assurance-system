#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Offline verification for the public technical system record."""

from __future__ import annotations

import argparse
import html
import json
import re
import struct
import sys
import xml.etree.ElementTree as ET
import zlib
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
    "assets/VISUAL_SYSTEM.md",
    "assets/visuals/manifest.json",
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
    "schemas/visual-manifest.schema.json",
    "tests/test_verify_publication.py",
    "tools/verify_publication.py",
}

TEXT_SUFFIXES = {".cff", ".json", ".md", ".py", ".svg", ".txt", ".yaml", ".yml"}
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
VISUAL_APPROVAL_STATUSES = {"DRAFT", "OWNER_APPROVED", "SUPERSEDED"}
INDEPENDENT_REVIEW_STATUSES = {"COMPLETED", "IN_PROGRESS", "NOT_PERFORMED"}
SVG_NAMESPACE = "http://www.w3.org/2000/svg"
STRUCTURED_CLAIM_SOURCES = {
    "evidence/publication.json": {"ARC-001", "REL-003", "REV-001"},
}
PNG_ALLOWED_CHUNKS = {
    b"IDAT",
    b"IEND",
    b"IHDR",
    b"PLTE",
    b"bKGD",
    b"cHRM",
    b"gAMA",
    b"pHYs",
    b"sBIT",
    b"sRGB",
    b"tRNS",
}
VISUAL_MANIFEST_KEYS = {
    "independent_review_status",
    "record_id",
    "record_scope",
    "release_boundary",
    "schema_version",
    "visuals",
}
VISUAL_ITEM_KEYS = {
    "approval_status",
    "claim_ids",
    "description",
    "does_not_establish",
    "file",
    "height",
    "id",
    "public_sources",
    "title",
    "view_box",
    "width",
}
CLAIM_MARKER = re.compile(r"<!--\s*public-claims:\s*([A-Z0-9 -]+?)\s*-->")
MARKDOWN_IMAGE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
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
    sources_by_claim: dict[str, list[str]] = {}
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
        evidence_class = claim.get("evidence_class")
        if not isinstance(evidence_class, str) or evidence_class not in EVIDENCE_CLASSES:
            errors.append(f"{label} has an invalid evidence_class")
        claim_status = claim.get("status")
        if not isinstance(claim_status, str) or claim_status not in CLAIM_STATUSES:
            errors.append(f"{label} has an invalid status")
        sources = claim.get("public_sources")
        if not isinstance(sources, list) or not sources:
            errors.append(f"{label} has no public_sources")
            sources = []
        elif any(not isinstance(source, str) or not source for source in sources):
            errors.append(f"{label} public_sources must contain only non-empty strings")
            sources = [source for source in sources if isinstance(source, str) and source]
        else:
            if sources != sorted(set(sources)):
                errors.append(f"{label} public_sources must be unique and sorted")
        for source in sources:
            if _repository_file(root, source) is None:
                errors.append(f"{label} references missing public source: {source!r}")
        if isinstance(claim_id, str):
            sources_by_claim[claim_id] = sources
        boundaries = claim.get("does_not_establish")
        if not isinstance(boundaries, list) or not boundaries or any(
            not isinstance(boundary, str) or not boundary.strip() for boundary in boundaries
        ):
            errors.append(f"{label} must state at least one non-claim")

    if ids != sorted(ids):
        errors.append("public claims must be sorted by id")
    if len(ids) != len(set(ids)):
        errors.append("public claim ids must be unique")

    registered = set(ids)
    markers_by_source: dict[str, set[str]] = {}
    for source_path in sorted(
        {source for claim_sources in sources_by_claim.values() for source in claim_sources}
    ):
        if _repository_file(root, source_path) is None:
            continue
        markers = set(STRUCTURED_CLAIM_SOURCES.get(source_path, set()))
        if source_path not in STRUCTURED_CLAIM_SOURCES:
            text = (root / source_path).read_text(encoding="utf-8")
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
        for source_path in sources_by_claim.get(claim_id, []):
            if claim_id not in markers_by_source.get(source_path, set()):
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
    publication_status = data.get("status")
    if not isinstance(publication_status, str) or publication_status not in PUBLICATION_STATUSES:
        errors.append("publication status is invalid")
    independent_review = data.get("independent_review")
    if not isinstance(independent_review, dict):
        errors.append("publication independent_review must be an object")
    else:
        review_status = independent_review.get("status")
        if review_status not in INDEPENDENT_REVIEW_STATUSES:
            errors.append("publication independent review status is invalid")
        if review_status == "NOT_PERFORMED" and any(
            independent_review.get(key) is not None
            for key in ("public_statement", "reviewed_release")
        ):
            errors.append(
                "NOT_PERFORMED independent review must not identify a review or statement"
            )
        expected_reviewed_release = f"v{data.get('version')}"
        if review_status == "IN_PROGRESS":
            if independent_review.get("reviewed_release") != expected_reviewed_release:
                errors.append(
                    "IN_PROGRESS independent review must identify the version-bound release"
                )
            if independent_review.get("public_statement") is not None:
                errors.append(
                    "IN_PROGRESS independent review must not identify a final public statement"
                )
        if review_status == "COMPLETED":
            if independent_review.get("reviewed_release") != expected_reviewed_release:
                errors.append(
                    "COMPLETED independent review must identify the version-bound release"
                )
            public_statement = independent_review.get("public_statement")
            if not isinstance(public_statement, str) or not re.fullmatch(
                r"https://[^\s]+", public_statement
            ):
                errors.append(
                    "COMPLETED independent review requires a stable HTTPS public statement"
                )
        if review_status in {"IN_PROGRESS", "COMPLETED"}:
            claims_path = root / "evidence/public-claims.json"
            if claims_path.is_file():
                try:
                    claims_data = _load_json(claims_path)
                except (OSError, ValueError, json.JSONDecodeError):
                    claims_data = {}
                claims = claims_data.get("claims", [])
                if isinstance(claims, list) and any(
                    isinstance(claim, dict) and claim.get("id") == "REV-001"
                    for claim in claims
                ):
                    errors.append(
                        "active or completed independent review requires retiring "
                        "the REV-001 NOT_PERFORMED claim"
                    )
    controls = data.get("publication_controls")
    repository_approval = (
        controls.get("repository_publication_approval")
        if isinstance(controls, dict)
        else None
    )
    if isinstance(publication_status, str) and publication_status in {"READY", "RELEASED"}:
        if not isinstance(repository_approval, dict) or repository_approval.get("status") != "APPROVED":
            errors.append("READY or RELEASED status requires repository publication approval")
    if isinstance(controls, dict):
        release_approval = controls.get("release_approval")
        if not isinstance(release_approval, str) or release_approval not in {
            "APPROVED",
            "PENDING",
        }:
            errors.append("release_approval must be PENDING or APPROVED")
    observed_release = (
        controls.get("observed_release") if isinstance(controls, dict) else None
    )
    if publication_status == "RELEASED":
        release_requirements = (
            controls.get("release_requirements") if isinstance(controls, dict) else None
        )
        required_release_controls = {
            "artifact_attestation",
            "immutable_release",
            "signed_annotated_tag",
            "signed_commit",
        }
        if not isinstance(release_requirements, dict) or any(
            release_requirements.get(key) is not True
            for key in required_release_controls
        ):
            errors.append("RELEASED status requires all recorded release controls")
        commit_sha = (
            observed_release.get("commit_sha")
            if isinstance(observed_release, dict)
            else None
        )
        if not isinstance(commit_sha, str) or not re.fullmatch(r"[0-9a-f]{40}", commit_sha):
            errors.append("RELEASED status requires a lowercase observed release commit SHA")
        version = data.get("version")
        expected_tag = f"v{version}"
        expected_release_url = (
            "https://github.com/Atanasseri/agentic-engineering-assurance-system/"
            f"releases/tag/{expected_tag}"
        )
        required_observations = {
            "tag": expected_tag,
            "release_url": expected_release_url,
            "immutable": True,
        }
        if not isinstance(observed_release, dict):
            errors.append("RELEASED status requires observed release metadata")
            observed_release = {}
        for key, expected in required_observations.items():
            if observed_release.get(key) != expected:
                errors.append(f"observed release {key} does not match the released version")
        if not re.fullmatch(
            r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z",
            str(observed_release.get("published_at", "")),
        ):
            errors.append("observed release published_at must be a UTC timestamp")
        if not re.fullmatch(
            r"https://github\.com/Atanasseri/agentic-engineering-assurance-system/actions/runs/[0-9]+",
            str(observed_release.get("evidence_run_url", "")),
        ):
            errors.append("observed release evidence_run_url is invalid")
        for key in ("bundle_sha256", "manifest_sha256"):
            if not re.fullmatch(r"[0-9a-f]{64}", str(observed_release.get(key, ""))):
                errors.append(f"observed release {key} must be a lowercase SHA-256 digest")
        doi = observed_release.get("doi")
        concept_doi = observed_release.get("concept_doi")
        if not isinstance(doi, str) or not re.fullmatch(r"10\.5281/zenodo\.[0-9]+", doi):
            errors.append("observed release DOI is invalid")
        if not isinstance(concept_doi, str) or not re.fullmatch(
            r"10\.5281/zenodo\.[0-9]+", concept_doi
        ):
            errors.append("observed release concept DOI is invalid")
        if doi == concept_doi:
            errors.append("version DOI and concept DOI must be distinct")
        record_id = doi.rsplit(".", 1)[-1] if isinstance(doi, str) else ""
        expected_zenodo_url = f"https://zenodo.org/records/{record_id}"
        if observed_release.get("zenodo_record_url") != expected_zenodo_url:
            errors.append("observed Zenodo record URL does not match the version DOI")
        if not isinstance(controls, dict) or controls.get("release_approval") != "APPROVED":
            errors.append("RELEASED status requires explicit release approval")
    if release:
        if not isinstance(publication_status, str) or publication_status not in {
            "READY",
            "RELEASED",
        }:
            errors.append("release verification requires publication status READY or RELEASED")
        if not isinstance(controls, dict) or controls.get("release_approval") != "APPROVED":
            errors.append("release verification requires explicit release approval")
        approval_record = (
            controls.get("release_approval_record")
            if isinstance(controls, dict)
            else None
        )
        expected_release = f"v{data.get('version')}"
        if (
            not isinstance(approval_record, dict)
            or approval_record.get("release") != expected_release
        ):
            errors.append(
                "release verification requires a version-bound Release approval record"
            )
        elif (
            not isinstance(approval_record.get("approved_by"), str)
            or not approval_record["approved_by"].strip()
            or not isinstance(approval_record.get("approved_on"), str)
            or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", approval_record["approved_on"])
            or not isinstance(approval_record.get("statement"), str)
            or not approval_record["statement"].strip()
        ):
            errors.append("Release approval record is incomplete")

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


def _xml_local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _positive_integer(value: object) -> int | None:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        return None
    return value


def _string_set(value: object) -> set[str] | None:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        return None
    return set(value)


def _repository_file(root: Path, relative: object) -> Path | None:
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute():
        return None
    path = (root / relative).resolve()
    try:
        path.relative_to(root.resolve())
    except ValueError:
        return None
    return path if path.is_file() else None


def _verify_svg(
    path: Path,
    relative: str,
    visual: dict,
    errors: list[str],
) -> None:
    if path.stat().st_size > 250_000:
        errors.append(f"SVG exceeds 250 KB visual limit: {relative}")
        return
    try:
        source = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        errors.append(f"unreadable SVG visual {relative}: {exc}")
        return
    if re.search(r"<!\s*(?:DOCTYPE|ENTITY)\b", source, flags=re.IGNORECASE):
        errors.append(f"SVG visual must not contain a DTD or entity declaration: {relative}")
        return
    if "<?" in source:
        errors.append(f"SVG visual must not contain processing instructions: {relative}")
        return
    try:
        svg = ET.fromstring(source)
    except ET.ParseError as exc:
        errors.append(f"invalid SVG visual {relative}: {exc}")
        return
    if svg.tag != f"{{{SVG_NAMESPACE}}}svg":
        errors.append(f"visual must use the canonical SVG namespace: {relative}")
        return

    width_text = svg.get("width", "")
    height_text = svg.get("height", "")
    if not re.fullmatch(r"[1-9][0-9]*", width_text):
        errors.append(f"SVG width must be a positive unitless integer: {relative}")
    elif int(width_text) != visual.get("width"):
        errors.append(f"SVG width differs from visual manifest: {relative}")
    if not re.fullmatch(r"[1-9][0-9]*", height_text):
        errors.append(f"SVG height must be a positive unitless integer: {relative}")
    elif int(height_text) != visual.get("height"):
        errors.append(f"SVG height differs from visual manifest: {relative}")
    expected_view_box = None
    if isinstance(visual.get("width"), int) and isinstance(visual.get("height"), int):
        expected_view_box = f"0 0 {visual['width']} {visual['height']}"
    if svg.get("viewBox") != visual.get("view_box"):
        errors.append(f"SVG viewBox differs from visual manifest: {relative}")
    if expected_view_box is not None and svg.get("viewBox") != expected_view_box:
        errors.append(f"SVG viewBox must match its intrinsic dimensions: {relative}")
    if svg.get("role") != "img":
        errors.append(f"SVG visual must declare role=img: {relative}")

    children = list(svg)
    if len(children) < 2 or [_xml_local_name(item.tag) for item in children[:2]] != [
        "title",
        "desc",
    ]:
        errors.append(f"SVG visual must begin with title and desc: {relative}")
    else:
        title, description = children[:2]
        title_text = "".join(title.itertext()).strip()
        description_text = "".join(description.itertext()).strip()
        if not title_text or not description_text:
            errors.append(f"SVG title and desc must be non-empty: {relative}")
        if title_text != visual.get("title"):
            errors.append(f"SVG title differs from visual manifest: {relative}")
        if description_text != visual.get("description"):
            errors.append(f"SVG desc differs from visual manifest: {relative}")
        expected_ids = [title.get("id"), description.get("id")]
        labelled_by = svg.get("aria-labelledby", "").split()
        if any(not value for value in expected_ids) or labelled_by != expected_ids:
            errors.append(f"SVG aria-labelledby must resolve title and desc: {relative}")

    prohibited_elements = {
        "animate",
        "animateMotion",
        "animateTransform",
        "foreignObject",
        "image",
        "script",
        "set",
    }
    elements = list(svg.iter())
    ids: set[str] = set()
    duplicate_ids: set[str] = set()
    for element in elements:
        element_id = element.get("id")
        if element_id:
            if element_id in ids:
                duplicate_ids.add(element_id)
            ids.add(element_id)
    if duplicate_ids:
        errors.append(f"SVG visual ids must be unique: {relative}")

    fragment_references: set[str] = set()
    css_animation = re.compile(
        r"@keyframes\b|\banimation(?:-[a-z-]+)?\s*:|\btransition(?:-[a-z-]+)?\s*:",
        flags=re.IGNORECASE,
    )
    for element in elements:
        if not isinstance(element.tag, str):
            errors.append(f"SVG visual contains a non-SVG element namespace: {relative}")
            continue
        if not element.tag.startswith(f"{{{SVG_NAMESPACE}}}"):
            errors.append(f"SVG visual contains a non-SVG element namespace: {relative}")
        name = _xml_local_name(element.tag)
        if name in prohibited_elements:
            errors.append(f"SVG visual contains prohibited element {name}: {relative}")
        for attribute, value in element.attrib.items():
            attribute_name = _xml_local_name(attribute).lower()
            if attribute_name.startswith("on"):
                errors.append(
                    f"SVG visual contains event-handler attribute {attribute_name}: {relative}"
                )
            if attribute == "{http://www.w3.org/XML/1998/namespace}base" or attribute_name == "base":
                errors.append(f"SVG visual must not declare xml:base: {relative}")
            if attribute_name == "href":
                if not value.startswith("#"):
                    errors.append(f"SVG visual contains external reference: {relative}")
                else:
                    fragment_references.add(value[1:])
            for match in re.findall(r"url\(([^)]+)\)", value, flags=re.IGNORECASE):
                reference = match.strip().strip("\"'")
                if not reference.startswith("#"):
                    errors.append(f"SVG visual contains external URL reference: {relative}")
                else:
                    fragment_references.add(reference[1:])
            if attribute_name == "style" and css_animation.search(value):
                errors.append(f"SVG visual contains CSS animation or transition: {relative}")
        if name == "style":
            style_text = "".join(element.itertext())
            if re.search(r"@import\b", style_text, flags=re.IGNORECASE):
                errors.append(f"SVG visual contains a stylesheet import: {relative}")
            if css_animation.search(style_text):
                errors.append(f"SVG visual contains CSS animation or transition: {relative}")
            for match in re.findall(r"url\(([^)]+)\)", style_text, flags=re.IGNORECASE):
                reference = match.strip().strip("\"'")
                if not reference.startswith("#"):
                    errors.append(f"SVG visual contains external URL reference: {relative}")
                else:
                    fragment_references.add(reference[1:])
    if "" in fragment_references or not fragment_references.issubset(ids):
        errors.append(f"SVG visual contains an unresolved fragment reference: {relative}")


def _verify_png(
    path: Path,
    relative: str,
    visual: dict,
    errors: list[str],
) -> None:
    if path.stat().st_size > 5_000_000:
        errors.append(f"PNG exceeds 5 MB visual limit: {relative}")
        return
    try:
        data = path.read_bytes()
    except OSError as exc:
        errors.append(f"unreadable PNG visual {relative}: {exc}")
        return
    if len(data) < 33 or data[:8] != b"\x89PNG\r\n\x1a\n":
        errors.append(f"invalid PNG signature: {relative}")
        return

    position = 8
    chunk_index = 0
    ihdr: bytes | None = None
    idat_count = 0
    iend_count = 0
    while position < len(data):
        if position + 12 > len(data):
            errors.append(f"truncated PNG chunk: {relative}")
            return
        length = struct.unpack(">I", data[position : position + 4])[0]
        chunk_type = data[position + 4 : position + 8]
        chunk_end = position + 12 + length
        if chunk_end > len(data):
            errors.append(f"PNG chunk exceeds file bounds: {relative}")
            return
        chunk_data = data[position + 8 : position + 8 + length]
        expected_crc = struct.unpack(">I", data[position + 8 + length : chunk_end])[0]
        actual_crc = zlib.crc32(chunk_type)
        actual_crc = zlib.crc32(chunk_data, actual_crc) & 0xFFFFFFFF
        if actual_crc != expected_crc:
            errors.append(f"PNG chunk CRC mismatch: {relative}")
        if not re.fullmatch(rb"[A-Za-z]{4}", chunk_type):
            errors.append(f"PNG chunk type is invalid: {relative}")
        if chunk_type not in PNG_ALLOWED_CHUNKS:
            errors.append(f"PNG contains unsupported metadata or chunk type: {relative}")
        if chunk_index == 0 and (chunk_type != b"IHDR" or length != 13):
            errors.append(f"PNG must begin with a 13-byte IHDR chunk: {relative}")
        if chunk_type == b"IHDR":
            if ihdr is not None or length != 13:
                errors.append(f"PNG must contain exactly one valid IHDR chunk: {relative}")
            else:
                ihdr = chunk_data
        elif chunk_type == b"IDAT":
            idat_count += 1
        elif chunk_type == b"IEND":
            iend_count += 1
            if length != 0:
                errors.append(f"PNG IEND chunk must be empty: {relative}")
            if chunk_end != len(data):
                errors.append(f"PNG must end exactly at its IEND chunk: {relative}")
                return
        position = chunk_end
        chunk_index += 1

    if ihdr is None or idat_count == 0 or iend_count != 1:
        errors.append(f"PNG must contain IHDR, IDAT, and exactly one IEND: {relative}")
        return
    width, height, bit_depth, color_type, compression, filtering, interlace = struct.unpack(
        ">IIBBBBB", ihdr
    )
    valid_depths = {
        0: {1, 2, 4, 8, 16},
        2: {8, 16},
        3: {1, 2, 4, 8},
        4: {8, 16},
        6: {8, 16},
    }
    if (
        color_type not in valid_depths
        or bit_depth not in valid_depths[color_type]
        or compression != 0
        or filtering != 0
        or interlace not in {0, 1}
    ):
        errors.append(f"PNG IHDR contains unsupported values: {relative}")
    if width != visual.get("width") or height != visual.get("height"):
        errors.append(f"PNG dimensions differ from visual manifest: {relative}")
    if visual.get("view_box") is not None:
        errors.append(f"PNG visual view_box must be null: {relative}")


def verify_visual_schema(root: Path, errors: list[str]) -> None:
    path = root / "schemas/visual-manifest.schema.json"
    if not path.is_file():
        return
    try:
        schema = _load_json(path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        errors.append(f"invalid visual manifest schema JSON: {exc}")
        return
    properties = schema.get("properties")
    if (
        schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema"
        or schema.get("type") != "object"
        or schema.get("additionalProperties") is not False
        or _string_set(schema.get("required")) != VISUAL_MANIFEST_KEYS
        or not isinstance(properties, dict)
        or set(properties) != VISUAL_MANIFEST_KEYS
    ):
        errors.append("visual manifest schema root contract is inconsistent")
        return
    version_schema = properties.get("schema_version")
    version_schema = version_schema if isinstance(version_schema, dict) else {}
    if version_schema.get("const") != "1.0.0":
        errors.append("visual manifest schema version contract is inconsistent")
    scope_schema = properties.get("record_scope")
    scope_schema = scope_schema if isinstance(scope_schema, dict) else {}
    if (
        scope_schema.get("const")
        != "POST_RELEASE_DOCUMENTATION_REFINEMENT"
    ):
        errors.append("visual manifest schema scope contract is inconsistent")
    review_schema = properties.get("independent_review_status")
    review_schema = review_schema if isinstance(review_schema, dict) else {}
    if _string_set(review_schema.get("enum")) != (
        INDEPENDENT_REVIEW_STATUSES
    ):
        errors.append("visual manifest schema review-status contract is inconsistent")
    visuals_schema = properties.get("visuals")
    visuals_schema = visuals_schema if isinstance(visuals_schema, dict) else {}
    item_schema = visuals_schema.get("items")
    item_schema = item_schema if isinstance(item_schema, dict) else {}
    item_properties = item_schema.get("properties")
    if (
        visuals_schema.get("type") != "array"
        or visuals_schema.get("minItems") != 1
        or item_schema.get("type") != "object"
        or item_schema.get("additionalProperties") is not False
        or _string_set(item_schema.get("required")) != VISUAL_ITEM_KEYS
        or not isinstance(item_properties, dict)
        or set(item_properties) != VISUAL_ITEM_KEYS
    ):
        errors.append("visual manifest schema item contract is inconsistent")
        return
    approval_schema = item_properties.get("approval_status")
    approval_schema = approval_schema if isinstance(approval_schema, dict) else {}
    if _string_set(approval_schema.get("enum")) != (
        VISUAL_APPROVAL_STATUSES
    ):
        errors.append("visual manifest schema approval-status contract is inconsistent")


def verify_visual_manifest(root: Path, errors: list[str]) -> None:
    manifest_path = root / "assets/visuals/manifest.json"
    claims_path = root / "evidence/public-claims.json"
    publication_path = root / "evidence/publication.json"
    if not manifest_path.is_file() or not claims_path.is_file():
        return
    verify_visual_schema(root, errors)
    try:
        manifest = _load_json(manifest_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        errors.append(f"invalid visual manifest JSON: {exc}")
        return
    try:
        claims_data = _load_json(claims_path)
    except (OSError, ValueError, json.JSONDecodeError):
        return

    missing_manifest_keys = sorted(VISUAL_MANIFEST_KEYS - set(manifest))
    extra_manifest_keys = sorted(set(manifest) - VISUAL_MANIFEST_KEYS)
    for key in missing_manifest_keys:
        errors.append(f"visual manifest is missing required field: {key}")
    for key in extra_manifest_keys:
        errors.append(f"visual manifest contains unsupported field: {key}")
    if manifest.get("schema_version") != "1.0.0":
        errors.append("visual manifest schema_version must be 1.0.0")
    if not isinstance(manifest.get("record_id"), str) or not manifest["record_id"].strip():
        errors.append("visual manifest record_id must be a non-empty string")
    if manifest.get("record_scope") != "POST_RELEASE_DOCUMENTATION_REFINEMENT":
        errors.append("visual manifest record_scope is invalid")
    if not isinstance(manifest.get("release_boundary"), str) or not manifest[
        "release_boundary"
    ].strip():
        errors.append("visual manifest must state its release boundary")
    manifest_review_status = manifest.get("independent_review_status")
    if (
        not isinstance(manifest_review_status, str)
        or manifest_review_status not in INDEPENDENT_REVIEW_STATUSES
    ):
        errors.append("visual manifest independent_review_status is invalid")

    if publication_path.is_file():
        try:
            publication = _load_json(publication_path)
        except (OSError, ValueError, json.JSONDecodeError):
            publication = {}
        independent_review = publication.get("independent_review", {})
        expected_status = (
            independent_review.get("status")
            if isinstance(independent_review, dict)
            else None
        )
        if manifest_review_status != expected_status:
            errors.append(
                "visual manifest independent_review_status differs from publication record"
            )

    claims = claims_data.get("claims", [])
    if not isinstance(claims, list):
        claims = []
    claim_map = {
        claim.get("id"): claim
        for claim in claims
        if isinstance(claim, dict) and isinstance(claim.get("id"), str)
    }
    claim_source_map: dict[str, set[str]] = {}
    for claim_id, claim in claim_map.items():
        raw_sources = claim.get("public_sources")
        claim_source_map[claim_id] = (
            {
                source
                for source in raw_sources
                if isinstance(source, str) and source
            }
            if isinstance(raw_sources, list)
            else set()
        )
    visuals = manifest.get("visuals")
    if not isinstance(visuals, list) or not visuals:
        errors.append("visual manifest visuals must be a non-empty list")
        return

    visual_ids: list[str] = []
    registered_files: list[str] = []
    for index, visual in enumerate(visuals):
        label = f"visual[{index}]"
        if not isinstance(visual, dict):
            errors.append(f"{label} must be an object")
            continue
        missing_visual_keys = sorted(VISUAL_ITEM_KEYS - set(visual))
        extra_visual_keys = sorted(set(visual) - VISUAL_ITEM_KEYS)
        for key in missing_visual_keys:
            errors.append(f"{label} is missing required field: {key}")
        for key in extra_visual_keys:
            errors.append(f"{label} contains unsupported field: {key}")
        visual_id = visual.get("id")
        if not isinstance(visual_id, str) or not re.fullmatch(
            r"[a-z0-9]+(?:-[a-z0-9]+)*", visual_id
        ):
            errors.append(f"{label} has an invalid id")
        else:
            visual_ids.append(visual_id)
            label = visual_id
        relative = visual.get("file")
        if not isinstance(relative, str) or not re.fullmatch(
            r"assets/visuals/[a-z0-9-]+\.(?:svg|png)", relative
        ):
            errors.append(f"{label} has an invalid visual file path")
            continue
        registered_files.append(relative)
        path = (root / relative).resolve()
        try:
            path.relative_to((root / "assets/visuals").resolve())
        except ValueError:
            errors.append(f"{label} visual file escapes assets/visuals")
            continue
        if not path.is_file():
            errors.append(f"{label} references missing visual file: {relative}")
            continue

        for key in ("title", "description"):
            if not isinstance(visual.get(key), str) or not visual[key].strip():
                errors.append(f"{label} has no {key}")
        width = _positive_integer(visual.get("width"))
        height = _positive_integer(visual.get("height"))
        if width is None or height is None:
            errors.append(f"{label} width and height must be positive integers")
        view_box = visual.get("view_box")
        if view_box is not None and (
            not isinstance(view_box, str)
            or not re.fullmatch(r"0 0 [1-9][0-9]* [1-9][0-9]*", view_box)
        ):
            errors.append(f"{label} has an invalid view_box")

        claim_ids = visual.get("claim_ids")
        if not isinstance(claim_ids, list) or not claim_ids:
            errors.append(f"{label} must declare at least one claim_id")
            claim_ids = []
        elif any(
            not isinstance(claim_id, str)
            or not re.fullmatch(r"[A-Z]{3}-[0-9]{3}", claim_id)
            for claim_id in claim_ids
        ):
            errors.append(f"{label} claim_ids must contain only valid strings")
            claim_ids = [claim_id for claim_id in claim_ids if isinstance(claim_id, str)]
        elif claim_ids != sorted(set(claim_ids)):
            errors.append(f"{label} claim_ids must be unique and sorted")
        sources = visual.get("public_sources")
        if not isinstance(sources, list) or not sources:
            errors.append(f"{label} must declare at least one public source")
            sources = []
        elif any(not isinstance(source, str) or not source for source in sources):
            errors.append(f"{label} public_sources must contain only non-empty strings")
            sources = [source for source in sources if isinstance(source, str) and source]
        elif sources != sorted(set(sources)):
            errors.append(f"{label} public_sources must be unique and sorted")
        valid_sources = {
            source for source in sources if _repository_file(root, source) is not None
        }
        for source in sources:
            if _repository_file(root, source) is None:
                errors.append(f"{label} references missing public source: {source!r}")
        for claim_id in claim_ids:
            claim = claim_map.get(claim_id)
            if claim is None:
                errors.append(f"{label} references unknown public claim: {claim_id!r}")
                continue
            claim_sources = claim_source_map.get(claim_id, set())
            if not claim_sources.intersection(valid_sources):
                errors.append(
                    f"{label} claim {claim_id} is unsupported by its declared public_sources"
                )
        referenced_claims = [
            claim_map[claim_id] for claim_id in claim_ids if claim_id in claim_map
        ]
        for source in sorted(valid_sources):
            if not any(
                source in claim_source_map.get(claim.get("id"), set())
                for claim in referenced_claims
            ):
                errors.append(
                    f"{label} source is unrelated to its referenced claims: {source}"
                )
        boundaries = visual.get("does_not_establish")
        if not isinstance(boundaries, list) or not boundaries or any(
            not isinstance(item, str) or not item.strip() for item in boundaries
        ):
            errors.append(f"{label} must state at least one visual non-claim")
        approval_status = visual.get("approval_status")
        if (
            not isinstance(approval_status, str)
            or approval_status not in VISUAL_APPROVAL_STATUSES
        ):
            errors.append(f"{label} has an invalid approval_status")
        if manifest_review_status != "NOT_PERFORMED" and "REV-001" in claim_ids:
            errors.append(
                f"{label} retains the REV-001 NOT_PERFORMED claim while independent "
                "review status has advanced"
            )

        if path.suffix.lower() == ".svg":
            _verify_svg(path, relative, visual, errors)
        else:
            _verify_png(path, relative, visual, errors)

    if visual_ids != sorted(visual_ids):
        errors.append("visual manifest entries must be sorted by id")
    if len(visual_ids) != len(set(visual_ids)):
        errors.append("visual manifest ids must be unique")
    if len(registered_files) != len(set(registered_files)):
        errors.append("visual manifest files must be unique")

    actual_files = {
        _relative(root, path)
        for path in (root / "assets/visuals").rglob("*")
        if path.is_file() and path.suffix.lower() in {".png", ".svg"}
    }
    registered_file_set = set(registered_files)
    for relative in sorted(actual_files - registered_file_set):
        errors.append(f"unregistered visual asset: {relative}")
    for relative in sorted(registered_file_set - actual_files):
        errors.append(f"registered visual asset is missing: {relative}")

    approval_by_file = {
        visual.get("file"): visual.get("approval_status")
        for visual in visuals
        if isinstance(visual, dict) and isinstance(visual.get("file"), str)
    }
    for markdown_path in _iter_text_files(root):
        if markdown_path.suffix.lower() != ".md":
            continue
        text = markdown_path.read_text(encoding="utf-8")
        if re.search(r"!\[[^\]]*\]\[[^\]]*\]", text):
            errors.append(
                f"reference-style Markdown images are not permitted in {_relative(root, markdown_path)}"
            )
        if re.search(r"<(?:img|picture|source)\b", text, flags=re.IGNORECASE):
            errors.append(
                f"raw HTML image elements are not permitted in {_relative(root, markdown_path)}"
            )
        for alt_text, raw_target in MARKDOWN_IMAGE.findall(text):
            target = raw_target.strip().split(maxsplit=1)[0].strip("<>")
            target = target.split("#", 1)[0]
            if target.startswith(("http://", "https://")):
                continue
            if not alt_text.strip():
                errors.append(
                    f"local Markdown image has empty alt text in {_relative(root, markdown_path)}"
                )
            resolved = (markdown_path.parent / target).resolve()
            try:
                relative = _relative(root, resolved)
            except ValueError:
                errors.append(
                    f"image link escapes repository in {_relative(root, markdown_path)}: {target}"
                )
                continue
            if not resolved.is_file():
                errors.append(
                    f"broken local image in {_relative(root, markdown_path)}: {target}"
                )
            elif relative not in registered_file_set:
                errors.append(
                    f"Markdown image is not registered in visual manifest: {relative}"
                )
            elif approval_by_file.get(relative) == "SUPERSEDED":
                errors.append(f"Markdown embeds superseded visual asset: {relative}")


def _iter_json_strings(value: object, path: tuple[str, ...] = ()):
    if isinstance(value, dict):
        for key, child in value.items():
            if isinstance(key, str):
                yield path + (key,), key
                yield from _iter_json_strings(child, path + (key,))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _iter_json_strings(child, path + (str(index),))
    elif isinstance(value, str):
        yield path, value


def _decoded_sensitive_text(relative: str, raw_text: str) -> str:
    fragments = [html.unescape(raw_text)]
    if relative.endswith(".json"):
        try:
            parsed = json.loads(raw_text)
        except json.JSONDecodeError:
            parsed = None
        if parsed is not None:
            exempt_path = (
                "publication_controls",
                "observed_release",
                "commit_sha",
            )
            for path, value in _iter_json_strings(parsed):
                if relative == "evidence/publication.json" and path == exempt_path:
                    continue
                fragments.append(html.unescape(value))
    elif relative.endswith(".svg"):
        try:
            svg = ET.fromstring(raw_text)
        except ET.ParseError:
            svg = None
        if svg is not None:
            for element in svg.iter():
                if element.text:
                    fragments.append(html.unescape(element.text))
                if element.tail:
                    fragments.append(html.unescape(element.tail))
                fragments.extend(html.unescape(value) for value in element.attrib.values())
    return "\n".join(fragments)


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

        # Workflow actions are intentionally pinned to full upstream SHAs. The
        # one other permitted full SHA is the structured, public release commit
        # recorded after publication. Redact only that exact JSON field; any
        # duplicate or out-of-field SHA remains visible to the scanner.
        sha_scan_text = text
        if relative == "evidence/publication.json":
            try:
                publication = json.loads(text)
            except json.JSONDecodeError:
                publication = {}
            controls = publication.get("publication_controls", {})
            observed = controls.get("observed_release", {}) if isinstance(controls, dict) else {}
            observed_sha = observed.get("commit_sha") if isinstance(observed, dict) else None
            if (
                publication.get("status") == "RELEASED"
                and isinstance(observed_sha, str)
                and re.fullmatch(r"[0-9a-f]{40}", observed_sha)
            ):
                field = re.compile(
                    r'("commit_sha"\s*:\s*")' + re.escape(observed_sha) + r'(")'
                )
                sha_scan_text, _ = field.subn(
                    r"\1<observed-release-commit>\2", sha_scan_text, count=1
                )

        scan_text = _decoded_sensitive_text(relative, sha_scan_text)
        lowered = scan_text.casefold()
        for literal in private_deny_list:
            if literal.casefold() in lowered:
                errors.append(f"external private deny-list match in {relative}")
        if disallowed_phrase in lowered:
            errors.append(f"disallowed positioning phrase in {relative}")
        if chr(0x2014) in scan_text:
            errors.append(f"prohibited em dash character in {relative}")
        if PRIVATE_PATH.search(scan_text):
            errors.append(f"operational-style absolute path found in {relative}")
        for repository in GITHUB_REPOSITORY_URL.findall(scan_text):
            if repository.casefold() != CANONICAL_REPOSITORY.casefold():
                errors.append(f"non-canonical GitHub repository URL found in {relative}")

        workflow_source = relative.startswith(".github/workflows/")
        if not workflow_source and full_sha.search(scan_text):
            errors.append(f"full private-style Git SHA found in {relative}")
        if internal_id.search(scan_text):
            errors.append(f"private workflow identifier found in {relative}")
        for pattern in secret_patterns:
            if pattern.search(scan_text):
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
    publication_path = root / "evidence/publication.json"
    if publication_path.is_file():
        try:
            publication = _load_json(publication_path)
        except (OSError, ValueError, json.JSONDecodeError):
            publication = {}
        if publication.get("status") == "RELEASED":
            controls = publication.get("publication_controls", {})
            observed = controls.get("observed_release", {}) if isinstance(controls, dict) else {}
            doi = observed.get("doi") if isinstance(observed, dict) else None
            if not isinstance(doi, str) or f'doi: "{doi}"' not in text:
                errors.append("CITATION.cff DOI must match the observed version DOI")


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
    verify_visual_manifest(root, errors)
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
    print("- visual manifest, assets, and accessibility contract consistent")
    print("- private locator and secret scan passed")
    print("- local Markdown links resolved")
    print("- citation metadata present")
    return 0


if __name__ == "__main__":
    sys.exit(main())
