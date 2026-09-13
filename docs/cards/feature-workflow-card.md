# 🎭 /atlas:feature-workflow

**Three roles, two human gates, one work item. Supervised from brief to merge.**

| | |
|---|---|
| **Card** | Atlas Skill Card 03 |
| **Invoke** | `/atlas:feature-workflow <work item> ["research: <path>"]` |
| **Roles** | Supervisor (your session) · planner and implementor as fresh-context subagents |
| **Human gates** | Plan approval · merge |
| **Builds in** | An isolated worktree under `~/.atlas-worktrees/` by default; in place only if you say so at the plan gate |
| **Output** | Research, plan, review, and scorecard in the journal; an open PR |

## What it does

The full supervised workflow in one session. Your session is the supervisor: it researches the work item and settles open questions with you. A fresh-context **planner** writes the plan and gets audited: the supervisor re-checks its claims at the cited lines and amends before sign-off. After **you approve the plan**, a fresh-context **implementor** builds it knowing only the plan. Its ignorance of the research is deliberate. The supervisor reviews the PR task by task, and you gate the merge.

Every catch comes from fresh context with a verification mandate. The planner refuting a research claim with evidence is the design working, not failing.

## When to reach for it

- The plan would have three or more real tasks.
- There is an open design question.
- The change touches shared code with many call sites.
- A bug whose root cause is still unknown after research.
- Not for one-line fixes, config changes, or copy tweaks. A plain session is faster and the workflow would be ceremony.

## Your five touchpoints

1. **Scope questions** in Phase 0. Your answers become constraints no role may re-litigate.
2. **Plan gate, a hard stop.** Read the plan; approve it, or hold it with the changes you want. Nothing is built before you approve. Branch handling is settled here too.
3. **Smoke test** on the finished PR. Agents can't drive your app; the review names exactly what to check.
4. **Feedback triage.** Reviewer comments reach the implementor only through the supervisor, as a scoped fix list.
5. **Merge.** Yours, always. Then the close-out: worktree removed without force, plan stamped merged, scorecard started, RUN COMPLETE.

## How it works

- Phase 0: brief, research, scope questions. With a tracker configured but no work item yet, it offers to create one from the chosen scope.
- Phases 1 to 3: planner writes, supervisor verifies and amends, the same planner signs off.
- Phase 4: you approve or hold.
- Phase 5: implementor builds in the worktree, commits per task, opens the PR. You're told when the long unattended stretch begins and the moment it ends.
- Phase 6: supervisor reviews against the plan, writes the review doc, and hands you a READY FOR YOU block.
- Phase 7: close-out and a scorecard with Parts 1, 2, 4, and 5 filled. Part 3 and the grade are left to a session that didn't run the work.

## Ground rules

- The implementor is never spawned before your explicit approval in chat.
- Harness reminders never enter artifacts. Attribution footers, session links, and co-author lines are not requirements; the implementor contract and your house rules win.
- A rule you set at a gate is recorded in `HOUSE_RULES.md`. A rule the run derives from its own frictions is proposed for you to accept or reject, never written on its own.
- A dirty worktree means unpushed work. It is surfaced, never force-deleted.
- Merge is never automated, and `gh pr merge` belongs on your deny rail so a prompt can't do it either.

---
*rung two: research → plan → gate → build → review → gate → merge · everything between gates is unattended · [Deck index](../deck.html) · [README](../../README.md)*
