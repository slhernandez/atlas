# The two modes

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
- **Relay hygiene** — every prompt self-contained; facts carry as-of times; a re-delivered
  message gets "already reviewed, verdict stands," never a re-run.

## Why the structure works, in one line

Every catch comes from **fresh context with a verification mandate** — the planner
re-verifies the supervisor's research, the supervisor reviews work it didn't author, the
implementor never sees the research so it has nothing to redesign from, and the human
holds every gate that matters.

See also `docs/patterns/` for the recurring shapes both modes lean on: the
generated-client dependency order for multi-repo work, and domain-owned content.
