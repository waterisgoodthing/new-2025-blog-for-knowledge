#!/usr/bin/env python3
"""Tests for scripts/week3-scratch-guard.py (W3-00 scratch-only guard).

Run either way:

    python3 scripts/week3-scratch-guard.test.py
    python3 -m pytest scripts/week3-scratch-guard.test.py -q
"""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "week3-scratch-guard.py"


def _load_guard():
    spec = importlib.util.spec_from_file_location("week3_scratch_guard", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


guard = _load_guard()

LEGAL_NAMES = ("astra_week3_demo", "astra_week3_x", "astra_week3_pr09", "astra_week3_ok_01")

ILLEGAL_NAMES = (
    "blog_db",
    "blog_v2",
    "astra_week2_x",
    "astra_week3_bad-name",
    "astra_week3_bad.name",
    "astra_week3_bad!",
    "astra_week3_UPPER",
    "ASTRA_WEEK3_X",
    "astra_week3",
    "week3_demo",
    "production_db",
)

PROD_URLS = (
    "postgresql+asyncpg://blog_user:secret@localhost:5432/blog_v2",
    "postgresql+asyncpg://user:pass@prod-db.example.com:5432/blog_db",
    "postgresql://app:pw@prod.rds.amazonaws.com:5432/production_db",
    "postgresql+asyncpg://user:pass@db.internal:5432/astra_week3_ok?options=-c%20blog_db",
)

LOCAL_URL = "postgresql+asyncpg://scratch:scratch@localhost:5432/astra_week3_demo"
LOCAL_URL_OTHER = "postgresql+asyncpg://scratch:scratch@localhost:5432/astra_week3_other"
REMOTE_SCRATCH_URL = "postgresql+asyncpg://scratch:scratch@db.internal:5432/astra_week3_demo"


class TestCheckSubcommand(unittest.TestCase):
    def test_legal_names_pass(self) -> None:
        for name in LEGAL_NAMES:
            with self.subTest(name=name):
                rc = guard.main(["check", "--db-name", name])
                self.assertEqual(rc, guard.EXIT_OK)

    def test_illegal_names_fail(self) -> None:
        for name in ILLEGAL_NAMES:
            with self.subTest(name=name):
                rc = guard.main(["check", "--db-name", name])
                self.assertEqual(rc, guard.EXIT_FAIL)

    def test_empty_name_fails(self) -> None:
        self.assertEqual(guard.main(["check", "--db-name", ""]), guard.EXIT_FAIL)

    def test_no_args_without_env_fails(self) -> None:
        saved = os.environ.pop(guard.ENV_DATABASE_URL, None)
        try:
            self.assertEqual(guard.main(["check"]), guard.EXIT_FAIL)
        finally:
            if saved is not None:
                os.environ[guard.ENV_DATABASE_URL] = saved

    def test_env_database_url_with_prod_db_fails(self) -> None:
        saved = os.environ.get(guard.ENV_DATABASE_URL)
        os.environ[guard.ENV_DATABASE_URL] = (
            "postgresql+asyncpg://blog_user:secret@localhost:5432/blog_v2"
        )
        try:
            self.assertEqual(guard.main(["check"]), guard.EXIT_FAIL)
        finally:
            if saved is None:
                os.environ.pop(guard.ENV_DATABASE_URL, None)
            else:
                os.environ[guard.ENV_DATABASE_URL] = saved

    def test_env_database_url_with_legal_scratch_name_passes(self) -> None:
        saved = os.environ.get(guard.ENV_DATABASE_URL)
        os.environ[guard.ENV_DATABASE_URL] = (
            "postgresql+asyncpg://scratch:scratch@localhost:5432/astra_week3_env_ok"
        )
        try:
            self.assertEqual(guard.main(["check"]), guard.EXIT_OK)
        finally:
            if saved is None:
                os.environ.pop(guard.ENV_DATABASE_URL, None)
            else:
                os.environ[guard.ENV_DATABASE_URL] = saved

    def test_prod_urls_fail(self) -> None:
        for url in PROD_URLS:
            with self.subTest(url=url):
                self.assertEqual(guard.main(["check", "--url", url]), guard.EXIT_FAIL)

    def test_legal_url_passes(self) -> None:
        self.assertEqual(guard.main(["check", "--url", LOCAL_URL]), guard.EXIT_OK)


class TestDualArgPrecedence(unittest.TestCase):
    """W3R-01: --url is authoritative; mismatched --db-name is a hard FAIL."""

    def test_mismatched_db_name_and_url_fails(self) -> None:
        rc = guard.main(
            ["check", "--db-name", "astra_week3_demo", "--url", LOCAL_URL_OTHER]
        )
        self.assertEqual(rc, guard.EXIT_FAIL)

    def test_mismatched_db_name_and_prod_url_fails(self) -> None:
        rc = guard.main(
            [
                "check",
                "--db-name",
                "astra_week3_demo",
                "--url",
                "postgresql://app:pw@prod.rds.amazonaws.com:5432/production_db",
            ]
        )
        self.assertEqual(rc, guard.EXIT_FAIL)

    def test_url_production_db_with_legal_db_name_fails(self) -> None:
        rc = guard.main(
            [
                "check",
                "--db-name",
                "astra_week3_demo",
                "--url",
                "postgresql+asyncpg://u:p@localhost:5432/production_db",
            ]
        )
        self.assertEqual(rc, guard.EXIT_FAIL)

    def test_url_blog_db_with_legal_db_name_fails(self) -> None:
        rc = guard.main(
            [
                "check",
                "--db-name",
                "astra_week3_demo",
                "--url",
                "postgresql+asyncpg://u:p@localhost:5432/blog_db",
            ]
        )
        self.assertEqual(rc, guard.EXIT_FAIL)

    def test_url_blog_v2_with_legal_db_name_fails(self) -> None:
        rc = guard.main(
            [
                "check",
                "--db-name",
                "astra_week3_demo",
                "--url",
                "postgresql+asyncpg://u:p@localhost:5432/blog_v2",
            ]
        )
        self.assertEqual(rc, guard.EXIT_FAIL)

    def test_matching_db_name_and_url_passes_with_url_name(self) -> None:
        rc = guard.main(
            ["check", "--db-name", "astra_week3_other", "--url", LOCAL_URL_OTHER]
        )
        self.assertEqual(rc, guard.EXIT_OK)

    def test_url_name_is_authoritative_when_db_name_absent(self) -> None:
        rc = guard.main(["check", "--url", LOCAL_URL_OTHER])
        self.assertEqual(rc, guard.EXIT_OK)

    def test_run_injects_only_the_validated_url(self) -> None:
        env = dict(os.environ)
        env.pop(guard.ENV_DATABASE_URL, None)
        proc = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "run",
                "--db-name",
                "astra_week3_other",
                "--url",
                LOCAL_URL_OTHER,
                "--",
                "python3",
                "-c",
                "import os; print('CHILD_DSN', os.environ.get('DATABASE_URL',''))",
            ],
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )
        self.assertEqual(proc.returncode, 0)
        self.assertIn("CHILD_DSN", proc.stdout)
        self.assertIn(LOCAL_URL_OTHER, proc.stdout)
        self.assertNotIn("astra_week3_demo", proc.stdout.split("CHILD_DSN", 1)[-1])

    def test_run_does_not_execute_child_on_mismatch(self) -> None:
        env = dict(os.environ)
        env.pop(guard.ENV_DATABASE_URL, None)
        proc = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "run",
                "--db-name",
                "astra_week3_demo",
                "--url",
                LOCAL_URL_OTHER,
                "--",
                "echo",
                "SHOULD_NOT_RUN",
            ],
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )
        self.assertEqual(proc.returncode, 1)
        self.assertNotIn("SHOULD_NOT_RUN", proc.stdout)
        self.assertIn("child command NOT executed", proc.stdout)

    def test_run_does_not_execute_child_on_prod_url(self) -> None:
        env = dict(os.environ)
        env.pop(guard.ENV_DATABASE_URL, None)
        proc = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "run",
                "--db-name",
                "astra_week3_demo",
                "--url",
                "postgresql://app:pw@prod.rds.amazonaws.com:5432/production_db",
                "--",
                "echo",
                "SHOULD_NOT_RUN",
            ],
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )
        self.assertEqual(proc.returncode, 1)
        self.assertNotIn("SHOULD_NOT_RUN", proc.stdout)


