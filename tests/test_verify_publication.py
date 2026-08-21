from __future__ import annotations

# SPDX-License-Identifier: Apache-2.0

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from tools.verify_publication import verify


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


class PublicationVerifierTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name) / "record"
        shutil.copytree(REPOSITORY_ROOT, self.root, ignore=shutil.ignore_patterns("__pycache__"))

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_repository_passes(self) -> None:
        self.assertEqual(verify(self.root), [])

    def test_release_mode_rejects_pending_release_approval(self) -> None:
        path = self.root / "evidence/publication.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["status"] = "READY"
        data["publication_controls"]["release_approval"] = "PENDING"
        data["publication_controls"].pop("release_approval_record", None)
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        errors = verify(self.root, release=True)
        self.assertFalse(any("status READY or RELEASED" in error for error in errors))
        self.assertTrue(any("explicit release approval" in error for error in errors))

    def test_release_mode_rejects_draft(self) -> None:
        path = self.root / "evidence/publication.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["status"] = "DRAFT"
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        errors = verify(self.root, release=True)
        self.assertTrue(any("status READY or RELEASED" in error for error in errors))

    def test_release_mode_accepts_approved_candidate(self) -> None:
        path = self.root / "evidence/publication.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["status"] = "READY"
        data["publication_controls"]["release_approval"] = "APPROVED"
        data["publication_controls"]["observed_release"] = {
            "commit_sha": None,
            "tag": None,
            "release_url": None,
            "doi": None,
        }
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        self.assertEqual(verify(self.root, release=True), [])

    def test_release_mode_rejects_approval_without_release_record(self) -> None:
        path = self.root / "evidence/publication.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["status"] = "READY"
        data["publication_controls"]["release_approval"] = "APPROVED"
        data["publication_controls"].pop("release_approval_record", None)
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        self.assertTrue(
            any(
                "version-bound Release approval record" in error
                for error in verify(self.root, release=True)
            )
        )

    def test_release_mode_rejects_wrong_release_identity(self) -> None:
        path = self.root / "evidence/publication.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["status"] = "READY"
        data["publication_controls"]["release_approval"] = "APPROVED"
        data["publication_controls"]["release_approval_record"]["release"] = "v9.9.9"
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        self.assertTrue(
            any(
                "version-bound Release approval record" in error
                for error in verify(self.root, release=True)
            )
        )

    def test_missing_required_file_fails(self) -> None:
        (self.root / "README.md").unlink()
        self.assertTrue(any("missing required file: README.md" in error for error in verify(self.root)))

    def test_external_private_deny_list_fails_without_echoing_value(self) -> None:
        private_literal = "private" + "-source-" + "repository-example"
        path = self.root / "README.md"
        path.write_text(path.read_text(encoding="utf-8") + f"\n{private_literal}\n", encoding="utf-8")
        deny_list = Path(self.temp_dir.name) / "private-deny-list.txt"
        deny_list.write_text(private_literal + "\n", encoding="utf-8")
        errors = verify(self.root, private_deny_list=deny_list)
        self.assertTrue(any("external private deny-list match" in error for error in errors))
        self.assertTrue(all(private_literal not in error for error in errors))

    def test_operational_path_fails(self) -> None:
        private_path = "/" + "srv" + "/example"
        path = self.root / "README.md"
        path.write_text(path.read_text(encoding="utf-8") + f"\n{private_path}\n", encoding="utf-8")
        self.assertTrue(any("operational-style absolute path" in error for error in verify(self.root)))

    def test_internal_identifier_fails(self) -> None:
        private_identifier = "RV-" + "2099-999"
        path = self.root / "README.md"
        path.write_text(path.read_text(encoding="utf-8") + f"\n{private_identifier}\n", encoding="utf-8")
        self.assertTrue(any("private workflow identifier" in error for error in verify(self.root)))

    def test_full_git_sha_fails(self) -> None:
        path = self.root / "README.md"
        path.write_text(path.read_text(encoding="utf-8") + "\n" + "a" * 40 + "\n", encoding="utf-8")
        self.assertTrue(any("full private-style Git SHA" in error for error in verify(self.root)))

    def test_released_record_accepts_observed_release_commit_sha(self) -> None:
        path = self.root / "evidence/publication.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        observed = data["publication_controls"]["observed_release"]
        data["status"] = "RELEASED"
        data["publication_controls"]["release_approval"] = "APPROVED"
        observed["commit_sha"] = "a" * 40
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        self.assertEqual(verify(self.root), [])

    def test_observed_release_sha_is_not_exempt_while_ready(self) -> None:
        path = self.root / "evidence/publication.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["status"] = "READY"
        data["publication_controls"]["observed_release"]["commit_sha"] = "a" * 40
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        self.assertTrue(any("full private-style Git SHA" in error for error in verify(self.root)))

    def test_observed_release_sha_exemption_is_field_scoped(self) -> None:
        path = self.root / "evidence/publication.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["status"] = "RELEASED"
        data["publication_controls"]["release_approval"] = "APPROVED"
        data["publication_controls"]["observed_release"]["commit_sha"] = "a" * 40
        data["publication_controls"]["observed_release"]["doi"] = "b" * 40
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        self.assertTrue(any("full private-style Git SHA" in error for error in verify(self.root)))

    def test_released_record_rejects_mismatched_tag(self) -> None:
        path = self.root / "evidence/publication.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["publication_controls"]["observed_release"]["tag"] = "v9.9.9"
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        self.assertTrue(any("observed release tag" in error for error in verify(self.root)))

    def test_released_record_rejects_missing_provenance_digest(self) -> None:
        path = self.root / "evidence/publication.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["publication_controls"]["observed_release"]["bundle_sha256"] = None
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        self.assertTrue(any("bundle_sha256" in error for error in verify(self.root)))

    def test_released_record_rejects_citation_doi_mismatch(self) -> None:
        path = self.root / "CITATION.cff"
        path.write_text(
            path.read_text(encoding="utf-8").replace(
                "10.5281/zenodo.22019208", "10.5281/zenodo.99999999"
            ),
            encoding="utf-8",
        )
        self.assertTrue(any("CITATION.cff DOI" in error for error in verify(self.root)))

    def test_possible_secret_fails(self) -> None:
        path = self.root / "README.md"
        path.write_text(path.read_text(encoding="utf-8") + "\nghp_" + "A" * 24 + "\n", encoding="utf-8")
        self.assertTrue(any("possible secret material" in error for error in verify(self.root)))

    def test_test_fixtures_are_scanned(self) -> None:
        path = self.root / "tests/test_verify_publication.py"
        secret = "ghp_" + "B" * 24
        path.write_text(path.read_text(encoding="utf-8") + f"\n# {secret}\n", encoding="utf-8")
        self.assertTrue(any("possible secret material" in error for error in verify(self.root)))

    def test_broken_link_fails(self) -> None:
        path = self.root / "README.md"
        path.write_text(path.read_text(encoding="utf-8") + "\n[missing](docs/missing.md)\n", encoding="utf-8")
        self.assertTrue(any("broken local link" in error for error in verify(self.root)))
    def test_citation_rejects_repository_wide_apache_alternative(self) -> None:
        path = self.root / "CITATION.cff"
        text = path.read_text(encoding="utf-8").replace(
            "license: CC-BY-NC-4.0",
            "license:\n  - CC-BY-NC-4.0\n  - Apache-2.0",
        )
        path.write_text(text, encoding="utf-8")
        self.assertTrue(
            any("complete cited record" in error for error in verify(self.root))
        )

    def test_duplicate_claim_id_fails(self) -> None:
        path = self.root / "evidence/public-claims.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["claims"].append(dict(data["claims"][0]))
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        self.assertTrue(any("claim ids must be unique" in error for error in verify(self.root)))

    def test_unsorted_claims_fail(self) -> None:
        path = self.root / "evidence/public-claims.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["claims"][0], data["claims"][1] = data["claims"][1], data["claims"][0]
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        self.assertTrue(any("claims must be sorted" in error for error in verify(self.root)))

    def test_commitment_mismatch_fails(self) -> None:
        path = self.root / "evidence/publication.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["derived_from"]["baseline_manifest_sha256"] = "f" * 64
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        self.assertTrue(any("baseline digest differs" in error for error in verify(self.root)))

    def test_declared_source_without_claim_marker_fails(self) -> None:
        path = self.root / "README.md"
        text = path.read_text(encoding="utf-8").replace("AUD-002 ", "")
        path.write_text(text, encoding="utf-8")
        self.assertTrue(any("is not marked in declared public source" in error for error in verify(self.root)))

    def test_unregistered_claim_marker_fails(self) -> None:
        path = self.root / "README.md"
        path.write_text(
            path.read_text(encoding="utf-8") + "\n<!-- public-claims: ZZZ-999 -->\n",
            encoding="utf-8",
        )
        self.assertTrue(any("unregistered public claim marker" in error for error in verify(self.root)))

    def test_disallowed_positioning_phrase_fails(self) -> None:
        phrase = "case" + " study"
        path = self.root / "README.md"
        path.write_text(path.read_text(encoding="utf-8") + f"\nA research {phrase}.\n", encoding="utf-8")
        self.assertTrue(any("disallowed positioning phrase" in error for error in verify(self.root)))

    def test_em_dash_character_fails(self) -> None:
        path = self.root / "README.md"
        prohibited_character = chr(0x2014)
        path.write_text(
            path.read_text(encoding="utf-8")
            + f"\nAuthority {prohibited_character} implementation.\n",
            encoding="utf-8",
        )
        self.assertTrue(any("prohibited em dash character" in error for error in verify(self.root)))

    def test_missing_visual_manifest_fails(self) -> None:
        (self.root / "assets/visuals/manifest.json").unlink()
        self.assertTrue(
            any(
                "missing required file: assets/visuals/manifest.json" in error
                for error in verify(self.root)
            )
        )

    def test_unregistered_visual_fails(self) -> None:
        source = self.root / "assets/visuals/system-map.svg"
        target = self.root / "assets/visuals/unregistered.svg"
        shutil.copyfile(source, target)
        self.assertTrue(any("unregistered visual asset" in error for error in verify(self.root)))

    def test_visual_unknown_claim_fails(self) -> None:
        path = self.root / "assets/visuals/manifest.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["visuals"][0]["claim_ids"].append("ZZZ-999")
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        self.assertTrue(
            any("references unknown public claim" in error for error in verify(self.root))
        )

    def test_visual_claim_requires_supporting_source(self) -> None:
        path = self.root / "assets/visuals/manifest.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["visuals"][0]["public_sources"] = ["docs/02-implementation-record.md"]
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        self.assertTrue(
            any("unsupported by its declared public_sources" in error for error in verify(self.root))
        )

    def test_visual_requires_nonclaim(self) -> None:
        path = self.root / "assets/visuals/manifest.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["visuals"][0]["does_not_establish"] = []
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        self.assertTrue(any("visual non-claim" in error for error in verify(self.root)))

    def test_visual_review_status_matches_publication(self) -> None:
        path = self.root / "assets/visuals/manifest.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["independent_review_status"] = "COMPLETED"
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        self.assertTrue(
            any("differs from publication record" in error for error in verify(self.root))
        )

    def test_svg_requires_accessible_title_and_description(self) -> None:
        path = self.root / "assets/visuals/system-map.svg"
        text = path.read_text(encoding="utf-8").replace(
            '<title id="system-map-title">',
            '<metadata id="system-map-title">',
            1,
        ).replace("</title>", "</metadata>", 1)
        path.write_text(text, encoding="utf-8")
        self.assertTrue(any("begin with title and desc" in error for error in verify(self.root)))

    def test_svg_rejects_script(self) -> None:
        path = self.root / "assets/visuals/system-map.svg"
        text = path.read_text(encoding="utf-8").replace("</svg>", "<script/></svg>")
        path.write_text(text, encoding="utf-8")
        self.assertTrue(any("prohibited element script" in error for error in verify(self.root)))

    def test_svg_rejects_external_reference(self) -> None:
        path = self.root / "assets/visuals/system-map.svg"
        text = path.read_text(encoding="utf-8").replace(
            "</svg>",
            '<use href="https://example.invalid/external.svg#node"/></svg>',
        )
        path.write_text(text, encoding="utf-8")
        self.assertTrue(any("external reference" in error for error in verify(self.root)))

    def test_visual_manifest_rejects_unsupported_field(self) -> None:
        path = self.root / "assets/visuals/manifest.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["visuals"][0]["uncontrolled_note"] = "not part of the schema"
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        self.assertTrue(any("unsupported field" in error for error in verify(self.root)))

    def test_visual_rejects_invalid_approval_status(self) -> None:
        path = self.root / "assets/visuals/manifest.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["visuals"][0]["approval_status"] = "REVIEWED"
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        self.assertTrue(any("invalid approval_status" in error for error in verify(self.root)))

    def test_svg_dimension_mismatch_fails(self) -> None:
        path = self.root / "assets/visuals/manifest.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        system_map = next(item for item in data["visuals"] if item["id"] == "system-map")
        system_map["height"] += 1
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        self.assertTrue(any("SVG height differs" in error for error in verify(self.root)))

    def test_png_dimension_mismatch_fails(self) -> None:
        path = self.root / "assets/visuals/manifest.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        social_preview = next(
            item for item in data["visuals"] if item["id"] == "social-preview"
        )
        social_preview["width"] += 1
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        self.assertTrue(any("PNG dimensions differ" in error for error in verify(self.root)))

    def test_local_markdown_image_requires_alt_text(self) -> None:
        path = self.root / "README.md"
        path.write_text(
            path.read_text(encoding="utf-8")
            + "\n![](assets/visuals/system-map.svg)\n",
            encoding="utf-8",
        )
        self.assertTrue(any("empty alt text" in error for error in verify(self.root)))

    def test_broken_local_markdown_image_fails(self) -> None:
        path = self.root / "README.md"
        path.write_text(
            path.read_text(encoding="utf-8")
            + "\n![missing visual](assets/visuals/missing.svg)\n",
            encoding="utf-8",
        )
        self.assertTrue(any("broken local image" in error for error in verify(self.root)))

    def test_encoded_json_private_path_fails(self) -> None:
        path = self.root / "assets/visuals/manifest.json"
        encoded_path = "\\u002froot\\u002fprivate-record"
        text = path.read_text(encoding="utf-8").replace(
            "Repository social preview identifying",
            encoded_path + " Repository social preview identifying",
            1,
        )
        path.write_text(text, encoding="utf-8")
        self.assertTrue(
            any("operational-style absolute path" in error for error in verify(self.root))
        )

    def test_encoded_svg_private_path_fails(self) -> None:
        path = self.root / "assets/visuals/system-map.svg"
        slash_entity = "&" + "#47;"
        payload = f"<text>{slash_entity}root{slash_entity}private-record</text>"
        path.write_text(
            path.read_text(encoding="utf-8").replace("</svg>", payload + "</svg>"),
            encoding="utf-8",
        )
        self.assertTrue(
            any("operational-style absolute path" in error for error in verify(self.root))
        )

    def test_svg_rejects_processing_instruction(self) -> None:
        path = self.root / "assets/visuals/system-map.svg"
        path.write_text(
            '<?xml-stylesheet href="https://example.invalid/style.css"?>\n'
            + path.read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        self.assertTrue(
            any("processing instructions" in error for error in verify(self.root))
        )

    def test_svg_rejects_xml_base(self) -> None:
        path = self.root / "assets/visuals/system-map.svg"
        text = path.read_text(encoding="utf-8").replace(
            'role="img"',
            'xml:base="https://example.invalid/" role="img"',
            1,
        )
        path.write_text(text, encoding="utf-8")
        self.assertTrue(any("xml:base" in error for error in verify(self.root)))

    def test_png_rejects_invalid_first_chunk(self) -> None:
        path = self.root / "assets/visuals/social-preview.png"
        data = bytearray(path.read_bytes())
        data[12:16] = b"FAKE"
        path.write_bytes(data)
        self.assertTrue(any("must begin with" in error for error in verify(self.root)))

    def test_png_rejects_trailing_payload(self) -> None:
        path = self.root / "assets/visuals/social-preview.png"
        path.write_bytes(path.read_bytes() + b"trailing-payload")
        self.assertTrue(any("end exactly" in error for error in verify(self.root)))

    def test_png_rejects_text_metadata_chunk(self) -> None:
        path = self.root / "assets/visuals/social-preview.png"
        data = bytearray(path.read_bytes())
        first_idat = data.find(b"IDAT")
        self.assertGreater(first_idat, 0)
        data[first_idat : first_idat + 4] = b"tEXt"
        path.write_bytes(data)
        self.assertTrue(any("unsupported metadata" in error for error in verify(self.root)))

    def test_visual_manifest_malformed_claim_ids_do_not_crash(self) -> None:
        path = self.root / "assets/visuals/manifest.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["visuals"][0]["claim_ids"] = ["SYS-001", 7]
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        self.assertTrue(any("valid strings" in error for error in verify(self.root)))

    def test_malformed_registered_claim_sources_do_not_crash(self) -> None:
        path = self.root / "evidence/public-claims.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        claim = next(item for item in data["claims"] if item["id"] == "ARC-001")
        claim["public_sources"].append({"unexpected": "source"})
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        errors = verify(self.root)
        self.assertTrue(
            any(
                "public_sources must contain only non-empty strings" in error
                for error in errors
            )
        )

    def test_visual_manifest_malformed_approval_status_does_not_crash(self) -> None:
        path = self.root / "assets/visuals/manifest.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["visuals"][0]["approval_status"] = {}
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        self.assertTrue(any("invalid approval_status" in error for error in verify(self.root)))

    def test_invalid_independent_review_status_fails_even_when_records_match(self) -> None:
        publication_path = self.root / "evidence/publication.json"
        publication = json.loads(publication_path.read_text(encoding="utf-8"))
        publication["independent_review"]["status"] = "BOGUS"
        publication_path.write_text(
            json.dumps(publication, indent=2) + "\n", encoding="utf-8"
        )
        manifest_path = self.root / "assets/visuals/manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["independent_review_status"] = "BOGUS"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        errors = verify(self.root)
        self.assertTrue(any("independent review status is invalid" in error for error in errors))
        self.assertTrue(any("independent_review_status is invalid" in error for error in errors))

    def test_completed_review_requires_evidence_and_retires_not_performed_claim(self) -> None:
        publication_path = self.root / "evidence/publication.json"
        publication = json.loads(publication_path.read_text(encoding="utf-8"))
        publication["independent_review"] = {
            "status": "COMPLETED",
            "reviewed_release": None,
            "public_statement": None,
        }
        publication_path.write_text(
            json.dumps(publication, indent=2) + "\n", encoding="utf-8"
        )

        manifest_path = self.root / "assets/visuals/manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["independent_review_status"] = "COMPLETED"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

        errors = verify(self.root)
        self.assertTrue(any("version-bound release" in error for error in errors))
        self.assertTrue(any("stable HTTPS public statement" in error for error in errors))
        self.assertTrue(any("REV-001 NOT_PERFORMED" in error for error in errors))

    def test_visual_rejects_unrelated_declared_source(self) -> None:
        path = self.root / "assets/visuals/manifest.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        sources = data["visuals"][0]["public_sources"]
        data["visuals"][0]["public_sources"] = sorted(sources + ["SECURITY.md"])
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        self.assertTrue(any("source is unrelated" in error for error in verify(self.root)))

    def test_markdown_rejects_superseded_visual(self) -> None:
        path = self.root / "assets/visuals/manifest.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        system_map = next(item for item in data["visuals"] if item["id"] == "system-map")
        system_map["approval_status"] = "SUPERSEDED"
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        self.assertTrue(any("embeds superseded" in error for error in verify(self.root)))

    def test_visual_schema_contract_is_verified(self) -> None:
        path = self.root / "schemas/visual-manifest.schema.json"
        path.write_text("{}\n", encoding="utf-8")
        self.assertTrue(any("schema root contract" in error for error in verify(self.root)))

    def test_svg_rejects_css_animation(self) -> None:
        path = self.root / "assets/visuals/system-map.svg"
        text = path.read_text(encoding="utf-8").replace(
            "</svg>",
            "<style>@keyframes pulse { from { opacity: 1; } to { opacity: 0; } }</style></svg>",
        )
        path.write_text(text, encoding="utf-8")
        self.assertTrue(any("CSS animation" in error for error in verify(self.root)))

    def test_svg_requires_canonical_namespace(self) -> None:
        path = self.root / "assets/visuals/system-map.svg"
        text = path.read_text(encoding="utf-8").replace(
            "http://www.w3.org/2000/svg",
            "https://example.invalid/not-svg",
            1,
        )
        path.write_text(text, encoding="utf-8")
        self.assertTrue(any("canonical SVG namespace" in error for error in verify(self.root)))

    def test_svg_rejects_duplicate_ids(self) -> None:
        path = self.root / "assets/visuals/system-map.svg"
        text = path.read_text(encoding="utf-8").replace(
            'id="system-map-desc"',
            'id="system-map-title"',
            1,
        )
        path.write_text(text, encoding="utf-8")
        self.assertTrue(any("ids must be unique" in error for error in verify(self.root)))

    def test_svg_rejects_unresolved_fragment(self) -> None:
        path = self.root / "assets/visuals/system-map.svg"
        text = path.read_text(encoding="utf-8").replace(
            "url(#system-arrow)",
            "url(#missing-arrow)",
            1,
        )
        path.write_text(text, encoding="utf-8")
        self.assertTrue(any("unresolved fragment" in error for error in verify(self.root)))

    def test_svg_viewbox_must_match_dimensions(self) -> None:
        svg_path = self.root / "assets/visuals/system-map.svg"
        svg_path.write_text(
            svg_path.read_text(encoding="utf-8").replace(
                'viewBox="0 0 960 1500"',
                'viewBox="0 0 1 1"',
                1,
            ),
            encoding="utf-8",
        )
        manifest_path = self.root / "assets/visuals/manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        system_map = next(
            item for item in manifest["visuals"] if item["id"] == "system-map"
        )
        system_map["view_box"] = "0 0 1 1"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        self.assertTrue(any("intrinsic dimensions" in error for error in verify(self.root)))

    def test_reference_style_markdown_image_is_rejected(self) -> None:
        path = self.root / "README.md"
        path.write_text(
            path.read_text(encoding="utf-8")
            + "\n![system map][system-map-ref]\n\n"
            + "[system-map-ref]: assets/visuals/system-map.svg\n",
            encoding="utf-8",
        )
        self.assertTrue(any("reference-style" in error for error in verify(self.root)))

    def test_raw_html_image_is_rejected(self) -> None:
        path = self.root / "README.md"
        path.write_text(
            path.read_text(encoding="utf-8")
            + '\n<img src="assets/visuals/system-map.svg" alt="system map">\n',
            encoding="utf-8",
        )
        self.assertTrue(any("raw HTML image" in error for error in verify(self.root)))


if __name__ == "__main__":
    unittest.main()
