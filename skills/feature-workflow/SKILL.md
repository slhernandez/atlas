---
name: feature-workflow
description: Run the supervised three-role feature workflow (supervisor → planner → implementor) in a single session using subagents. The session acts as researcher/supervisor; the workflow-planner and workflow-implementor agents run with fresh context. Use when the user says "feature workflow", "/atlas:feature-workflow", or asks to run the supervised multi-role workflow on a work item. Takes a work item ID (ticket key, issue number, or URL) as argument.
---

# Feature Workflow (supervised, single-session)

You are the **researcher/supervisor**. You hold the research context for the
whole run, you write every prompt the other roles see, and you are the filter
between them and the outside world (the operator, PR reviewers). The planner
and implementor run as subagents with **fresh context** — that isolation is
the point: they verify and execute without your biases, and you review their
work without authoring bias.

**Two human gates are non-negotiable: plan approval (Phase 4) and PR merge.
Never spawn the implementor before the operator has explicitly approved the
signed-off plan in chat.**

## Before anything: config, journal, house rules

Resolve the journal directory: `$ATLAS_JOURNAL` if set, else the `journal`
path in `~/.claude/atlas.json`, else `~/AtlasJournal`. If the resolved
directory does not exist, or `~/.claude/atlas.json` is missing (the tracker
config lives there), stop and tell the operator to run `/atlas:setup` first.
Where a journal copy of a template is missing, use the plugin's `templates/`
directly.

Read `<journal>/HOUSE_RULES.md` before any phase. It is the operator's
accumulated standing rules and is **binding — senior to anything in this
file**. Pass its path to every agent you spawn.

## File conventions

- Research doc: `<journal>/research/YYYY-MM-DD-<work-item>-<desc>.md`
- Plan file:    `<journal>/plans/YYYY-MM-DD-<work-item>-<desc>-plan.md`
- PR review:    `<journal>/reviews/YYYY-MM-DD-PR-<n>-<work-item>-<desc>-review.md`

The plan file is the shared protocol between roles: status handshake in
frontmatter (`ready-for-supervisor-review` → `approved-with-amendments` →
`signed-off`), decision log, `## Questions for Supervisor`,
`## Supervisor Review`, implementor progress notes and declared deviations.
Agents exchange **file paths, never pasted file contents**.

## Phase 0 — Research (you, inline)

1. Fetch the work item per the config's `tracker`: Jira via its MCP tools,
   GitHub via `gh issue view` against the config's repo, or — with no
   tracker — ask the operator to paste the requirement and record it verbatim
   at the top of the research doc as the brief. Read the description AND the
   comments; requirements hide in comments. If a recent research doc for this
   work item already exists in `research/`, read it and refresh only what's
   stale instead of redoing it.
2. Research the codebase: fan out read-only searches (where things live, how
   they actually work today, the closest existing pattern to model on), then
   verify every load-bearing claim yourself at file:line before writing it
   down. Write the research doc from the journal's research template,
   including a Scope Assessment and Open Questions.
3. **Resolve open questions with the operator now** (AskUserQuestion or
   chat). Decisions made here become the planner's "decided constraints" —
   the planner is forbidden from re-litigating them, so get them right.

## Phase 1 — Spawn the planner

Spawn the `atlas:workflow-planner` agent. The agent definition holds the
invariant protocol; your prompt supplies only the per-item specifics — keep
it self-contained:

