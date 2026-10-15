import os
import importlib.util
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

from tests.lsr03_guarded_runner import (
    GuardError,
    guarded_environment,
    parse_isolated_url,
    project_python_executable,
    require_project_runtime,
)


ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "backend/tests/lsr03_guarded_runner.py"


def _non_project_python() -> str:
    expected = project_python_executable().resolve()
    candidates = [Path("/usr/bin/python3"), Path(shutil.which("python3") or "")]
    for candidate in candidates:
        if candidate and candidate.exists() and candidate.resolve() != expected:
            return str(candidate)
    pytest.skip("no non-project Python interpreter available")


def test_exact_isolated_url_is_accepted_without_connecting() -> None:
    parsed = parse_isolated_url(
        "postgresql+asyncpg://runner:secret@127.0.0.1:55432/lsr03_guard"
    )
    assert parsed.host == "127.0.0.1"
    assert parsed.port == 55432
    assert parsed.database == "lsr03_guard"


@pytest.mark.parametrize(
    "value",
    [
        "",
        "postgresql+asyncpg://runner@localhost:55432/lsr03_guard",
        "postgresql+asyncpg://runner@127.0.0.1:5432/lsr03_guard",
        "postgresql+asyncpg://runner@127.0.0.1:55432/blog_v2",
        "postgresql+asyncpg://runner@127.0.0.1:55432/postgres",
        "postgresql+asyncpg://runner@127.0.0.1:55432/template1",
        "postgresql+asyncpg:///lsr03_guard",
        "postgres://runner@127.0.0.1:55432/lsr03_guard",
    ],
)
def test_rejects_non_isolated_url(value: str) -> None:
    with pytest.raises(GuardError):
        parse_isolated_url(value)


def test_missing_and_conflicting_environment_are_rejected() -> None:
    with pytest.raises(GuardError, match="LSR03_DATABASE_URL"):
        guarded_environment({})
    with pytest.raises(GuardError, match="DATABASE_URL"):
        guarded_environment(
            {
                "LSR03_DATABASE_URL": "postgresql+asyncpg://runner@127.0.0.1:55432/lsr03_guard",
                "DATABASE_URL": "postgresql+asyncpg://blog_user@127.0.0.1:5432/blog_v2",
            }
        )


def test_child_environment_contains_only_explicit_isolated_url() -> None:
    env = guarded_environment(
        {
            "LSR03_DATABASE_URL": "postgresql+asyncpg://runner:secret@127.0.0.1:55432/lsr03_guard",
            "DATABASE_URL": "",
        }
    )
    assert env["DATABASE_URL"] == env["LSR03_DATABASE_URL"]
    assert "secret" not in env.get("LSR03_LOG_PREFIX", "")


def test_asyncpg_is_available_and_psycopg2_is_not_a_runtime_fallback() -> None:
    assert importlib.util.find_spec("asyncpg") is not None
    assert importlib.util.find_spec("psycopg2") is None


def test_plain_postgresql_scheme_fails_before_probe_and_child() -> None:
    env = dict(os.environ)
    env["LSR03_DATABASE_URL"] = "postgresql://runner@127.0.0.1:55432/lsr03_guard"
    env["DATABASE_URL"] = env["LSR03_DATABASE_URL"]
    python = str(project_python_executable())
    result = subprocess.run(
        [
            python,
            str(RUNNER),
            "--unit-only",
            "--",
            python,
            "-m",
            "pytest",
            "-q",
        ],
        cwd=ROOT / "backend",
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 64
    assert "LSR03_DATABASE_URL_ASYNCPG_SCHEME_REQUIRED" in result.stderr
    assert "collected" not in result.stdout


def test_wrong_interpreter_fails_before_probe_and_child() -> None:
    wrong_python = _non_project_python()
    env = dict(os.environ)
    env["LSR03_DATABASE_URL"] = "postgresql+asyncpg://runner@127.0.0.1:55432/lsr03_guard"
    env["DATABASE_URL"] = env["LSR03_DATABASE_URL"]
    result = subprocess.run(
        [
            wrong_python,
            str(RUNNER),
            "--unit-only",
            "--",
            wrong_python,
            "-c",
            "print('CHILD_MUST_NOT_RUN')",
        ],
        cwd=ROOT / "backend",
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 64
    assert "LSR03_PYTHON_RUNTIME_REQUIRED" in result.stderr
    assert "CHILD_MUST_NOT_RUN" not in result.stdout


def test_private_project_runtime_is_the_only_runtime() -> None:
    expected = project_python_executable().resolve()
    assert expected == (ROOT / "backend/.venv/bin/python").resolve()
    assert require_project_runtime() == (ROOT / "backend/.venv").resolve()
