import tempfile
import unittest
from pathlib import Path

from app.services.local_music_source import (
    CLOUDFLARE_WORKERS_ASSET_LIMIT_BYTES,
    find_local_music_source,
    write_local_music_selection,
)


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
        self.assertIn("检测到多个音频文件", "\n".join(result.warnings))

    def test_selection_file_controls_active_track(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp)
            (source / "a-track.m4a").write_bytes(b"fake")
            (source / "b-track.mp3").write_bytes(b"fake")
            write_local_music_selection(source, "b-track.mp3")

            result = find_local_music_source(source, public_prefix="/mymusic")

        self.assertTrue(result.exists)
        self.assertEqual(result.selected_file, "b-track.mp3")
        self.assertEqual(result.track["title"], "b-track")
        self.assertEqual(result.track["preview_url"], "/mymusic/b-track.mp3")

    def test_invalid_selection_falls_back_with_warning(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp)
            (source / "a-track.m4a").write_bytes(b"fake")
            write_local_music_selection(source, "missing.mp3")

            result = find_local_music_source(source, public_prefix="/mymusic")

        self.assertTrue(result.exists)
        self.assertEqual(result.selected_file, "a-track.m4a")
        self.assertIn("选择的音源不存在", "\n".join(result.warnings))

    def test_oversized_file_is_reported_and_not_selected(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp)
            oversized = source / "big.wav"
            with oversized.open("wb") as file:
                file.truncate(CLOUDFLARE_WORKERS_ASSET_LIMIT_BYTES + 1)

            result = find_local_music_source(source, public_prefix="/mymusic")

        self.assertFalse(result.exists)
        self.assertIsNone(result.track)
        self.assertEqual(result.file_count, 1)
        self.assertEqual(result.deployable_file_count, 0)
        self.assertIn("超过 Cloudflare 25 MiB 限制", "\n".join(result.warnings))

    def test_reports_missing_audio_without_creating_placeholder_track(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = find_local_music_source(Path(tmp), public_prefix="/mymusic")

        self.assertFalse(result.exists)
        self.assertIsNone(result.track)
        self.assertIn("未找到音频文件", result.warnings[0])


if __name__ == "__main__":
    unittest.main()
