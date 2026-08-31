---
date: YYYY-MM-DD
work_item: TICKET-123 (or "none")
title: <short title>
repository: <repo name>
branch: <branch or "not yet created">
base_commit: <hash>
research: <research doc path>
status: ready-for-supervisor-review   # → approved-with-amendments → signed-off → merged
last_updated: YYYY-MM-DD
---

# TICKET-123 — <title>

## Questions for Supervisor
<numbered, each marked blocking or non-blocking — or "None.">

## Overview
<what and why>

### Reasoning
<defend the non-obvious design choices>

## Design
<state machines / data flow where applicable>

## Task breakdown

### T1 — <name>
<file paths, exact line references, code sketch for the non-obvious>
**Acceptance:** <how the implementor knows T1 is done>

### T2 — Tests (same PR)
<what the tests assert; note any test that exists to lock a guard — those get a mutation check>

### T3 — Verification
<build/analyze commands + targeted test commands; mutation checks spelled out>

## Test plan
<cases + test-infrastructure caveats discovered>

## Out of scope
<bulleted, one-line justification each>

## Verified against code (research claims spot-checked)
| Claim | Result |
|---|---|
