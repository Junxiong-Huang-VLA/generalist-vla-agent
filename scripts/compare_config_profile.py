from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fp:
        while True:
            chunk = fp.read(1024 * 1024)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare current configs against a locked profile.")
    parser.add_argument("--profile-dir", default="configs/lock/default_weak_eval")
    parser.add_argument("--output", default=None, help="Optional json output path.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    profile_dir = ROOT / args.profile_dir
    manifest_path = profile_dir / "manifest.json"

    with manifest_path.open("r", encoding="utf-8") as fp:
        manifest = json.load(fp)

    baseline = {entry["path"]: entry["sha256"] for entry in manifest.get("files", [])}
    changed: list[str] = []
    missing: list[str] = []
    same: list[str] = []
    extra: list[str] = []

    for rel, expected_hash in baseline.items():
        path = ROOT / rel
        if not path.exists():
            missing.append(rel)
            continue
        current_hash = _sha256(path)
        if current_hash == expected_hash:
            same.append(rel)
        else:
            changed.append(rel)

    tracked = {Path(p).as_posix() for p in baseline.keys()}
    for cfg in (ROOT / "configs").glob("*.yaml"):
        rel = cfg.relative_to(ROOT).as_posix()
        if rel not in tracked:
            extra.append(rel)

    result = {
        "profile_dir": args.profile_dir,
        "same_count": len(same),
        "changed_count": len(changed),
        "missing_count": len(missing),
        "extra_count": len(extra),
        "changed": sorted(changed),
        "missing": sorted(missing),
        "extra": sorted(extra),
    }

    print(json.dumps(result, ensure_ascii=True, indent=2))
    if args.output:
        out = ROOT / args.output
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("w", encoding="utf-8") as fp:
            json.dump(result, fp, ensure_ascii=True, indent=2)


if __name__ == "__main__":
    main()
