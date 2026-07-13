#!/usr/bin/env python3
"""
fetch_stats.py — pulls REAL, verifiable data only. No fabricated numbers, no
inflated claims. Every value written here must be traceable to a live GitHub
API response or a specific CI run. If a data source is unavailable, this
script writes an honest "unavailable" placeholder rather than guessing.

Output: writes stats.json in the repo root, consumed by render_readme.py.
"""
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

GH = "gh"
OWNER = "Andre-Weissmann"


def run_gh(args):
    """Run a `gh` CLI command and return parsed JSON, or None on failure."""
    try:
        result = subprocess.run(
            [GH] + args, capture_output=True, text=True, timeout=30, check=True
        )
        return json.loads(result.stdout) if result.stdout.strip() else None
    except Exception as e:
        print(f"WARN: gh command failed ({args}): {e}", file=sys.stderr)
        return None


def fetch_user_profile():
    data = run_gh(["api", f"users/{OWNER}"])
    if not data:
        return {"followers": None, "public_repos": None, "created_at": None}
    return {
        "followers": data.get("followers"),
        "public_repos": data.get("public_repos"),
        "created_at": data.get("created_at"),
    }


def fetch_repos():
    """List public, non-fork repos with real star/language/push data."""
    data = run_gh([
        "repo", "list", OWNER,
        "--limit", "50",
        "--json", "name,description,stargazerCount,primaryLanguage,pushedAt,url,isFork",
    ])
    if not data:
        return []
    return [r for r in data if not r.get("isFork")]


def fetch_latest_workflow_run(workflow_file):
    """
    Query a SPECIFIC named workflow file directly for its latest run on main,
    rather than scanning a shared, noisy run list (which can be dominated by
    high-frequency unrelated workflows and miss less-frequent ones entirely).
    Returns None if the workflow has no runs or the API call fails.
    """
    runs = run_gh([
        "run", "list",
        "--repo", f"{OWNER}/dataglow",
        "--branch", "main",
        "--workflow", workflow_file,
        "--limit", "1",
        "--json", "conclusion,createdAt",
    ])
    if not runs:
        return None
    return runs[0]


def fetch_dataglow_ci():
    """
    Pull the latest run of the two flagship, verifiable CI workflows for
    DataGlow: the main test suite and the zero-upload egress-deny proof.
    Returns None fields (never fake numbers) if a workflow is unavailable.
    """
    tests_run = fetch_latest_workflow_run("test.yml")
    zero_upload_run = fetch_latest_workflow_run("zero-upload-proof.yml")

    return {
        "tests_status": tests_run.get("conclusion") if tests_run else None,
        "tests_checked_run_at": tests_run.get("createdAt") if tests_run else None,
        "zero_upload_status": zero_upload_run.get("conclusion") if zero_upload_run else None,
        "zero_upload_checked_run_at": zero_upload_run.get("createdAt") if zero_upload_run else None,
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }


def fetch_dataglow_open_pr_count():
    """Real, current count of open PRs — an honest 'work in progress' signal,
    not something to hide."""
    prs = run_gh([
        "pr", "list", "--repo", f"{OWNER}/dataglow", "--state", "open",
        "--json", "number",
    ])
    return len(prs) if prs is not None else None


def main():
    stats = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "profile": fetch_user_profile(),
        "repos": fetch_repos(),
        "dataglow_ci": fetch_dataglow_ci(),
        "dataglow_open_prs": fetch_dataglow_open_pr_count(),
    }

    out_path = os.path.join(os.path.dirname(__file__), "..", "stats.json")
    with open(out_path, "w") as f:
        json.dump(stats, f, indent=2)

    print(f"Wrote {out_path}")
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
