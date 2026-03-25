# GitHub Issue Automation

Create issues from `docs/github_issue_seeds.md`.

## 1) Dry Run

```bash
python scripts/create_github_issues.py --repo Junxiong-Huang-VLA/generalist-vla-agent
```

This writes payload preview to:

- `outputs/reports/github_issue_payloads.json`

## 2) Apply (Create Issues)

Set token:

```bash
# PowerShell
$env:GITHUB_TOKEN="YOUR_TOKEN"
```

Create issues:

```bash
python scripts/create_github_issues.py --repo Junxiong-Huang-VLA/generalist-vla-agent --apply
```

Created issue summary:

- `outputs/reports/github_issues_created.json`
