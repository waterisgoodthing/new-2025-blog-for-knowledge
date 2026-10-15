import unittest

from shadow_delta_tool import (
    build_delta_manifest,
    classify_delta,
    replay_delta,
    validate_shadow_target,
)


class ShadowTargetSafetyTests(unittest.TestCase):
    def test_rejects_daily_database_as_shadow_target(self):
        with self.assertRaisesRegex(ValueError, "Refusing source database"):
            validate_shadow_target("blog_db")


class DeltaClassificationTests(unittest.TestCase):
    def test_classifies_insert_update_delete_and_unchanged(self):
        before = {
            ("notes", "same"): "hash-a",
            ("notes", "updated"): "hash-before",
            ("notes", "deleted"): "hash-deleted",
        }
        after = {
            ("notes", "same"): "hash-a",
            ("notes", "updated"): "hash-after",
            ("notes", "inserted"): "hash-inserted",
        }

        result = classify_delta(before, after)

        self.assertEqual(result["unchanged"], [("notes", "same")])
        self.assertEqual(result["inserted"], [("notes", "inserted")])
        self.assertEqual(result["updated"], [("notes", "updated")])
        self.assertEqual(result["deleted"], [("notes", "deleted")])


class DeltaManifestTests(unittest.TestCase):
    def test_preserves_v1_and_archives_new_noncanonical_user(self):
        v1 = {
            "canonical_owner_id": "owner-1",
            "rows": [
                {
                    "source_table": "notes",
                    "source_id": "note-1",
                    "source_row_hash": "hash-note",
                }
            ],
        }
        current = {
            ("notes", "note-1"): "hash-note",
            ("users", "user-2"): "hash-user",
        }

        delta = build_delta_manifest(v1, current, generated_at="now")

        self.assertEqual(delta["base_count"], 1)
        self.assertEqual(delta["delta_count"], 1)
        self.assertEqual(delta["current_count"], 2)
        self.assertEqual(delta["rows"][0]["source_id"], "user-2")
        self.assertEqual(delta["rows"][0]["disposition"], "ARCHIVED")
        self.assertEqual(delta["rows"][0]["target_owner_id"], "owner-1")


class DeltaReplayTests(unittest.TestCase):
    def test_replay_is_idempotent_and_tombstones_deletes(self):
        before = {
            ("notes", "updated"): "hash-before",
            ("notes", "deleted"): "hash-deleted",
        }
        after = {
            ("notes", "updated"): "hash-after",
            ("notes", "inserted"): "hash-inserted",
        }
        ledger = {
            ("notes", "updated"): {
                "source_row_hash": "hash-before",
                "owner_id": "owner-1",
                "disposition": "MIGRATED",
            },
            ("notes", "deleted"): {
                "source_row_hash": "hash-deleted",
                "owner_id": "owner-1",
                "disposition": "MIGRATED",
            },
        }

        first = replay_delta(ledger, {}, before, after, owner_id="owner-1")
        second = replay_delta(
            first["ledger"],
            first["tombstones"],
            before,
            after,
            owner_id="owner-1",
        )

        self.assertEqual(first["applied_count"], 3)
        self.assertEqual(second["applied_count"], 0)
        self.assertEqual(
            first["ledger"][("notes", "deleted")]["disposition"],
            "TOMBSTONED",
        )
        self.assertEqual(
            first["tombstones"][("notes", "deleted")]["last_source_row_hash"],
            "hash-deleted",
        )


if __name__ == "__main__":
    unittest.main()
