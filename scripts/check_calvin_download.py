from __future__ import annotations

import argparse
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check current CALVIN zip download progress.")
    parser.add_argument("--zip-path", required=True)
    parser.add_argument("--total-bytes", type=int, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    zip_path = Path(args.zip_path)
    if not zip_path.exists():
        print("status=missing downloaded_bytes=0 progress=0.00%")
        return

    downloaded = zip_path.stat().st_size
    total = max(args.total_bytes, 1)
    progress = downloaded / total * 100.0
    print(
        f"status=downloading downloaded_bytes={downloaded} "
        f"downloaded_gb={downloaded / (1024**3):.2f} "
        f"total_gb={total / (1024**3):.2f} progress={progress:.2f}%"
    )


if __name__ == "__main__":
    main()
