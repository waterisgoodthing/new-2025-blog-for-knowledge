import tempfile
import unittest
from pathlib import Path

from app.services.local_music_source import find_local_music_source


class LocalMusicSourceTest(unittest.TestCase):
    def test_selects_one_audio_file_deterministically_and_warns_about_extras(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp)
            (source / "b-track.mp3").write_bytes(b"fake")
            (source / "a-track.m4a").write_bytes(b"fake")
            (source / "notes.txt").write_text("ignore me", encoding="utf-8")

            result = find_local_music_source(source, public_prefix="/mymusic")

        self.assertTrue(result.exists)
        self.assertEqual(result.track["title"], "a-track")
        self.assertEqual(result.track["preview_url"], "/mymusic/a-track.m4a")
        self.assertIn("检测到多个音频文件", result.warnings[0])

    def test_reports_missing_audio_without_creating_placeholder_track(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = find_local_music_source(Path(tmp), public_prefix="/mymusic")

        self.assertFalse(result.exists)
        self.assertIsNone(result.track)
        self.assertIn("未找到音频文件", result.warnings[0])


if __name__ == "__main__":
    unittest.main()
