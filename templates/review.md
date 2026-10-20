---
date: YYYY-MM-DD
work_item: TICKET-123
pr: <number + URL>
plan: <plan file path>
verdict: <APPROVE / FIX LIST / NEEDS DISCUSSION>
---

# PR Review — TICKET-123 (PR #N)

## Task-by-task
| Plan task | Commit(s) | Matches plan? | Notes |
|---|---|---|---|

## Mechanical-task isolation check
<for any "pure mechanical" task: the isolated diff was verified behavior-preserving — or wasn't>

## Declared deviations
<each: accepted / challenged, with reasoning>

## Commit & PR hygiene
<subjects, no attribution lines, no unrelated files, PR body template + accessible overview>

## Findings
**N findings: C critical, R recommended, S suggestions · P pre-existing** (or "No findings worth fixing.")
**How to undo:** <redeploy the previous build / a follow-up migration / a feature flag / an app release>

<numbered; each with file:line and a concrete failure scenario — a finding without one is a question.
A repeating pattern is one finding listing every instance.>

## Pre-existing
<findings whose failure also happens on the base: the code is unchanged (git blame) and nothing the
PR changes (a caller, an input, a setting, a removed guard) makes it reachable, more likely, or
worse. Never in the verdict or the fix list; offered to the operator as follow-up candidates.
If that can't be established, the finding is the PR's.>

## Fix list sent to implementor
<the scoped items, or "none — approved as built">