class TestHostAllowlist(unittest.TestCase):
    """W3R-02: fail-closed local host allowlist unless --allow-remote-host."""

    def test_remote_host_without_flag_fails(self) -> None:
        self.assertEqual(guard.main(["check", "--url", REMOTE_SCRATCH_URL]), guard.EXIT_FAIL)

    def test_remote_host_with_flag_passes_when_name_legal(self) -> None:
        rc = guard.main(["check", "--url", REMOTE_SCRATCH_URL, "--allow-remote-host"])
        self.assertEqual(rc, guard.EXIT_OK)

    def test_remote_host_with_flag_warns_on_stderr(self) -> None:
        import contextlib
        import io

        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            rc = guard.main(["check", "--url", REMOTE_SCRATCH_URL, "--allow-remote-host"])
        self.assertEqual(rc, guard.EXIT_OK)
        self.assertIn("WARNING", stderr.getvalue())
        self.assertIn("db.internal", stderr.getvalue())

    def test_remote_host_with_flag_still_rejects_illegal_name(self) -> None:
        url = "postgresql+asyncpg://u:p@db.internal:5432/production_db"
        rc = guard.main(["check", "--url", url, "--allow-remote-host"])
        self.assertEqual(rc, guard.EXIT_FAIL)

    def test_local_hosts_pass_without_flag(self) -> None:
        for host in ("localhost", "127.0.0.1"):
            url = f"postgresql+asyncpg://u:p@{host}:5432/astra_week3_demo"
            with self.subTest(host=host):
                self.assertEqual(guard.main(["check", "--url", url]), guard.EXIT_OK)

    def test_ipv6_loopback_passes_without_flag(self) -> None:
        url = "postgresql+asyncpg://u:p@[::1]:5432/astra_week3_demo"
        self.assertEqual(guard.main(["check", "--url", url]), guard.EXIT_OK)

    def test_db_name_only_stays_local_and_passes(self) -> None:
        self.assertEqual(guard.main(["check", "--db-name", "astra_week3_demo"]), guard.EXIT_OK)

    def test_run_does_not_execute_child_on_remote_host_without_flag(self) -> None:
        env = dict(os.environ)
        env.pop(guard.ENV_DATABASE_URL, None)
        proc = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "run",
                "--url",
                REMOTE_SCRATCH_URL,
                "--",
                "echo",
                "SHOULD_NOT_RUN",
            ],
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )
        self.assertEqual(proc.returncode, 1)
        self.assertNotIn("SHOULD_NOT_RUN", proc.stdout)


