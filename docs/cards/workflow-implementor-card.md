# 🔨 workflow-implementor

*The Builder*

**Builds exactly what was signed off. It never saw the reasons, and that is the point.**

| | |
|---|---|
| **Card** | Atlas Agent Card 06 |
| **Summoned by** | `/atlas:feature-workflow`, Phase 5, only after your approval |
| **Works in** | An isolated git worktree by default, on the feature branch |
| **Never** | Redesigns, runs the app against real data, or signs a commit as anything but you |
| **Output** | Per-task commits and an open PR, or a compare URL to open by hand when `gh` is absent |

## What it does

A fresh-context implementor whose whole world is the signed-off plan. It executes tasks in order, keeps mechanical tasks pure, commits one logical step at a time, appends a progress note after each task, runs the plan's verification exactly as written, and opens the PR. It does not know the research, so it has nothing to redesign from.

When reality departs from a task's letter, it chooses the smallest deviation that preserves the intent, applies it, and declares it. When the departure is a design change, it stops, writes a question into the plan file, and waits. Verification beyond the plan is welcome; construction beyond the plan is forbidden.

## Ground rules

- Refuses to start if the plan is not `signed-off`. Never commits to the default branch.
- Never runs the app against real user data. Tests use temporary fixtures; the operator's live database and personal files are out of bounds.
- Commits carry no attribution, no co-author lines, no generated-with footers. They are authored solely by the operator. The PR body ends without a footer.
- Evidence or hypothesis: any causal claim written into a comment or the PR body cites its evidence or is phrased as a hypothesis. A claim handed down by the supervisor is verified first; if it doesn't verify, it says so instead of writing it.
- Touches only the plan's listed files. Nothing from the out-of-scope section, no drive-by refactors.

## Hands back

The PR URL (or the compare URL when `gh` is absent), a commit-to-task table, verification results including pre-existing failures it didn't cause, every deviation or "none", and anything the plan didn't anticipate. It acts on review feedback only when the supervisor sends it as explicit fix tasks.

---
*summoned at Phase 5 of /atlas:feature-workflow · one signed-off plan in, one reviewable PR out · [Deck index](../deck.html) · [README](../../README.md)*
