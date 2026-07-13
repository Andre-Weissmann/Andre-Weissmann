#!/usr/bin/env python3
"""
render_readme.py — turns stats.json into README.md.

Design rules (deliberate, research-backed):
  - One screen. No "Hi I'm Andre" wave-emoji banner, no badge walls, no streak
    widgets. 2026 profile-README research is explicit that these read as
    template filler, not signal.
  - Every number shown must come from stats.json (real data) — never a
    hardcoded or aspirational figure.
  - Content is regenerated between HTML markers so any manual edits outside
    those markers survive re-runs (Simon Willison's reference pattern).
  - "Prove, don't tell": CI status and test outcomes are linked to their live
    GitHub Actions run, not just asserted in prose.
  - Open PR / work-in-progress counts are shown plainly, not hidden — this is
    a real, currently-active project, and hiding that would be dishonest.
"""
import json
import os
from datetime import datetime

START_MARKER = "<!-- STATS:START - AUTO-GENERATED, DO NOT EDIT BELOW -->"
END_MARKER = "<!-- STATS:END -->"

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
STATS_PATH = os.path.join(REPO_ROOT, "stats.json")
README_PATH = os.path.join(REPO_ROOT, "README.md")


def fmt_date(iso_str):
    if not iso_str:
        return "unavailable"
    try:
        return datetime.fromisoformat(iso_str.replace("Z", "+00:00")).strftime("%b %d, %Y")
    except Exception:
        return "unavailable"


def status_badge(conclusion):
    if conclusion == "success":
        return "🟢 passing"
    if conclusion in ("failure", "timed_out", "cancelled"):
        return f"🔴 {conclusion}"
    return "⚪ unavailable"


def render_static_header():
    return """# Andre Weissmann

Data analyst (healthcare focus). I enjoy building tools that I've wanted ever since I first learned lessons from the Google Data Analytics Professional Certificate program. Currently building [DataGlow](https://github.com/Andre-Weissmann/dataglow) — a zero-upload data cleaning and validation workbench.

Portfolio: [andre-weissmann-portfolio.pplx.app](https://andre-weissmann-portfolio.pplx.app)
"""


def render_stats_block(stats):
    ci = stats.get("dataglow_ci", {})
    profile = stats.get("profile", {})
    repos = stats.get("repos", [])
    open_prs = stats.get("dataglow_open_prs")

    lines = [START_MARKER, ""]
    lines.append("## Live status (auto-refreshed, not hand-written)")
    lines.append("")
    lines.append(
        f"**DataGlow CI:** tests {status_badge(ci.get('tests_status'))} · "
        f"zero-upload egress-deny proof {status_badge(ci.get('zero_upload_status'))} "
        f"([see the workflow](https://github.com/Andre-Weissmann/dataglow/actions/workflows/zero-upload-proof.yml))"
    )
    if open_prs is not None:
        lines.append(
            f"\n**Active work:** {open_prs} open pull request(s) on DataGlow right now — "
            f"this is a project in progress, not a finished showcase."
        )
    lines.append("")
    lines.append("### Repositories")
    lines.append("")
    lines.append("| Repo | Description | Stars | Last push |")
    lines.append("|---|---|---|---|")
    for r in sorted(repos, key=lambda x: x.get("pushedAt") or "", reverse=True):
        name = r.get("name", "?")
        url = r.get("url", "#")
        desc = (r.get("description") or "").replace("|", "-")
        stars = r.get("stargazerCount", 0)
        pushed = fmt_date(r.get("pushedAt"))
        lines.append(f"| [{name}]({url}) | {desc} | {stars} | {pushed} |")

    lines.append("")
    lines.append(
        f"*Last refreshed {fmt_date(stats.get('generated_at'))} · "
        f"data pulled live from the GitHub API, not hand-maintained · "
        f"see [`scripts/fetch_stats.py`](scripts/fetch_stats.py) for exactly what is measured and how.*"
    )
    lines.append("")
    lines.append(END_MARKER)
    return "\n".join(lines)


def main():
    with open(STATS_PATH) as f:
        stats = json.load(f)

    stats_block = render_stats_block(stats)

    if os.path.exists(README_PATH):
        with open(README_PATH) as f:
            existing = f.read()
    else:
        existing = ""

    if START_MARKER in existing and END_MARKER in existing:
        pre = existing.split(START_MARKER)[0]
        post = existing.split(END_MARKER)[1]
        new_content = pre + stats_block + post
    else:
        new_content = render_static_header() + "\n" + stats_block + "\n"

    with open(README_PATH, "w") as f:
        f.write(new_content)

    print(f"Wrote {README_PATH}")


if __name__ == "__main__":
    main()