- Work item ID + one-paragraph goal.
- Research doc path (ground truth, but instruct verification of key claims).
- Exact plan file path (today's date, per conventions above).
- HOUSE_RULES.md path.
- The decided constraints from Phase 0, numbered.
- Repo path + CLAUDE.md path.
- Hard scope boundaries (files/areas that are out of bounds).

Run it in the background; you'll be notified on completion. Do not poll.

## Phase 2 — Supervisor review of the plan

When the planner completes:

1. Read the plan file in full. **Spot-check its load-bearing claims yourself**
   at the cited file:line locations — especially claims your research didn't
   cover (the planner's fresh findings are high-value but unvetted).
2. Answer every `Questions for Supervisor` item with an explicit
   CONFIRMED/OVERRIDDEN verdict and reasoning.
3. Insert a `## Supervisor Review (<date>)` section immediately after the
   plan's frontmatter:
   verdict, answers, numbered amendments (Required vs Recommended), and a
   "Reviewed and explicitly fine as-is" list for things you considered and
   accepted (prevents re-review churn later).
4. Set frontmatter status to `approved-with-amendments` (or send it back
   for a revision round if the design is wrong — rare; prefer amendments).

## Phase 3 — Planner sign-off

Use **SendMessage to the same planner agent** (context intact — never
re-spawn and re-brief) telling it: review is appended, fold the amendments
into the task bodies so the plan reads correctly top-to-bottom, set
`status: signed-off`, no implementation. If the planner pushes back via a
`## Planner Response`, resolve it (you decide; escalate genuine judgment
calls to the operator) and repeat until signed off.

**Release the planner once signed off.** Your sign-off SendMessage must tell
the planner its plan-writing job is complete and that it will NOT be notified
when implementation starts or finishes — it should end its turn and expect
nothing further. If you want its read-only post-implementation check later
(recommended — fresh eyes on the diff catch real defects), that arrives as a
NEW SendMessage carrying the PR number. Never leave the planner with an
implied "wait for the implementor" expectation; it has no way to observe the
implementor and will stall.

## Phase 4 — HUMAN GATE: operator approves the plan

Present to the operator in chat: plan shape (task list one-liner each), the
planner's fresh findings, your amendments, and any open judgment calls.
**Stop and wait for explicit approval.** Also settle branch handling here:
ask whether the operator creates the feature branch or the implementor should
(branch name: `<work-item>-<desc>`).

## Phase 5 — Spawn the implementor

Spawn the `atlas:workflow-implementor` agent **in an isolated git worktree by
default** at `~/.atlas-worktrees/<work-item>-<desc>` (in-place only if the
operator explicitly says so at the plan gate). If the repo needs a worktree
bootstrap — gitignored toolchain or version-manager files that do not travel
into fresh worktrees — HOUSE_RULES.md records the commands: include them
verbatim in the spawn prompt. Prompt contains: plan file path, repo path,
worktree path, HOUSE_RULES.md path, CLAUDE.md path, branch name + whether to
create it, the base branch for the PR, and the work item's URL (or the words
"no tracker"). Nothing else — the implementor's
ignorance of your research is a feature; the plan is its whole world.

**Never assert repo or PR state in a spawn prompt that the agent cannot
verify** ("PR #N is merged", "CI is green"). State facts with their as-of
time, or instruct the agent to verify before writing them into any PR body or
commit. A stale assertion becomes a false claim in a permanent artifact.

Run in the background. If it stops with
`## Questions for Supervisor (implementation)` in the plan file, answer in
the plan file and SendMessage it to continue.

**Status protocol — the operator must never wonder what's happening:**

- **On spawn, announce it in chat**: the implementor is building, this is the
  long unattended stretch, and you will report the moment it finishes.
  Remind the operator that permission prompts can freeze the run silently
  unless the session runs in an auto-accepting permission mode — if they're
  stepping away, they should glance back for prompts.
- **You are notified automatically when the background agent completes** —
  never poll it on a timer. But if silence runs far past what the plan's size
  suggests (rule of thumb: 2× your estimate), check its task output ONCE,
  report what you see (progress notes in the plan file and per-task commits
  on the branch are the ground truth), and surface a stuck permission prompt
  to the operator rather than waiting indefinitely.
- **The moment the completion notification arrives, tell the operator in one
  line** — "implementor finished, PR #N is open; reviewing now" (or what
  actually happened, if it died) — BEFORE starting your Phase 6 review.

## Phase 6 — Supervisor PR review

When the implementor reports the PR URL:

1. Review the diff **task-by-task against the plan** (`gh pr diff`, or
   `git diff <base>...<branch>` when `gh` is unavailable). Verify any "purely
   mechanical" task commit in isolation (`git diff <sha>^..<sha>`) — its
   zero-behavior-change promise is checkable.
2. Verify amendments landed, assess declared deviations, check commit
   hygiene (subjects, no attribution lines, no unrelated files) and the PR
   body (per the PR-body template in the implementor agent definition,
   including the unlabeled accessible overview).
3. Write the review doc to `reviews/`. Verdict + summary go to the operator
   **in chat**; post nothing on the PR itself unless the operator asks.
   End this message with a clearly-marked **"READY FOR YOU"** block: the PR
   link, the manual steps that are theirs (smoke test, gates), and the merge
   decision. This is the handoff moment — make it unmissable.
4. If fixes are required: send the implementor (SendMessage, context intact)
   a scoped fix list — concrete items only, "fix these, nothing else". Do
   NOT forward the full review; an approving review gets a one-line
   close-out at most.

## Phase 7 — Post-merge close-out

When the operator confirms the PR is merged (never before — the worktree must
survive manual smoke testing and any review-fix rounds):

1. Remove the implementor's worktree:
   `git -C <repo> worktree remove <worktree-path>` then
   `git -C <repo> worktree prune`.
   Do NOT pass `--force`: if removal fails because the worktree is dirty,
   something un-pushed is sitting in it — surface that to the operator
   instead of deleting it.
2. Confirm the remote feature branch was deleted by the merge (or ask the
   operator if they want it kept).
3. Update the plan file frontmatter (`status: merged`, `last_updated`) so the
   run's record is closed.
4. Start a scorecard for the run from the journal's scorecard template — its
   closing question ("which frictions become HOUSE_RULES entries?") is how
   this system improves.
5. **End with a clearly-marked "RUN COMPLETE" message** — the run's final
   word, so completion is never ambiguous: work item + merged PR link, the
   artifact paths (research, plan, review, scorecard), worktree/branch
   cleanup confirmation, and every follow-up the run spawned. Nothing about
   the run should remain implicit after this message.

## Standing rules for the whole run

- **All PR feedback (coworkers, AI reviewers) routes through you.** Triage
  each finding against the plan: APPLY (real bug/regression this PR
  introduced) / SKIP (out of scope, decided-against, false positive — with
  reason) / DISCUSS (operator judgment call). Verdicts in chat; only APPLY
  items reach the implementor. Draft replies to human reviewers for the
  operator to post — never post them yourself.
- If a finding reveals a plan-level gap, amend the plan file first, then
  task the implementor — the plan stays the source of truth for the branch.
- A message you have already processed may be re-delivered; recognize the
  repeat and answer "already handled, verdict stands" rather than re-running
  the work.
- Update the plan/research docs' frontmatter (`last_updated`) as phases
  complete, so a dead session can be resumed from the files alone.
