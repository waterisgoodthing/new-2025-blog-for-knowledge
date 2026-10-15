"""Fail-closed command runner for LSR-03's one-time local PostgreSQL only.

Every database-touching command in this rehearsal must be launched through
this module. URL credentials are accepted for the driver but never printed.
"""

from __future__ import annotations

import argparse
import asyncio
import os
from dataclasses import dataclass
from pathlib import Path
from subprocess import run
import sys
from urllib.parse import SplitResult, urlsplit

class GuardError(RuntimeError):
    """The command would leave the explicitly isolated database boundary."""


def project_backend_root() -> Path:
    return Path(__file__).resolve().parents[1]


def project_python_executable() -> Path:
    return project_backend_root() / ".venv/bin/python"


def require_project_runtime() -> Path:
    expected_venv = (project_backend_root() / ".venv").resolve()
    prefix = Path(sys.prefix).resolve()
    executable = Path(sys.executable).absolute()
    if prefix != expected_venv or expected_venv not in executable.parents:
        raise GuardError("LSR03_PYTHON_RUNTIME_REQUIRED")
    return expected_venv


@dataclass(frozen=True)
class IsolatedURL:
    raw: str
    scheme: str
    username: str | None
    password: str | None
    host: str
    port: int
    database: str


def _split(raw: str) -> SplitResult:
    if not raw or "\n" in raw or "\r" in raw:
        raise GuardError("LSR03_DATABASE_URL is required")
    parsed = urlsplit(raw)
    if parsed.scheme != "postgresql+asyncpg":
        raise GuardError("LSR03_DATABASE_URL_ASYNCPG_SCHEME_REQUIRED")
    if parsed.hostname != "127.0.0.1":
        raise GuardError("LSR03 database host must be 127.0.0.1")
    if parsed.port != 55432:
        raise GuardError("LSR03 database port must be 55432")
    if not parsed.path.startswith("/lsr03_"):
        raise GuardError("LSR03 database name must start with lsr03_")
    database = parsed.path[1:]
    if database in {"blog_v2", "postgres", "template0", "template1"}:
        raise GuardError("production/default database is forbidden")
    if not database or "/" in database:
        raise GuardError("invalid isolated database name")
    if parsed.query or parsed.fragment:
        raise GuardError("URL query/fragment is not allowed")
    return parsed


def parse_isolated_url(raw: str) -> IsolatedURL:
    parsed = _split(raw)
    return IsolatedURL(
        raw=raw,
        scheme=parsed.scheme,
        username=parsed.username,
        password=parsed.password,
        host=parsed.hostname or "",
        port=parsed.port or 0,
        database=parsed.path[1:],
    )


def guarded_environment(source: dict[str, str] | None = None) -> dict[str, str]:
    env = dict(os.environ if source is None else source)
    raw = env.get("LSR03_DATABASE_URL", "")
    parsed = parse_isolated_url(raw)
    inherited = env.get("DATABASE_URL")
    if inherited and inherited != raw:
        raise GuardError("conflicting DATABASE_URL is forbidden")
    # Explicitly pin every child database convention to the already parsed URL.
    env["LSR03_DATABASE_URL"] = parsed.raw
    env["DATABASE_URL"] = parsed.raw
    env["PGHOST"] = parsed.host
    env["PGPORT"] = str(parsed.port)
    env["PGDATABASE"] = parsed.database
    if parsed.username:
        env["PGUSER"] = parsed.username
    env["LSR03_LOG_PREFIX"] = f"lsr03:{parsed.database}@{parsed.host}:{parsed.port}"
    return env


async def identity_probe(database_url: str) -> dict[str, object]:
    require_project_runtime()
    from sqlalchemy import text
    from sqlalchemy.ext.asyncio import create_async_engine

    parsed = parse_isolated_url(database_url)
    # The guard accepts the psql-compatible ``postgresql`` spelling, but the
    # runner's probe is async SQLAlchemy and must select its installed driver.
    probe_url = parsed.raw.replace("postgresql://", "postgresql+asyncpg://", 1)
    engine = create_async_engine(probe_url, poolclass=None)
    try:
        async with engine.connect() as connection:
            await connection.execute(text("SET SESSION CHARACTERISTICS AS TRANSACTION READ ONLY"))
            row = (await connection.execute(text("""
              SELECT current_database() AS database,
                     inet_server_addr()::text AS server_addr,
                     inet_server_port() AS server_port,
                     pg_is_in_recovery() AS recovery,
                     current_user AS current_user,
                     session_user AS session_user
            """))).mappings().one()
        if row["database"] != parsed.database or row["server_addr"] not in {"127.0.0.1", "127.0.0.1/32", "::1", "::1/128"}:
            raise GuardError(
                f"identity probe database/address mismatch: database={row['database']} address={row['server_addr']}"
            )
        if row["server_port"] != 55432 or row["recovery"]:
            raise GuardError("identity probe port/recovery check failed")
        return dict(row)
    finally:
        await engine.dispose()


def _safe_probe_output(probe: dict[str, object]) -> str:
    return " ".join(f"{key}={probe[key]}" for key in ("database", "server_addr", "server_port", "recovery", "current_user", "session_user"))


def _validate_child_command(command: list[str]) -> None:
    expected = project_python_executable()
    if not command or Path(command[0]).absolute() != expected.absolute():
        raise GuardError("LSR03_PYTHON_RUNTIME_REQUIRED: child must use backend/.venv/bin/python")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--probe-only", action="store_true")
    parser.add_argument("--unit-only", action="store_true")
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)
    try:
        require_project_runtime()
        env = guarded_environment()
        if args.unit_only:
            command = list(args.command)
            if command and command[0] == "--":
                command = command[1:]
            _validate_child_command(command)
            if len(command) < 3 or command[1:3] != ["-m", "pytest"]:
                raise GuardError("LSR03_PYTHON_RUNTIME_REQUIRED: unit child must use -m pytest")
            env["PYTHONPATH"] = "."
            return run(command, cwd=project_backend_root(), env=env, check=False).returncode
        probe = asyncio.run(identity_probe(env["LSR03_DATABASE_URL"]))
        print(_safe_probe_output(probe), flush=True)
        if args.probe_only:
            return 0
        command = list(args.command)
        if command and command[0] == "--":
            command = command[1:]
        if not command:
            parser.error("a command is required unless --probe-only is used")
        _validate_child_command(command)
        env["PYTHONPATH"] = "."
        return run(command, cwd=project_backend_root(), env=env, check=False).returncode
    except GuardError as exc:
        print(f"LSR03_GUARD_ERROR: {exc}", file=sys.stderr)
        return 64


if __name__ == "__main__":
    raise SystemExit(main())
