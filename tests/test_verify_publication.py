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

    def test_release_mode_rejects_repository_only_approval(self) -> None:
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
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        self.assertEqual(verify(self.root, release=True), [])

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
        data["status"] = "RELEASED"
        data["publication_controls"]["release_approval"] = "APPROVED"
        data["publication_controls"]["observed_release"]["commit_sha"] = "a" * 40
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        self.assertEqual(verify(self.root), [])

    def test_observed_release_sha_is_not_exempt_while_ready(self) -> None:
        path = self.root / "evidence/publication.json"
        data = json.loads(path.read_text(encoding="utf-8"))
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


if __name__ == "__main__":
    unittest.main()
