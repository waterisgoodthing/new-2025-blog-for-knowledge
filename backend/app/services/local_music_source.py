from dataclasses import dataclass
from datetime import date
from pathlib import Path


SUPPORTED_AUDIO_EXTENSIONS = {".mp3", ".m4a", ".aac", ".ogg", ".opus", ".webm", ".wav"}


@dataclass(frozen=True)
class LocalMusicSourceStatus:
    source_dir: str
    public_prefix: str
    exists: bool
    file_count: int
    selected_file: str | None
    warnings: list[str]
    track: dict | None


def _title_from_file(path: Path) -> str:
    return path.stem.strip() or path.stem


def find_local_music_source(
    source_dir: Path,
    public_prefix: str = "/mymusic",
    target_date: date | None = None,
) -> LocalMusicSourceStatus:
    warnings: list[str] = []
    if target_date is None:
        target_date = date.today()

    if not source_dir.exists():
        warnings.append(f"音源目录不存在: {source_dir}")
        return LocalMusicSourceStatus(
            source_dir=str(source_dir),
            public_prefix=public_prefix,
            exists=False,
            file_count=0,
            selected_file=None,
            warnings=warnings,
            track=None,
        )

    audio_files = sorted(
        path for path in source_dir.iterdir()
        if path.is_file() and path.suffix.lower() in SUPPORTED_AUDIO_EXTENSIONS
    )
    if not audio_files:
        warnings.append(f"未找到音频文件: {source_dir}")
        return LocalMusicSourceStatus(
            source_dir=str(source_dir),
            public_prefix=public_prefix,
            exists=False,
            file_count=0,
            selected_file=None,
            warnings=warnings,
            track=None,
        )

    selected = audio_files[0]
    if len(audio_files) > 1:
        warnings.append(f"检测到多个音频文件，将使用排序后的第一个: {selected.name}")

    track = {
        "id": 1,
        "date": target_date.isoformat(),
        "title": _title_from_file(selected),
        "artist": None,
        "album": None,
        "artwork_url": None,
        "preview_url": f"{public_prefix.rstrip('/')}/{selected.name}",
        "netease_url": None,
        "recommendation_reason": None,
    }
    return LocalMusicSourceStatus(
        source_dir=str(source_dir),
        public_prefix=public_prefix,
        exists=True,
        file_count=len(audio_files),
        selected_file=selected.name,
        warnings=warnings,
        track=track,
    )
