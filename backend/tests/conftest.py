"""INC-02: protect every SQLAlchemy connection before DBAPI is invoked.

Installed when conftest loads, before importing collected test modules. No
legacy filename or marker releases: cleanup/rollback does not authorize writes
to blog_v2 or blog_db. DB suites must use an explicit local astra_week3_* target.
Pure unit tests do not need DATABASE_URL; in-memory SQLite remains available.
Raw driver/subprocess tools require their own explicit entry-point guard.
"""
from app.utils.scratch_db_safety import install_test_connection_guard

install_test_connection_guard()
