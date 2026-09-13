---
date: YYYY-MM-DD
work_item: TICKET-123 (or "none")
repository: <repo name>
as_of_commit: <hash of the commit the findings were verified against>
branch: <branch name>
status: current   # pending-skeptic while a skeptic pass is still running
last_updated: YYYY-MM-DD
---

# Research — TICKET-123 <short title>

## The brief
<the work item's requirement — with no tracker, the operator's pasted requirement verbatim>

## Summary
<the direct answer: what this change is, in a paragraph>

## Findings
<each load-bearing fact with its file:line citation — verified, not recalled>

## What already exists
<the closest existing pattern to model on; anything that partially does this already>

## Code references
<`path:line` - what's there, one per line — the index a planner navigates from>

## Scope assessment
<what will change, blast radius (tests, migrations, other services/clients, generated code), size estimate, questions for the reporter>

## Historical context (from the journal)
<prior research, plans, decisions — with paths and dates; flag anything likely superseded>

## Related research
<other research docs on adjacent topics>

## Open questions
<what the operator must decide before planning — these become the planner's binding constraints>
