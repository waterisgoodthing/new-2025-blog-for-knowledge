"""Database safety for verification tools; never installed by the web app."""
from __future__ import annotations

import os
import re

from sqlalchemy import event
from sqlalchemy.engine import Engine, make_url

_SCRATCH = re.compile(r'astra_week[34]_[a-z0-9_]+')
_LOCAL = {'localhost', '127.0.0.1', '::1'}
_REDIRECT_ENV = ('PGHOSTADDR', 'PGSERVICE', 'PGSERVICEFILE', 'PGOPTIONS')


def require_scratch_database(target) -> None:
    """Reject ambiguous/non-local targets without disclosing credentials."""
    try:
        url = make_url(target)
    except Exception:
        raise RuntimeError('Database safety: invalid target') from None
    if (
        url.get_backend_name() != 'postgresql'
        or not _SCRATCH.fullmatch(url.database or '')
        or url.host not in _LOCAL
        or url.query
        or any(os.environ.get(key) for key in _REDIRECT_ENV)
    ):
        raise RuntimeError(
            'Database safety: verification requires a local astra_week3_* or '
            'astra_week4_* database with no connection query overrides; '
            'protected target refused'
        )


def install_test_connection_guard() -> None:
    """Guard actual engine connections before DBAPI, including collection time.

    No filename/marker exemptions. SQLite in-memory unit tests remain usable.
    SQLAlchemy async engines delegate connections through the sync Engine event.
    """
    if not event.contains(Engine, 'do_connect', _guard_connection):
        event.listen(Engine, 'do_connect', _guard_connection)


def _guard_connection(dialect, connection_record, connection_args, connection_params):
    if dialect.name == 'sqlite':
        # File-backed SQLite can mutate unrelated local data too.
        if connection_args and connection_args[0] == ':memory:':
            return
        raise RuntimeError('Database safety: only in-memory SQLite is allowed in tests')
    # Inspect final DBAPI parameters, so URLs and connect_args cannot disagree.
    if (
        dialect.name != 'postgresql'
        or connection_params.get('host') not in _LOCAL
        or not _SCRATCH.fullmatch(
            connection_params.get('database', connection_params.get('dbname', '')) or ''
        )
        or ('dbname' in connection_params and not _SCRATCH.fullmatch(connection_params['dbname'] or ''))
        or any(key in connection_params for key in ('hostaddr', 'service', 'servicefile', 'options', 'dsn'))
        or any(os.environ.get(key) for key in _REDIRECT_ENV)
    ):
        raise RuntimeError('Database safety: non-scratch connection refused before DBAPI')


def require_migration_target(target, *, approved_target: str | None = None) -> None:
    """Non-scratch migrations need a separately authorized exact target opt-in.

    The opt-in is an operational confirmation, never evidence of user approval.
    Query overrides are refused even with opt-in because they can redirect libpq.
    """
    try:
        require_scratch_database(target)
        return
    except RuntimeError:
        pass
    try:
        url = make_url(target)
        identity = f'{url.host}:{url.port or 5432}/{url.database}'
        valid = (
            url.get_backend_name() == 'postgresql'
            and url.host and url.database and not url.query
            and not any(os.environ.get(key) for key in _REDIRECT_ENV)
            and approved_target == identity
        )
    except Exception:
        valid = False
    if not valid:
        raise RuntimeError(
            'Database safety: non-scratch migration refused. After separate user '
            'authorization, set BLOG_APPROVED_MIGRATION_TARGET to the exact '
            'host:port/database for this invocation; never persist it in .env.'
        )
