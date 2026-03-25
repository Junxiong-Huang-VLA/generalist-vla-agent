from __future__ import annotations

from datetime import datetime
import hashlib
import json
from pathlib import Path


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fp:
        while True:
            chunk = fp.read(1024 * 1024)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def snapshot_profile(
    files: list[Path],
    profile_dir: Path,
    root_dir: Path,
) -> Path:
    profile_dir.mkdir(parents=True, exist_ok=True)
    entries: list[dict] = []
    for src in files:
        abs_src = (root_dir / src).resolve() if not src.is_absolute() else src.resolve()
        rel = abs_src.relative_to(root_dir.resolve())
        dst = profile_dir / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(abs_src.read_bytes())
        entries.append(
            {
                "path": rel.as_posix(),
                "sha256": _sha256(abs_src),
                "bytes": abs_src.stat().st_size,
            }
        )

    manifest = {
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "root_dir": str(root_dir.resolve()),
        "files": entries,
    }
    manifest_path = profile_dir / "manifest.json"
    with manifest_path.open("w", encoding="utf-8") as fp:
        json.dump(manifest, fp, ensure_ascii=True, indent=2)
    return manifest_path


def restore_profile(profile_dir: Path, root_dir: Path) -> list[Path]:
    manifest_path = profile_dir / "manifest.json"
    with manifest_path.open("r", encoding="utf-8") as fp:
        manifest = json.load(fp)

    restored: list[Path] = []
    for entry in manifest.get("files", []):
        rel = Path(entry["path"])
        src = profile_dir / rel
        dst = root_dir / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(src.read_bytes())
        restored.append(dst)
    return restored
