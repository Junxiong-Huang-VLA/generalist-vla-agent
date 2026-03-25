from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from generalist_vla_agent.utils import restore_profile


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Restore configs from locked profile.")
    parser.add_argument("--profile-dir", default="configs/lock/default_weak_eval")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    restored = restore_profile(profile_dir=ROOT / args.profile_dir, root_dir=ROOT)
    print(f"restored_count={len(restored)}")
    for p in restored:
        print(p)


if __name__ == "__main__":
    main()
