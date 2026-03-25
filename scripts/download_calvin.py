from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import subprocess
import sys
from urllib.request import Request, urlopen


URLS = {
    "debug": "http://calvin.cs.uni-freiburg.de/dataset/calvin_debug_dataset.zip",
    "D": "http://calvin.cs.uni-freiburg.de/dataset/task_D_D.zip",
    "ABC": "http://calvin.cs.uni-freiburg.de/dataset/task_ABC_D.zip",
    "ABCD": "http://calvin.cs.uni-freiburg.de/dataset/task_ABCD_D.zip",
}


def _head_size(url: str) -> int:
    req = Request(url, method="HEAD")
    with urlopen(req, timeout=30) as resp:
        return int(resp.headers.get("Content-Length", "0"))


def _human_gb(num_bytes: int) -> str:
    return f"{num_bytes / (1024 ** 3):.2f} GB"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download CALVIN dataset with resume support.")
    parser.add_argument("--split", choices=["debug", "D", "ABC", "ABCD"], required=True)
    parser.add_argument(
        "--output-dir",
        default="data/external/calvin",
        help="Directory to store zip files.",
    )
    parser.add_argument(
        "--extract",
        action="store_true",
        help="Extract zip after download using PowerShell Expand-Archive.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    url = URLS[args.split]
    zip_name = url.split("/")[-1]
    zip_path = output_dir / zip_name

    total_bytes = _head_size(url)
    print(f"[calvin] split={args.split} url={url}")
    print(f"[calvin] expected_size={_human_gb(total_bytes)}")
    print(f"[calvin] output={zip_path}")

    curl_path = shutil.which("curl.exe") or shutil.which("curl")
    if not curl_path:
        raise RuntimeError("curl is required but not found in PATH.")

    cmd = [curl_path, "-L", "-C", "-", "-o", str(zip_path), url]
    print(f"[calvin] running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)

    downloaded = zip_path.stat().st_size if zip_path.exists() else 0
    print(f"[calvin] downloaded={_human_gb(downloaded)}")

    if args.extract:
        # Use PowerShell Expand-Archive because Python's zip extraction is too slow for very large archives.
        ps_cmd = (
            f"$zip='{zip_path}'; $dst='{output_dir}'; "
            "Expand-Archive -Path $zip -DestinationPath $dst -Force"
        )
        subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_cmd],
            check=True,
        )
        print("[calvin] extraction completed")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("[calvin] interrupted, you can rerun the same command to resume.")
        sys.exit(130)
