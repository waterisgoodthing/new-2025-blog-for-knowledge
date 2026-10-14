import os
import tempfile
import unittest
from pathlib import Path

from app.database import get_db
from app.utils.pending_files import track_pending_file


def _temp_path() -> Path:
    fd, name = tempfile.mkstemp()
    os.close(fd)
    path = Path(name)
    path.write_bytes(b"payload")
    return path


class PendingFileCleanupTest(unittest.IsolatedAsyncioTestCase):
    async def test_failed_commit_discards_written_file(self):
        path = _temp_path()
        self.assertTrue(path.exists())

        gen = get_db()
        session = await gen.__anext__()
        track_pending_file(session, path)

        with self.assertRaises(RuntimeError):
            await gen.athrow(RuntimeError("commit failed"))

        self.assertFalse(path.exists())

    async def test_successful_commit_keeps_written_file(self):
        path = _temp_path()
        try:
            gen = get_db()
            session = await gen.__anext__()
            track_pending_file(session, path)

            with self.assertRaises(StopAsyncIteration):
                await gen.asend(None)

            self.assertTrue(path.exists())
        finally:
            path.unlink(missing_ok=True)
