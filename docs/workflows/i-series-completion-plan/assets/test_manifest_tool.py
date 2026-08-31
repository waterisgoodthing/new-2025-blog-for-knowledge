import unittest

from manifest_tool import (
    build_manifest,
    project_row_to_manifest_revision,
    resolve_revision_projection,
    verify_manifest_rows,
)


class ManifestToolTest(unittest.TestCase):
    def test_build_manifest_applies_authorized_dispositions_without_raw_content(self):
        canonical_owner = "00000000-0000-0000-0000-000000000001"
        source_rows = {
            "capture_items": [],
            "notes": [("note-1", '{"id":"note-1","content":"private"}')],
            "ai_runs": [("run-1", '{"id":"run-1","input_summary":"private"}')],
            "users": [
                (canonical_owner, f'{{"id":"{canonical_owner}","password_hash":"secret"}}'),
                ("00000000-0000-0000-0000-000000000002", '{"id":"00000000-0000-0000-0000-000000000002","password_hash":"other"}'),
            ],
        }

        manifest = build_manifest(
            source_rows,
            canonical_owner=canonical_owner,
            source_revision="020",
            generated_at="2026-07-28T00:00:00+08:00",
        )

        by_key = {(row["source_table"], row["source_id"]): row for row in manifest["rows"]}
        self.assertEqual(by_key[("notes", "note-1")]["disposition"], "MIGRATED")
        self.assertEqual(by_key[("ai_runs", "run-1")]["disposition"], "ARCHIVED")
        self.assertEqual(by_key[("users", canonical_owner)]["disposition"], "MIGRATED")
        self.assertEqual(
            by_key[("users", "00000000-0000-0000-0000-000000000002")]["disposition"],
            "ARCHIVED",
        )
        serialized = str(manifest)
        self.assertNotIn("private", serialized)
        self.assertNotIn("secret", serialized)
        self.assertEqual(manifest["table_counts"]["capture_items"], 0)

    def test_verify_manifest_rows_fails_closed_on_duplicate_or_hash_drift(self):
        canonical_owner = "00000000-0000-0000-0000-000000000001"
        source_rows = {"notes": [("note-1", '{"id":"note-1","content":"original"}')]}
        manifest = build_manifest(
            source_rows,
            canonical_owner=canonical_owner,
            source_revision="020",
            generated_at="2026-07-28T00:00:00+08:00",
        )

        drift = verify_manifest_rows(
            manifest,
            {"notes": [("note-1", '{"id":"note-1","content":"changed"}')]},
        )
        self.assertEqual(drift["hash_drift"], 1)
        self.assertFalse(drift["passed"])

        duplicated_manifest = {**manifest, "rows": manifest["rows"] + manifest["rows"]}
        duplicate = verify_manifest_rows(duplicated_manifest, source_rows)
        self.assertEqual(duplicate["duplicate_manifest"], 1)
        self.assertFalse(duplicate["passed"])

    def test_revision_024_rows_project_to_revision_020_manifest_contract(self):
        note_020 = '{"id":"note-1","title":"Original"}'
        attachment_020 = '{"id":"attachment-1","storage_key":"uploads/a.png"}'

        projected_note = project_row_to_manifest_revision(
            "notes",
            '{"id":"note-1","title":"Original","revision":1}',
            manifest_revision="020",
            database_revision="024",
        )
        projected_attachment = project_row_to_manifest_revision(
            "attachments",
            (
                '{"id":"attachment-1","storage_key":"uploads/a.png",'
                '"display_name":"a.png","folder_id":null,"trashed_at":null}'
            ),
            manifest_revision="020",
            database_revision="024",
        )

        self.assertEqual(projected_note, note_020)
        self.assertEqual(projected_attachment, attachment_020)

    def test_revision_projection_fails_closed_for_unsupported_pair(self):
        with self.assertRaisesRegex(RuntimeError, "Unsupported manifest/database revision pair"):
            resolve_revision_projection("019", "024")


if __name__ == "__main__":
    unittest.main()
