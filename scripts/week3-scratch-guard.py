#!/usr/bin/env python3
"""Week 3 scratch-only database guard runner (W3-00).

Guards every SQL / alembic action behind an allowlist check so Week 3 work can
only touch task-specific scratch databases named ``astra_week3_*``.

Safety rules (all enforced BEFORE any child command runs):

1. The target database name is always taken from the connection string that
   will actually be used (``--url`` when present, else ``DATABASE_URL``, else
   the name derived from ``--db-name``). That name must match
   ``^astra_week3_[a-z0-9_]+$``.
2. ``blog_db``, ``blog_v2`` and any non-allowlisted name are rejected.
3. When both ``--db-name`` and ``--url`` are given, the name parsed from
   ``--url`` is authoritative. If ``--db-name`` disagrees with it the run is
   rejected outright (ambiguous target).
4. If the URL is taken heuristically from the environment variable
   ``DATABASE_URL`` (the default ``.env`` path), it is rejected whenever its
   database name is not on the allowlist. Explicit ``--db-name`` / ``--url``
   is the sanctioned way to name the target.
5. Empty names are rejected. Any URL containing the substrings ``blog_db`` or
   ``blog_v2`` is rejected outright.
6. Host allowlist (fail-closed): only ``localhost``, ``127.0.0.1`` and ``::1``
   are accepted by default. Any other host requires an explicit
   ``--allow-remote-host`` flag and emits a stderr warning when used.

Usage:

    python3 scripts/week3-scratch-guard.py check --db-name astra_week3_demo
    python3 scripts/week3-scratch-guard.py check --url postgresql+asyncpg://localhost:5432/astra_week3_pr09
    python3 scripts/week3-scratch-guard.py run --db-name astra_week3_pr09 -- alembic upgrade head

``check`` prints PASS/FAIL and exits 0/1. ``run`` validates first and only
then executes the child command with ``DATABASE_URL`` set in its environment;
on validation failure the child command is never executed and the runner
exits 1. The injected ``DATABASE_URL`` is always the validated URL/DSN.

When only ``--db-name`` is given, the child ``DATABASE_URL`` is built as a
local scratch DSN ``postgresql+asyncpg://localhost:5432/<db_name>`` so the
runner never inherits a production host or credentials implicitly. Pass
``--url`` explicitly when a different host/credential set is required.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from urllib.parse import urlparse

ALLOWLIST_PATTERN = re.compile(r"^astra_week3_[a-z0-9_]+$")
FORBIDDEN_SUBSTRINGS = ("blog_db", "blog_v2")
ENV_DATABASE_URL = "DATABASE_URL"
LOCAL_SCRATCH_DSN_TEMPLATE = "postgresql+asyncpg://localhost:5432/{db_name}"
ALLOWED_HOSTS = frozenset({"localhost", "127.0.0.1", "::1"})

EXIT_OK = 0
EXIT_FAIL = 1


class GuardError(Exception):
    """Validation failure with a human-readable reason."""


def db_name_from_url(url: str) -> str:
    """Extract the database name (last path segment) from a DSN."""
    parsed = urlparse(url)
    path = parsed.path or ""
    return path.lstrip("/").split("/")[0]


def host_from_url(url: str) -> str | None:
    """Extract the hostname from a DSN, or None when it cannot be resolved."""
    return urlparse(url).hostname


def check_host(url: str, *, allow_remote_host: bool, source: str) -> None:
    """Enforce the fail-closed host allowlist; raise GuardError on violation."""
    host = host_from_url(url)
    if host is None:
        raise GuardError(f"cannot resolve hostname from URL (source={source})")
    if host in ALLOWED_HOSTS:
        return
    if not allow_remote_host:
        raise GuardError(
            f"host {host!r} is not in the local allowlist "
            f"{sorted(ALLOWED_HOSTS)}; pass --allow-remote-host to override "
            f"(source={source})"
        )
    print(
        f"WARNING: --allow-remote-host permits non-local host {host!r} "
        f"(source={source})",
        file=sys.stderr,
    )


def validate_target(
    *,
    db_name: str | None,
    url: str | None,
    source: str,
    allow_remote_host: bool = False,
) -> str:
    """Return the validated database name or raise GuardError.

    The effective name is always derived from ``url`` when a URL is the
    connection string that will actually be used. ``db_name`` is only
    authoritative when no URL is supplied; when both are supplied they must
    agree or the target is rejected as ambiguous.

    ``source`` is informational (``explicit`` or ``env:DATABASE_URL``) and is
    used to reject heuristic ``.env`` URLs that point outside the allowlist.
    """
    if url is not None:
        for needle in FORBIDDEN_SUBSTRINGS:
            if needle in url:
                raise GuardError(
                    f"URL contains forbidden substring {needle!r} (source={source})"
                )
        effective_name = db_name_from_url(url)
        if db_name is not None and db_name != effective_name:
            raise GuardError(
                f"ambiguous target: --db-name={db_name!r} disagrees with the "
                f"database name {effective_name!r} parsed from the connection "
                f"URL (source={source})"
            )
    else:
        effective_name = db_name

    if effective_name is None or effective_name == "":
        raise GuardError(f"empty database name (source={source})")

    for needle in FORBIDDEN_SUBSTRINGS:
        if needle in effective_name:
            raise GuardError(
                f"database name contains forbidden substring {needle!r} (source={source})"
            )

    if not ALLOWLIST_PATTERN.match(effective_name):
        if source.startswith("env"):
            raise GuardError(
                f"database name {effective_name!r} from environment {ENV_DATABASE_URL} "
                f"is not on the astra_week3_* allowlist; pass --db-name/--url "
                f"explicitly (source={source})"
            )
        raise GuardError(
            f"database name {effective_name!r} does not match allowlist "
            f"^astra_week3_[a-z0-9_]+$ (source={source})"
        )

    if url is not None:
        check_host(url, allow_remote_host=allow_remote_host, source=source)

    return effective_name


def resolve_target(
    db_name_arg: str | None,
    url_arg: str | None,
    *,
    allow_remote_host: bool = False,
) -> tuple[str, str, str]:
    """Resolve (db_name, url_for_child, source) from CLI args or environment.

    ``url_for_child`` is the only DSN ever injected into a child process and
    always corresponds to the validated target.
    """
    if url_arg is not None:
        name = validate_target(
            db_name=db_name_arg,
            url=url_arg,
            source="explicit:--url",
            allow_remote_host=allow_remote_host,
        )
        return name, url_arg, "explicit:--url"

    if db_name_arg is not None:
        name = validate_target(
            db_name=db_name_arg,
            url=None,
            source="explicit:--db-name",
            allow_remote_host=allow_remote_host,
        )
        dsn = LOCAL_SCRATCH_DSN_TEMPLATE.format(db_name=name)
        return name, dsn, "explicit:--db-name"

    env_url = os.environ.get(ENV_DATABASE_URL, "")
    if env_url == "":
        raise GuardError(
            f"no --db-name/--url given and environment {ENV_DATABASE_URL} is unset"
        )
    name = validate_target(
        db_name=None,
        url=env_url,
        source=f"env:{ENV_DATABASE_URL}",
        allow_remote_host=allow_remote_host,
    )
    return name, env_url, f"env:{ENV_DATABASE_URL}"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="week3-scratch-guard",
        description="Scratch-only guard for Week 3 SQL/alembic actions (astra_week3_* allowlist).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    def add_target_args(p: argparse.ArgumentParser) -> None:
        p.add_argument(
            "--db-name",
            dest="db_name",
            default=None,
            help="explicit scratch database name (must match ^astra_week3_[a-z0-9_]+$)",
        )
        p.add_argument(
            "--url",
            dest="url",
            default=None,
            help="explicit scratch database URL (name inside must match the allowlist)",
        )
        p.add_argument(
            "--allow-remote-host",
            dest="allow_remote_host",
            action="store_true",
            help="permit a non-local host in --url (warns on stderr; default is local-only)",
        )

    check = sub.add_parser("check", help="validate the target and print PASS/FAIL")
    add_target_args(check)

    run = sub.add_parser(
        "run",
        help="validate, then run a child command with DATABASE_URL set",
    )
    add_target_args(run)
    run.add_argument(
        "child",
        nargs=argparse.REMAINDER,
        help="command to execute after validation (prefix with --)",
    )
    return parser


def run_check(db_name_arg: str | None, url_arg: str | None, *, allow_remote_host: bool) -> int:
    try:
        name, _dsn, source = resolve_target(
            db_name_arg, url_arg, allow_remote_host=allow_remote_host
        )
    except GuardError as exc:
        print(f"FAIL: {exc}")
        return EXIT_FAIL
    print(f"PASS: db_name={name!r} source={source}")
    return EXIT_OK


def run_guarded(
    db_name_arg: str | None,
    url_arg: str | None,
    child: list[str],
    *,
    allow_remote_host: bool,
) -> int:
    if child and child[0] == "--":
        child = child[1:]
    if not child:
        print("FAIL: run requires a child command after --")
        return EXIT_FAIL

    try:
        name, dsn, source = resolve_target(
            db_name_arg, url_arg, allow_remote_host=allow_remote_host
        )
    except GuardError as exc:
        print(f"FAIL: {exc}")
        print("child command NOT executed")
        return EXIT_FAIL

    print(f"PASS: db_name={name!r} source={source}; executing {child!r}")
    env = dict(os.environ)
    env[ENV_DATABASE_URL] = dsn
    completed = subprocess.run(child, env=env, check=False)
    return completed.returncode


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "check":
        return run_check(
            args.db_name, args.url, allow_remote_host=args.allow_remote_host
        )
    return run_guarded(
        args.db_name,
        args.url,
        args.child,
        allow_remote_host=args.allow_remote_host,
    )


if __name__ == "__main__":
    sys.exit(main())
