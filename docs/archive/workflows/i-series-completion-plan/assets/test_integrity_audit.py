import unittest

from integrity_audit import evaluate_audit


class IntegrityAuditTest(unittest.TestCase):
    def setUp(self):
        self.facts = {
            "source_revision": "024",
            "manifest_verification": {
                "passed": True,
                "source_count": 121,
                "manifest_count": 121,
                "source_aggregate_matches": True,
            },
            "fk_integrity": {
                "mistake_question": 0,
                "mistake_draft": 0,
                "review_item_target": 0,
                "review_record_item": 0,
                "attachment_link_attachment": 0,
                "attachment_link_target": 0,
                "capture_attachment": 0,
            },
            "backfill_verification": {
                "notes_revision_null": 0,
                "notes_revision_min": 1,
                "attachments_display_name_null": 0,
                "attachments_display_name_mismatch": 0,
                "attachments_folder_id_null": 1,
            },
            "source_facts": {
                "table_counts": {
                    "notes": 13,
                    "questions": 3,
                    "mistakes": 3,
                    "review_items": 3,
                    "review_records": 4,
                    "attachments": 1,
                    "attachment_links": 1,
                    "capture_items": 0,
                    "draft_items": 6,
                    "ai_runs": 32,
                    "ai_call_logs": 47,
                    "users": 8,
                },
                "extensions": ["pg_trgm", "plpgsql"],
                "canonical_owner": "4c503215-b158-4162-b472-79df8289ed0a",
                "admin_count": 4,
                "total_users": 8,
            },
        }

    def test_passes_only_when_all_integrity_gates_are_satisfied(self):
        report = evaluate_audit(self.facts)

        self.assertTrue(report["passed"])
        self.assertEqual(report["conclusion"], "PASS")
        self.assertEqual(report["fk_orphan_count"], 0)

        self.facts["backfill_verification"]["attachments_display_name_mismatch"] = 1
        drifted = evaluate_audit(self.facts)

        self.assertFalse(drifted["passed"])
        self.assertEqual(drifted["conclusion"], "FAIL")


if __name__ == "__main__":
    unittest.main()
