from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
from typing import Any
from urllib.request import Request, urlopen


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create GitHub issues from docs/github_issue_seeds.md")
    parser.add_argument("--repo", default="Junxiong-Huang-VLA/generalist-vla-agent")
    parser.add_argument("--seed-file", default="docs/github_issue_seeds.md")
    parser.add_argument("--token-env", default="GITHUB_TOKEN")
    parser.add_argument("--apply", action="store_true", help="Actually create issues on GitHub.")
    parser.add_argument("--output", default="outputs/reports/github_issue_payloads.json")
    return parser.parse_args()


def _extract_inline_code(text: str) -> str:
    m = re.search(r"`([^`]+)`", text)
    return m.group(1) if m else text.strip()


def parse_seed_markdown(path: Path) -> list[dict[str, Any]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    issues: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    in_done_when = False

    for raw in lines:
        line = raw.strip()
        if line.startswith("## "):
            if current:
                issues.append(current)
            current = {"section": line[3:].strip(), "title": "", "labels": [], "done_when": []}
            in_done_when = False
            continue
        if not current:
            continue
        if line.startswith("- **Title**:"):
            current["title"] = _extract_inline_code(line.split(":", 1)[1].strip())
            in_done_when = False
            continue
        if line.startswith("- **Labels**:"):
            label_part = line.split(":", 1)[1]
            labels = [x.strip(" `") for x in label_part.split(",") if x.strip()]
            current["labels"] = labels
            in_done_when = False
            continue
        if line.startswith("- **Done when**:"):
            in_done_when = True
            continue
        if in_done_when and line.startswith("-"):
            current["done_when"].append(line.lstrip("-").strip())
            continue
        if line == "":
            in_done_when = False

    if current:
        issues.append(current)

    payloads: list[dict[str, Any]] = []
    for issue in issues:
        body_lines = [
            f"Source section: **{issue['section']}**",
            "",
            "### Done when",
        ]
        body_lines.extend([f"- {item}" for item in issue["done_when"]])
        payloads.append(
            {
                "title": issue["title"],
                "labels": issue["labels"],
                "body": "\n".join(body_lines).strip(),
            }
        )
    return payloads


def create_issue(repo: str, token: str, payload: dict[str, Any]) -> dict[str, Any]:
    url = f"https://api.github.com/repos/{repo}/issues"
    data = json.dumps(payload).encode("utf-8")
    req = Request(url=url, data=data, method="POST")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("Content-Type", "application/json")
    with urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main() -> None:
    args = parse_args()
    payloads = parse_seed_markdown(Path(args.seed_file))

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payloads, ensure_ascii=True, indent=2), encoding="utf-8")
    print(f"prepared_payloads={len(payloads)} output={out}")

    if not args.apply:
        print("mode=dry_run (use --apply to create issues)")
        return

    token = os.getenv(args.token_env, "").strip()
    if not token:
        raise RuntimeError(f"Missing token env: {args.token_env}")

    created = []
    for payload in payloads:
        result = create_issue(args.repo, token, payload)
        created.append({"title": result.get("title"), "number": result.get("number"), "url": result.get("html_url")})
        print(f"created #{result.get('number')}: {result.get('title')}")

    summary_path = out.with_name("github_issues_created.json")
    summary_path.write_text(json.dumps(created, ensure_ascii=True, indent=2), encoding="utf-8")
    print(f"created_issues={len(created)} summary={summary_path}")


if __name__ == "__main__":
    main()
