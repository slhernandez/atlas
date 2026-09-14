# 🧭 Quick Start

**From an empty machine to your first scorecard, in one sitting. The README tells you what Atlas is; this card tells you what to type.**

| | |
|---|---|
| **Card** | Atlas Guide Card 00 |
| **Needs** | Claude Code and git, run inside a repository |
| **Optional** | A reachable `origin` and an authenticated `gh` for one-step PRs; a tracker (Jira or GitHub Issues) |
| **Writes** | `~/.claude/atlas.json` and `~/AtlasJournal/` |
| **Never touches** | Your Claude Code settings. The deny rail is yours to paste |

## Before you start

Open Claude Code inside a git repository. The wizard's preflight runs a short checklist and blocks on two items: git must be present and you must be inside a repository. Everything else warns with a one-line fix: a missing git identity, an unreachable `origin`, an unauthenticated `gh`.

No tracker is fine. The **manual tracker option** has zero dependencies: each run starts by pasting the requirement. Pick it if you are unsure; you can re-run the wizard later and switch.

## 1 · Install

```
/plugin marketplace add slhernandez/atlas
/plugin install atlas@atlas
/atlas:setup
```

The marketplace and the plugin are both named `atlas`, so the install string is exactly `atlas@atlas`. After the install, `/atlas:setup` is available in the same session; no restart. If you would rather not type the first two lines, the README has a one-paste prompt that has Claude run them and stop before the wizard.

## 2 · Answer the wizard

It asks where the journal should live (`~/AtlasJournal` is the default), which tracker to use (what it detected is the default), and the one detail that tracker needs: a Jira project key, or the GitHub issues repository with `origin` offered as the default. With a tracker configured, it then asks you to name one real work item so it can prove the read. Detection is a default, never a decision.

When the wizard ends with **a real work item's title read back to you**, the setup is proven. If the read fails, it shows the error and offers to switch tracker; the manual option always works. With no tracker there is nothing to prove, and it says so.

## 3 · Paste the deny rail

The wizard offers to print it and never applies it; that is yours. Add this to your Claude Code `settings.json`, then keep it:

```
{
  "permissions": {
    "deny": [
      "Bash(git push --force:*)", "Bash(git push -f:*)",
      "Bash(git reset --hard:*)", "Bash(git clean:*)",
      "Bash(git worktree remove --force:*)",
      "Bash(gh pr merge:*)", "Bash(gh repo delete:*)",
      "Bash(rm -rf:*)"
    ]
  }
}
```

`gh pr merge` on the rail is the mechanical form of the core promise: merge is never automated, even if a prompt goes wrong. These are prefix rules and a floor, not a proof; review still does the real work. The full pattern is in [permissions.md](https://github.com/slhernandez/atlas/blob/main/docs/permissions.md).

## 4 · First run: research something real

Pick a bug or small task you actually have, then:

```
/atlas:research <work item or question>
```

It writes a verified research document to the journal, then offers to fix in-session or escalate to the feature workflow with the document in hand. Read the document before you accept either. Expect permission prompts on a first run. What you approve is the raw material for your allow list, which you build yourself; Atlas never edits your settings. A prompt for something obviously safe is an allow-list gap worth noting.

## 5 · Second run: a feature with a plan gate

When a change would have three or more real tasks, or an open design question:

```
/atlas:feature-workflow <work item>
/atlas:feature-workflow <work item> "research: <path>"
```

The second form carries a research document from step 4 into the run, so nothing is re-derived. You are needed at five points, and two of them are hard stops: approving the plan, and merging. Nothing is built before you approve, and the merge is never automated. Between them, the build runs unattended in a worktree under `~/.atlas-worktrees/`. The review ends with a **READY FOR YOU** block naming exactly what is yours to check; after you merge, the close-out runs and the run ends with **RUN COMPLETE**.

## After the run

- **The journal filled in.** `research/`, `plans/`, `reviews/`, and a `scorecards/` entry with Parts 1, 2, 4, and 5 written. Part 3 and the grade are for a fresh session that did not run the work.
- **Your corrections go in `HOUSE_RULES.md`.** Every skill obeys it, it outranks the plugin's defaults, and it survives updates. A rule you set at a gate is recorded there; a rule the run derives from its own frictions is only proposed.
- **Which rung next.** Bug or small task: research. Feature: the feature workflow. Multi-week work across sessions: `/atlas:launch-supervisor`. One-line fixes: a plain session. [two-modes.md](https://github.com/slhernandez/atlas/blob/main/docs/two-modes.md) has the decision table.

## If something goes wrong

- **Install fails on a manifest error.** Run `/plugin marketplace update atlas` and install again; you may have a stale marketplace copy.
- **The proof read fails.** Stale tracker auth is the usual cause. The wizard shows the error and offers to switch; fix the auth and re-run `/atlas:setup` later.
- **No `gh`.** The implementor pushes the branch and hands you a compare URL to open the PR by hand. Everything else works.
- **A run stops with a worktree it will not remove.** Something unpushed is in it. It is surfaced, never force-deleted; look before you clean up.

---
*start here: install → wizard → deny rail → first research run → first feature run · then the Deck, one card per skill and role · [Deck index](../deck.html) · [README](../../README.md)*
