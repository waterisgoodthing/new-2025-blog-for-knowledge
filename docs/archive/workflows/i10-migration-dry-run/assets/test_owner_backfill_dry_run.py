import unittest

from owner_backfill_dry_run import (
    evaluate_audit,
    validate_manifest,
    validate_target_database,
)


class TargetDatabaseSafetyTests(unittest.TestCase):
    def test_rejects_daily_database(self):
        with self.assertRaisesRegex(ValueError, "Refusing daily database"):
            validate_target_database("blog_db")


class ManifestValidationTests(unittest.TestCase):
    def test_accepts_complete_single_owner_manifest(self):
        payload = {
            "source_count": 2,
            "canonical_owner_id": "owner-1",
            "rows": [
                {
                    "source_table": "notes",
                    "source_id": "note-1",
                    "target_owner_id": "owner-1",
                },
                {
                    "source_table": "users",
                    "source_id": "owner-1",
                    "target_owner_id": "owner-1",
                },
            ],
        }

        self.assertEqual(
            validate_manifest(payload),
            {"row_count": 2, "owner_count": 1, "duplicate_count": 0},
        )


class AuditEvaluationTests(unittest.TestCase):
    def test_passes_only_complete_clean_backfill(self):
        metrics = {
            "source_count": 121,
            "manifest_count": 121,
            "sidecar_count": 121,
            "missing_count": 0,
            "extra_count": 0,
            "hash_drift_count": 0,
            "owner_conflict_count": 0,
            "owner_fk_orphan_count": 0,
            "relationship_orphan_count": 0,
            "database_revision": "025",
            "canonical_owner_count": 1,
        }

        self.assertTrue(evaluate_audit(metrics))


if __name__ == "__main__":
    unittest.main()
