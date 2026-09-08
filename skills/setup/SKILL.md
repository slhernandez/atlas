---
name: setup
description: First-run wizard for Atlas. Configures the journal and work-item tracker interactively, verifies the setup with a real read, seeds the journal from the plugin's templates, and prints the quick start. Use when the user runs /atlas:setup, asks to set up or configure Atlas, or when any Atlas skill reports missing configuration. Idempotent — re-running shows current config and offers changes.
---

# Atlas Setup — the first-run wizard

You configure Atlas by **asking, not assuming**. Detection findings are presented as
defaults; the operator decides. You never write to the operator's Claude Code settings or
permissions — configuration lives in `~/.claude/atlas.json` and the journal, nothing else.

If `~/.claude/atlas.json` already exists, this is a re-run: show the current config and the
preflight report card, offer to change any value, and **never re-seed over an existing
journal** (offer to add only missing template files, never overwrite).

## Step 0 — Machine preflight

Check, then print a report card (✓ / ⚠, one line each, each ⚠ with its one-line fix):

| Check | How | On failure |
|---|---|---|
| git installed | `git --version` | **BLOCK**: point at the platform's installer (on macOS the first `git` run offers the developer tools) |
| inside a git repository | `git rev-parse --show-toplevel` | **BLOCK**: "Atlas runs inside a git repository. `cd` into your project and re-run `/atlas:setup`." |
| git identity | `git config user.name` + `user.email` | ⚠ offer to set them now (ask for the values; this is git config, not Claude settings) |
| remote reachable | `GIT_TERMINAL_PROMPT=0 GIT_SSH_COMMAND='ssh -oBatchMode=yes -oConnectTimeout=5' git ls-remote -q --heads origin` (portable; converts a credential hang into the ⚠) | ⚠ "reads from `origin` failed — check your remote/credentials before a run needs to push" |
| `gh` present + authed | `gh auth status` | ⚠ "PRs will degrade to push + a compare-URL you open by hand; install/auth `gh` to restore one-step PRs" |
| permission posture | none (informational) | note: "your first run will ask for permission often; approvals accumulate — Atlas never edits your settings itself." Then offer to print the recommended deny-rail inline (nine lines, from the plugin's `docs/permissions.md`) |

Proceed past any ⚠. Block only on the two BLOCKs.

## Step 1 — Journal location

Explain in one sentence (everything Atlas produces — plans, research, reviews, scorecards —
accumulates here, outside your repos), propose `~/AtlasJournal`, accept an override.
Create the structure and seed it from the plugin's templates:

```
<journal>/HOUSE_RULES.md        (from templates/HOUSE_RULES.md)
<journal>/plans/                (templates/plan.md → plans/_template.md)
<journal>/research/             (templates/research.md → research/_template.md)
<journal>/reviews/              (templates/review.md → reviews/_template.md)
<journal>/dossiers/             (templates/dossier.md → dossiers/_template.md,
                                 templates/ledger.md → dossiers/_ledger-template.md)
<journal>/scorecards/           (templates/scorecard.md → scorecards/_template.md)
```

Resolve the plugin's `templates/` directory relative to this skill file's own location.
The plan skeleton also lives inside the planner agent (self-containment); the journal
copies are the operator's reference set.
Mention, without doing it: initializing the journal as a git repo is a good idea.

## Step 2 — Tracker

Probe first, silently: are Jira MCP tools available in this session? Is `gh` authenticated,
and what is this repo's `origin`? Then present what you found and ask the operator to
choose — detection is a default, never a decision:

- **Jira** (via MCP tools) — if none are connected, say so and point at Claude Code's MCP
  docs rather than walking them through it here.
- **GitHub Issues** (via `gh`).
- **Manual** — no tracker: each run starts by pasting the requirement. Zero dependencies;
  the guaranteed path.

## Step 3 — The one detail

Jira → ask for the project key (so `/atlas:feature-workflow 123` expands to `KEY-123`).
GitHub → ask for the issues repo, offering this repo's `origin` as the default.
Manual → nothing.

## Step 4 — Verify with a real read

Ask the operator to name any existing work item, fetch it through the chosen tracker, and
echo its title back. **Do not skip this step**: a wizard that ends with "config written"
has verified nothing; one that ends with a proven read has caught the stale OAuth or the
unauthenticated CLI while the operator is still at the keyboard. Manual mode: skip with a
note (there is nothing to verify).

If the read fails: show the error, offer to switch tracker (manual always works), and only
write config the operator confirms.

## Step 5 — Write config and hand over

Write `~/.claude/atlas.json`:

```json
{ "journal": "~/AtlasJournal", "tracker": "github", "tracker_detail": "owner/repo" }
```

(`tracker`: `jira-mcp` | `github` | `manual`; `tracker_detail`: Jira project key or GitHub
issues repo; omitted for manual. `$ATLAS_JOURNAL` overrides the journal path if the
operator prefers env config.)

Then print the quick start, exactly this shape:

> **You're set.** Start your first run: `/atlas:feature-workflow <work item>`
> It researches, asks you 2–3 scope questions, writes a plan for your approval (nothing is
> built before you approve), builds in an isolated worktree, opens a PR, and reviews it —
> then the merge is yours. Your corrections go in `<journal>/HOUSE_RULES.md`; every Atlas
> skill obeys that file, and it survives plugin updates.
