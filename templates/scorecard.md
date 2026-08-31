---
work_item: TICKET-123
run_date: YYYY-MM-DD
graded: YYYY-MM-DD
grade: <A / B / C / F>
---

# Run Scorecard — TICKET-123

> Grade after merge (or abort). Part 3 is graded by an independent session that did not
> run the work — the writer is never the grader. (Launch a fresh Claude Code session by
> hand and point it at this file and the PR; a grader skill is planned for a later phase.)

## Run metadata
| | |
|---|---|
| Work item / size | |
| Duration (launch → PR-open → merge) | |
| Artifacts (research / plan / review) | |
| Outcome | |

## 1 · Process fidelity
Phases in order; status handshake transitioned correctly; **hard gate 1** — zero implementor
activity before explicit plan approval; **hard gate 2** — close-out only after explicit merge
confirmation; sign-off reached the SAME planner (no re-spawn); roles exchanged paths, never
pasted contents; per-task commits; every deviation declared in the plan file; clean worktree
lifecycle with nothing force-removed.

## 2 · Role quality
Did each role add its intended value? Planner's verification table filled with real file:line
evidence; its questions genuine judgment calls; mutation checks baked into any guard-locking
test. **Zero refutations on a research-heavy run is a yellow flag, not a green one.** The
supervisor spot-checked claims itself, amended substantively, reviewed task-by-task, and held
triage discipline. The implementor built only what the plan says, with extra verification that
left no trace in any commit.

## 3 · Outcome quality (independent grader)
Fresh-context re-review of the diff in an isolated worktree; the findings the run's own review
missed (each one a correction candidate); work-item alignment in both directions; and **proof
that guard-locking tests actually lock — revert the fix in a scratch worktree and watch the
new tests fail.**

## 4 · Friction log
| Friction | Correction | Applied to |
|---|---|---|

**Closing question — which frictions become HOUSE_RULES entries?**

## 5 · Verdict
Grade (A: protocol + outcome clean · B: shipped, corrections needed · C: human rescue
required · F: aborted), plus the honest questions: *would a plain session have done this
better or cheaper?* and *what does this run say about the system?*
