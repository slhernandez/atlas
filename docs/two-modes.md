# The two modes — and the rung below them

Three altitudes, one skill: match the process to the size of the *uncertainty*, not the
size of the diff.

## Rung 1 — Research first: `/atlas:research`

For bug tickets, small tasks, and any "how does this actually work?" A sparse ticket goes in;
a research document comes out — where it lives, how it works today, the closest existing
pattern, load-bearing claims verified at file:line, a scope assessment, open questions. Then
one of two exits: the fix is now obvious and small, so do it in the same session with no
ceremony; or the research shows structural work, so hand the document to the kit, whose
Phase 0 starts from it. Why research comes first for bugs: the **wrong-root-cause trap** —
fixing the symptom a ticket names is the commonest way AI-assisted bug work goes wrong, and
research separates *what the ticket says* from *what the code does* before anyone edits.
(Scale to the question: a one-file lookup needs no research run — just ask.)

| Signal | Rung |
|---|---|
| Quick lookup, one file | plain session — just ask |
| Bug ticket / small task | research first, then fix or escalate |
| 3+ tasks, an open design question, shared code | single-session mode (the kit) |
| Spec gate, multi-slice, weeks | multi-session mode |

The cost of the wrong rung: the kit on an epic degrades and dies mid-feature with the state in
its head; multi-session on a ticket is four windows for a 90-minute change; no research on a
bug is a confident fix to the wrong cause with tests that lock it in.


Both are the same supervised three-role workflow — a **supervisor** that researches and
reviews, a **planner** that verifies and writes the plan, an **implementor** that builds
exactly what was signed off. They share the plan-file protocol (status handshake:
`ready-for-supervisor-review → approved-with-amendments → signed-off → merged`), the human
gates, and the review standards. The difference is the bus.

## Single-session mode — `/atlas:feature-workflow`

One session runs the whole work item; the session IS the supervisor and spawns the planner
and implementor as fresh-context subagents. For ticket-sized work: one plan, one PR.

You are needed at five gates: scope answers (Phase 0), the plan gate (hard stop),
the manual smoke test, PR-feedback triage, and merge. Everything between runs unattended
inside your permission rails.

Reach for it when the plan would have 3+ real tasks, there's an open design question, or
the change touches shared code with many call sites. Skip it when you already know the
diff — a plain session is faster, and the workflow would be ceremony.

## Multi-session mode — `/atlas:launch-supervisor`

The same roles as separate Claude Code windows, for features too big for one session —
multi-week, multi-slice, possibly multi-repo. You are the message bus: you carry
supervisor-authored prompts to fresh role windows, and carry back their closing summaries
plus artifact *paths* (never pasted file bodies — the supervisor reads artifacts from
disk).

The load-bearing additions:

- **The dossier** (`<journal>/dossiers/…`) — the supervisor's durable memory, resumable
  from itself alone via its RESUME BLOCK. Sessions are expected to die; the feature isn't.
- **Slices** — one plan and one PR's worth at a time, onto an integration branch, so the
  default branch stays always-deployable.
- **The commit ledger** — every commit on every branch in plain language, topped by a
  QA/Product summary, maintained by the supervisor at every review. Work too large to read
  as diff still gets a real merge gate, because a human can read the ledger. Single-session
  runs don't need one: the PR body's accessible overview is the ledger for one PR.
- **Relay hygiene** — every prompt self-contained; facts carry as-of times; a re-delivered
  message gets "already reviewed, verdict stands," never a re-run.

## Why the structure works, in one line

Every catch comes from **fresh context with a verification mandate** — the planner
re-verifies the supervisor's research, the supervisor reviews work it didn't author, the
implementor never sees the research so it has nothing to redesign from, and the human
holds every gate that matters.

See also `docs/patterns/` for the recurring shapes both modes lean on: the
generated-client dependency order for multi-repo work, and domain-owned content.
