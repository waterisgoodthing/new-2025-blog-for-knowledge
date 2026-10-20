"""Connection-free regression tests for INC-01/02 prevention."""
import os
import subprocess
import tempfile
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'backend'))


class DatabaseSafetyTests(unittest.TestCase):
    def test_protected_and_remote_targets_are_rejected(self):
        from app.utils.scratch_db_safety import require_scratch_database
        for url in (
            'postgresql://u:secret@localhost/blog_v2',
            'postgresql://u:secret@localhost/blog_db',
            'postgresql://u:secret@remote/astra_week3_ok',
            'postgresql://u:secret@localhost/astra_week3_ok?host=remote',
            'postgresql://u:secret@localhost/astra_week3_ok?dbname=blog_db',
            'postgresql://u:secret@localhost/',
        ):
            with self.subTest(url=url), self.assertRaises(RuntimeError) as error:
                require_scratch_database(url)
            self.assertNotIn('secret', str(error.exception))
        require_scratch_database('postgresql+asyncpg://u:p@localhost:5432/astra_week3_ok')

    def test_actual_connection_is_blocked_before_driver_even_with_overrides(self):
        from sqlalchemy import create_engine
        from sqlalchemy.ext.asyncio import create_async_engine
        from app.utils.scratch_db_safety import install_test_connection_guard
        install_test_connection_guard()
        for target, args in (
            ('postgresql+asyncpg://u:p@localhost/blog_v2', {}),
            ('postgresql+asyncpg://u:p@localhost/blog_db', {}),
            ('postgresql+asyncpg://u:p@localhost/astra_week3_ok', {'host': 'remote'}),
            ('postgresql+asyncpg://u:p@localhost/astra_week3_ok', {'hostaddr': '203.0.113.4'}),
            ('postgresql+asyncpg://u:p@localhost/astra_week3_ok', {'dbname': 'blog_db'}),
        ):
            engine = create_async_engine(target, connect_args=args).sync_engine
            with patch.object(engine.dialect, 'connect', side_effect=AssertionError('DBAPI reached')) as driver:
                with self.assertRaisesRegex(RuntimeError, 'before DBAPI'):
                    engine.connect()
                driver.assert_not_called()
            engine.dispose()

    def test_scratch_and_memory_connections_reach_driver(self):
        from sqlalchemy import create_engine
        from sqlalchemy.ext.asyncio import create_async_engine
        from app.utils.scratch_db_safety import install_test_connection_guard
        install_test_connection_guard()
        engine = create_async_engine('postgresql+asyncpg://u:p@localhost/astra_week3_ok').sync_engine
        with patch.object(engine.dialect, 'connect', side_effect=RuntimeError('driver sentinel')) as driver:
            with self.assertRaisesRegex(RuntimeError, 'driver sentinel'):
                engine.connect()
            driver.assert_called_once()
        engine.dispose()
        memory = create_engine('sqlite:///:memory:')
        with memory.connect() as connection:
            self.assertEqual(connection.exec_driver_sql('SELECT 1').scalar(), 1)
        memory.dispose()

    def test_migration_requires_exact_explicit_target_for_non_scratch(self):
        from app.utils.scratch_db_safety import require_migration_target
        url = 'postgresql+asyncpg://u:secret@localhost:5432/blog_v2'
        with self.assertRaises(RuntimeError):
            require_migration_target(url)
        with self.assertRaises(RuntimeError):
            require_migration_target(url, approved_target='localhost:5432/blog_db')
        require_migration_target(url, approved_target='localhost:5432/blog_v2')
        require_migration_target('postgresql+asyncpg://localhost/astra_week3_ok')

    def test_entry_points_reject_protected_target_without_network(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            sentinel = folder / 'network-attempt'
            (folder / 'sitecustomize.py').write_text(
                "import socket\nfrom pathlib import Path\n"
                "def deny(*args, **kwargs):\n"
                f"    Path({str(sentinel)!r}).write_text('attempted')\n"
                "    raise RuntimeError('NETWORK_ATTEMPT_FORBIDDEN')\n"
                "socket.socket.connect = deny\n"
                "socket.socket.connect_ex = deny\n"
            )
            environment = dict(os.environ, DATABASE_URL='postgresql+asyncpg://u:secret@localhost:1/blog_v2')
            environment.pop('BLOG_APPROVED_MIGRATION_TARGET', None)
            environment['PYTHONPATH'] = os.pathsep.join((temporary, str(root / 'backend')))
            commands = [
                [sys.executable, str(path)]
                for path in sorted((root / 'backend/tests').glob('_pr*_evidence*.py'))
            ]
            commands.append([sys.executable, '-m', 'alembic', 'upgrade', 'head'])
            # A DB connection during module import must be intercepted before collection.
            (folder / 'conftest.py').write_text((root / 'backend/tests/conftest.py').read_text())
            (folder / 'test_import.py').write_text(
                "from sqlalchemy.ext.asyncio import create_async_engine\n"
                "engine = create_async_engine('postgresql+asyncpg://u:secret@localhost:1/blog_v2')\n"
                "engine.sync_engine.connect()\n"
                "def test_unused(): pass\n"
            )
            commands.append([sys.executable, '-m', 'pytest', str(folder / 'test_import.py'), '-q'])
            for command in commands:
                with self.subTest(command=command):
                    result = subprocess.run(command, cwd=root / 'backend', env=environment,
                                            capture_output=True, text=True, timeout=20)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn('Database safety:', result.stderr + result.stdout)
                    self.assertFalse(sentinel.exists(), 'entry point attempted network access')
                    # pytest includes the synthetic test source in a traceback; do not
                    # print captured subprocess output, which can include that literal.

    def test_libpq_environment_cannot_redirect_scratch_or_approved_migration(self):
        from app.utils.scratch_db_safety import require_scratch_database, require_migration_target
        with patch.dict(os.environ, {'PGHOSTADDR': '203.0.113.4'}):
            with self.assertRaises(RuntimeError):
                require_scratch_database('postgresql://localhost/astra_week3_ok')
            with self.assertRaises(RuntimeError):
                require_migration_target('postgresql://localhost/blog_v2', approved_target='localhost:5432/blog_v2')


if __name__ == '__main__':
    unittest.main()
