import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path


SUPPORTED_AUDIO_EXTENSIONS = {".mp3", ".m4a", ".aac", ".ogg", ".opus", ".webm", ".wav"}
CLOUDFLARE_WORKERS_ASSET_LIMIT_BYTES = 25 * 1024 * 1024
SELECTION_FILE_NAME = "selection.json"


@dataclass(frozen=True)
class LocalMusicFile:
    name: str
    size_bytes: int
    supported: bool
    deployable: bool
    selected: bool
    reason: str | None = None


@dataclass(frozen=True)
class LocalMusicSourceStatus:
    source_dir: str
    public_prefix: str
    exists: bool
    file_count: int
    deployable_file_count: int
    selected_file: str | None
    configured_selected_file: str | None
    files: list[LocalMusicFile]
    warnings: list[str]
    track: dict | None


def _title_from_file(path: Path) -> str:
    return path.stem.strip() or path.stem


def _selection_path(source_dir: Path) -> Path:
    return source_dir / SELECTION_FILE_NAME


def read_local_music_selection(source_dir: Path) -> str | None:
    path = _selection_path(source_dir)
    if not path.exists():
        return None

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None

    selected = data.get("selected_file")
    if not isinstance(selected, str):
        return None

    selected = selected.strip()
    if not selected or selected != Path(selected).name:
        return None
    return selected


def write_local_music_selection(source_dir: Path, selected_file: str) -> None:
    selected_name = Path(selected_file).name
    if selected_name != selected_file or not selected_name:
        raise ValueError("selected_file must be a file name in public/mymusic")

    source_dir.mkdir(parents=True, exist_ok=True)
    _selection_path(source_dir).write_text(
        json.dumps({"selected_file": selected_name}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _file_status(path: Path, selected_file: str | None) -> LocalMusicFile:
    supported = path.suffix.lower() in SUPPORTED_AUDIO_EXTENSIONS
    size_bytes = path.stat().st_size
    reason = None

    if not supported:
        reason = "不支持的文件类型"
    elif size_bytes > CLOUDFLARE_WORKERS_ASSET_LIMIT_BYTES:
        reason = "超过 Cloudflare 25 MiB 限制"

    return LocalMusicFile(
        name=path.name,
        size_bytes=size_bytes,
        supported=supported,
        deployable=supported and reason is None,
        selected=selected_file == path.name,
        reason=reason,
    )


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
            deployable_file_count=0,
            selected_file=None,
            configured_selected_file=None,
            files=[],
            warnings=warnings,
            track=None,
        )

    configured_selected_file = read_local_music_selection(source_dir)
    all_files = sorted(
        path for path in source_dir.iterdir()
        if path.is_file() and path.name != SELECTION_FILE_NAME and not path.name.startswith(".")
    )
    file_statuses = [_file_status(path, configured_selected_file) for path in all_files]
    audio_files = [
        source_dir / file.name
        for file in file_statuses
        if file.supported
    ]
    deployable_files = [
        source_dir / file.name
        for file in file_statuses
        if file.deployable
    ]

    for file in file_statuses:
        if file.reason:
            warnings.append(f"{file.name}: {file.reason}")

    if not audio_files:
        warnings.append(f"未找到音频文件: {source_dir}")
        return LocalMusicSourceStatus(
            source_dir=str(source_dir),
            public_prefix=public_prefix,
            exists=False,
            file_count=0,
            deployable_file_count=0,
            selected_file=None,
            configured_selected_file=configured_selected_file,
            files=file_statuses,
            warnings=warnings,
            track=None,
        )

    selected = None
    if configured_selected_file:
        selected_path = source_dir / configured_selected_file
        configured_status = next((file for file in file_statuses if file.name == configured_selected_file), None)
        if configured_status and configured_status.deployable:
            selected = selected_path
        elif configured_status:
            warnings.append(f"选择的音源不可部署: {configured_selected_file}")
        else:
            warnings.append(f"选择的音源不存在: {configured_selected_file}")

    if selected is None and deployable_files:
        selected = deployable_files[0]

    if selected is None:
        warnings.append("未找到可部署的音频文件")
        return LocalMusicSourceStatus(
            source_dir=str(source_dir),
            public_prefix=public_prefix,
            exists=False,
            file_count=len(audio_files),
            deployable_file_count=0,
            selected_file=None,
            configured_selected_file=configured_selected_file,
            files=file_statuses,
            warnings=warnings,
            track=None,
        )

    if len(deployable_files) > 1 and configured_selected_file is None:
        warnings.append(f"检测到多个音频文件，将使用排序后的第一个: {selected.name}")

    file_statuses = [
        LocalMusicFile(
            name=file.name,
            size_bytes=file.size_bytes,
            supported=file.supported,
            deployable=file.deployable,
            selected=file.name == selected.name,
            reason=file.reason,
        )
        for file in file_statuses
    ]

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
        deployable_file_count=len(deployable_files),
        selected_file=selected.name,
        configured_selected_file=configured_selected_file,
        files=file_statuses,
        warnings=warnings,
        track=track,
    )
