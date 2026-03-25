from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from generalist_vla_agent.utils import snapshot_profile


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Snapshot stable config profile.")
    parser.add_argument("--profile-dir", default="configs/lock/default_weak_eval")
    parser.add_argument(
        "--files",
        nargs="+",
        default=[
            "configs/base.yaml",
            "configs/eval.yaml",
            "configs/eval_trained.yaml",
            "configs/eval_temporal.yaml",
            "configs/eval_temporal_calvin_small.yaml",
            "configs/demo_release_small.yaml",
        ],
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    files = [Path(x) for x in args.files]
    manifest = snapshot_profile(files=files, profile_dir=ROOT / args.profile_dir, root_dir=ROOT)
    print(f"snapshot_manifest={manifest}")


if __name__ == "__main__":
    main()