class TestValidateTargetUnit(unittest.TestCase):
    def test_validate_target_raises_guard_error_on_blog_db(self) -> None:
        with self.assertRaises(guard.GuardError):
            guard.validate_target(db_name="blog_db", url=None, source="explicit:--db-name")

    def test_validate_target_raises_on_url_substring(self) -> None:
        with self.assertRaises(guard.GuardError):
            guard.validate_target(
                db_name="astra_week3_ok",
                url="postgresql+asyncpg://u:p@h:5432/blog_v2",
                source="explicit:--url",
            )

    def test_validate_target_prefers_url_name_over_db_name(self) -> None:
        with self.assertRaises(guard.GuardError):
            guard.validate_target(
                db_name="astra_week3_demo",
                url="postgresql+asyncpg://u:p@localhost:5432/production_db",
                source="explicit:--url",
            )

    def test_validate_target_requires_url_name_match(self) -> None:
        with self.assertRaises(guard.GuardError):
            guard.validate_target(
                db_name="astra_week3_a",
                url="postgresql+asyncpg://u:p@localhost:5432/astra_week3_b",
                source="explicit:--url",
            )

    def test_validate_target_accepts_matching_pair(self) -> None:
        name = guard.validate_target(
            db_name="astra_week3_demo",
            url=LOCAL_URL,
            source="explicit:--url",
        )
        self.assertEqual(name, "astra_week3_demo")

    def test_validate_target_rejects_remote_host_by_default(self) -> None:
        with self.assertRaises(guard.GuardError):
            guard.validate_target(
                db_name=None,
                url=REMOTE_SCRATCH_URL,
                source="explicit:--url",
            )

    def test_validate_target_accepts_remote_host_with_flag(self) -> None:
        name = guard.validate_target(
            db_name=None,
            url=REMOTE_SCRATCH_URL,
            source="explicit:--url",
            allow_remote_host=True,
        )
        self.assertEqual(name, "astra_week3_demo")


class TestRunSubcommand(unittest.TestCase):
    def test_run_does_not_execute_child_on_fail(self) -> None:
        marker = os.environ.get("WEEK3_GUARD_CHILD_RAN", "")
        env = dict(os.environ)
        env.pop(guard.ENV_DATABASE_URL, None)
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), "run", "--db-name", "blog_db", "--", "echo", "SHOULD_NOT_RUN"],
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )
        self.assertEqual(proc.returncode, 1)
        self.assertNotIn("SHOULD_NOT_RUN", proc.stdout)
        self.assertIn("child command NOT executed", proc.stdout)
        self.assertEqual(marker, os.environ.get("WEEK3_GUARD_CHILD_RAN", ""))

    def test_run_executes_child_on_pass(self) -> None:
        env = dict(os.environ)
        env.pop(guard.ENV_DATABASE_URL, None)
        proc = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "run",
                "--db-name",
                "astra_week3_demo",
                "--",
                "python3",
                "-c",
                "import os; print('CHILD_RAN', os.environ.get('DATABASE_URL',''))",
            ],
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )
        self.assertEqual(proc.returncode, 0)
        self.assertIn("CHILD_RAN", proc.stdout)
        self.assertIn("astra_week3_demo", proc.stdout)

    def test_run_without_child_command_fails(self) -> None:
        self.assertEqual(guard.main(["run", "--db-name", "astra_week3_demo"]), guard.EXIT_FAIL)


if __name__ == "__main__":
    unittest.main(verbosity=2)
