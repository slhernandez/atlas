# 🧰 /atlas:setup

**Asks instead of assuming, proves the setup with a real read, and writes nothing to your settings.**

| | |
|---|---|
| **Card** | Atlas Skill Card 01 |
| **Invoke** | `/atlas:setup` |
| **Writes** | `~/.claude/atlas.json` and the journal |
| **Never touches** | Your Claude Code `settings.json` or permissions |
| **Re-run** | Shows current config, offers changes, refreshes plugin-owned templates |

## What it does

The first-run wizard. It checks the machine and prints a report card, one line per check. It proposes a journal location and seeds it from the plugin's templates. It detects your work-item tracker and **asks** rather than decides. When a tracker is configured, it proves the whole thing by fetching a real work item and reading its title back to you, and only after that proof does it write the config file. Manual mode has no tracker to prove, so it skips the read and says so.

Detection is a default, never a decision. Everything the wizard finds is presented for you to confirm or change, and the one thing it will not do is edit your Claude Code settings. The deny rail it recommends is printed for you to paste by hand.

## How to run it

Inside a git repository, in any Claude Code session:

```
/plugin marketplace add slhernandez/atlas
/plugin install atlas@atlas
/atlas:setup
```

The marketplace and the plugin are both named `atlas`, so the install string is exactly `atlas@atlas`. After the install, `/atlas:setup` is available in the same session, no restart needed. Or paste the one-paste prompt from the README and let Claude run the first two lines for you; the wizard's questions stay yours to answer.

## The six steps

1. **Step 0, preflight.** git present, inside a repository, identity set, `origin` reachable, `gh` authenticated, and a note on permission posture. Two of these block; the rest warn with a one-line fix.
2. **Step 1, journal.** Proposes `~/AtlasJournal`, accepts an override, seeds `HOUSE_RULES.md` plus the plan, research, review, dossier, ledger, and scorecard templates. Suggests `git init` without doing it.
3. **Step 2, tracker.** Jira through MCP tools, GitHub Issues through `gh`, or manual paste. What it detected is the default; you choose.
4. **Step 3, the one detail.** A Jira project key, or the GitHub issues repository, offering `origin` as the default.
5. **Step 4, verify with a real read.** Name any work item and it fetches the title through the chosen tracker. On a fresh repository with no items, it offers to open a small smoke-test item, read it back, and close it, saying first that this writes to your tracker. Manual mode skips this step; there is nothing to verify.
6. **Step 5, write config and hand over.** Only now does it write `~/.claude/atlas.json`, then it prints the quick start: research for a bug or small task, the feature workflow for a feature, and where your corrections go.

## Ground rules

- A wizard that ends with "config written" has verified nothing. Whenever a tracker is configured, this one ends with a proven read.
- Config is written last, after the proof, and only what you confirmed.
- Re-running never overwrites your content. Templates you haven't renamed can be refreshed, with the diff shown first.
- Your corrections go in `HOUSE_RULES.md`. Every skill obeys it, it outranks the plugin's defaults, and it survives updates.

---
*first run: preflight → journal → tracker → proven read → config · then /atlas:research or /atlas:feature-workflow · [Deck index](../deck.html) · [README](../../README.md)*
