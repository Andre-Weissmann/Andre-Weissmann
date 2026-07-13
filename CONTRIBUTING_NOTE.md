# About this repository

This is Andre Weissmann's [GitHub profile README repository](https://docs.github.com/en/account-and-profile/setting-up-and-managing-your-github-profile/customizing-your-profile/managing-your-profile-readme) — its `README.md` renders on [github.com/Andre-Weissmann](https://github.com/Andre-Weissmann).

## How it works

- `scripts/fetch_stats.py` pulls real, live data from the GitHub API (repo list, star counts, DataGlow's CI results) and writes it to `stats.json`. No number in this repo is hand-entered or aspirational.
- `scripts/render_readme.py` turns `stats.json` into the "Live status" section of `README.md`, replacing only the content between the `STATS:START`/`STATS:END` markers so any hand-written prose above stays intact.
- `.github/workflows/refresh-profile.yml` runs both scripts weekly (and on manual trigger) and opens a pull request with the diff. **It never commits directly to `main`.** Every refresh is reviewed and merged by hand.
- `AGENTS.md` / `llms.txt` are a machine-readable fact sheet for AI agents browsing this profile. Both are deliberately written as static facts only — no instructions to any AI system — because of documented prompt-injection risks in agent-readable repo files (see the comment at the top of `AGENTS.md`).

## Design principles

1. **Prove, don't tell.** CI status links to the live workflow run, not just a claim in prose.
2. **No badge walls, no streak gimmicks.** One screen, real data only.
3. **Human review on every change.** Automation proposes, a person disposes.
4. **Honesty over polish.** Open PR counts and work-in-progress status are shown plainly, not hidden.
