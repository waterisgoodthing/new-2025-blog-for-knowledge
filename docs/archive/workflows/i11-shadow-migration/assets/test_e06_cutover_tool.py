import unittest

from e06_cutover_tool import (
    compare_snapshots,
    rewrite_env_authority,
    validate_database_pair,
)


class DatabasePairSafetyTests(unittest.TestCase):
    def test_rejects_source_as_cutover_target(self):
        with self.assertRaisesRegex(ValueError, "must differ"):
            validate_database_pair("blog_db", "blog_db")


class RuntimeAuthorityTests(unittest.TestCase):
    def test_rewrites_only_database_and_upload_authority(self):
        original = (
            "DATABASE_URL=postgresql+asyncpg://blog_user:s3cr%t@localhost:5432/blog_db\n"
            "JWT_SECRET_KEY=keep-me\n"
            "AUTH_BYPASS=false\n"
        )

        rewritten = rewrite_env_authority(
            original,
            target_database="blog_v2",
            target_upload_root="/private/authority/uploads",
        )

        self.assertIn("blog_user:s3cr%t@localhost:5432/blog_v2", rewritten)
        self.assertIn("JWT_SECRET_KEY=keep-me", rewritten)
        self.assertIn("AUTH_BYPASS=false", rewritten)
        self.assertIn("UPLOAD_ROOT=/private/authority/uploads", rewritten)
        self.assertNotIn("/blog_db", rewritten)

    def test_can_rewrite_authority_back_to_source(self):
        original = (
            "DATABASE_URL=postgresql+asyncpg://blog_user:secret@localhost:5432/blog_v2\n"
            "UPLOAD_ROOT=/private/authority/uploads\n"
        )

        rewritten = rewrite_env_authority(
            original,
            expected_current_database="blog_v2",
            target_database="blog_db",
            target_upload_root="/repo/backend/uploads",
        )

        self.assertIn("localhost:5432/blog_db", rewritten)
        self.assertIn("UPLOAD_ROOT=/repo/backend/uploads", rewritten)


class DeltaContractTests(unittest.TestCase):
    def test_accepts_zero_delta_across_expected_revision_change(self):
        source = {
            "database_revision": "024",
            "source_count": 1,
            "aggregate_sha256": "aggregate",
            "rows": [
                {
                    "source_table": "notes",
                    "source_id": "note-1",
                    "source_row_hash": "hash-1",
                }
            ],
        }
        target = {**source, "database_revision": "025"}

        result = compare_snapshots(
            source,
            target,
            expected_source_revision="024",
            expected_target_revision="025",
        )

        self.assertTrue(result["passed"])
        self.assertEqual(result["delta_count"], 0)


if __name__ == "__main__":
    unittest.main()
