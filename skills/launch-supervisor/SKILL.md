---
name: launch-supervisor
description: |
  Generate the kickoff prompt for a new SUPERVISOR window on a big, multi-session feature
  that will run the manual multi-window relay (supervisor → planner → implementor in
  separate Claude Code windows). Use this skill whenever the user wants to:
  - Start a new big feature and hand it to a fresh supervisor context
  - Produce a supervisor/kickoff/handoff prompt for an epic
  - Move a feature off the current context window onto a clean one
  MANDATORY TRIGGERS: launch supervisor, supervisor prompt, kickoff prompt, new supervisor
  window, start big feature, hand off feature, feature kickoff, supervisor handoff
  Takes an epic-sized work item id or URL as argument.
  NOT for: work that fits one plan and one PR (that is /atlas:feature-workflow), and not
  for spawning subagents in-session.
---

# Launch Supervisor

Produce ONE artifact: a self-contained prompt that a fresh Claude Code window can be given
to act as supervisor for a big feature. The prompt is the deliverable, not a summary of it.

Whether the feature belongs in multi-session mode at all is a size question — one plan and
one PR takes `/atlas:feature-workflow` instead (see `docs/two-modes.md`), and this skill
should say so rather than generate a prompt.

**The hard rule of this skill: do the research BEFORE writing the prompt.** A kickoff
prompt assembled purely from the work item is worth very little — the item is what the new
window would read anyway. The value is in the *verified starting facts* section, which only
exists if you go and establish them. If you find yourself writing the prompt without having
run searches against the actual repos, stop and go do that first.

## Phase 1 — Gather the brief (read, do not skim)

1. The work item itself, fetched per the config's tracker — if `~/.claude/atlas.json`
   is missing, stop and tell the operator to run `/atlas:setup` first. (With tracker
   `manual`, ask the operator for the brief and any documents that carry it.) Its
   description is the authoritative brief.
2. Hunt for a richer source than the item. Meeting notes and roadmap documents in the
   journal usually contain the stakeholders' actual words and are more useful than the
   ticket. Search `<journal>/` for the feature name.
3. Prior art: search the journal (and any design/spec repo the operator keeps) for existing
   spec, research, or decision docs on the same subject; search the tracker for related
   open items.
4. Note who the stakeholders are and what each one cares about, separately. A supervisor
   who knows "this is the product lead's north star, that is the finance owner's concern"
   makes better calls than one handed a flattened requirement list.

## Phase 2 — Establish verified starting facts (the part that earns the skill)

For every claim the feature rests on, go and check it in the code. Cite `file:line`. Aim to
answer, at minimum:

- Does the thing the feature proposes to build **already partially exist**? Features
  described as greenfield very often have a half-built precedent under a different name.
- What consumes it today, and from which side (server vs client)? An assumption that
  something is server-side when it is client-only will misshape the whole plan.
- What is the **actual current shape** of the data/config/schema involved — not the
  intended shape. Quote it.
- Where does the stated pattern already exist to copy from, and where does the current
  implementation **fail to follow** the pattern the stakeholder assumes it follows?
- What is the closest existing analogue in the codebase to model new work on?

Record each fact so the new window can re-verify cheaply, and tell it to re-verify rather
than trust. Include any fact that **corrects a likely assumption** — those are the
highest-value lines in the whole prompt.

## Phase 3 — Surface decisions the operator must make before work starts

Look for conflicts between the feature's goal and existing process or standing rules
(HOUSE_RULES.md is the first place to check). Typical sources: governance that is path- or
file-triggered and would be bypassed by the new design; process steps the operator waived
on a previous feature but which the work item still assumes; anything where two stated
goals cannot both hold.

Put these to the operator as a small number of specific questions, each with the evidence
and your recommendation. Then **fold the answers into the prompt as settled rulings** with
"do not re-open these" — and for any accepted exception, write the BOUNDARY, not just the
permission. An exception without a written edge erodes. Where a decision removes a safety
net, propose rebuilding the safety in the design (e.g. as a schema constraint) rather than
relying on care.

## Phase 4 — Choose the phase shape honestly

The relay's standard shape (planner → review → sign-off → implementor → PR review → merge)
is an **execution** shape. It works when the target is known and the risk is drift.

If the feature's first phase is genuinely research — the stakeholder is asking "what is the
best way to do this?" rather than "build this" — say so and adapt: send the same brief to
2–3 windows that cannot see each other, then compare. One window producing options and then
critiquing them anchors on its own first idea. Revert to the standard shape once a
direction is picked.

For any research phase, give every proposal a **disqualifier test** — a concrete, checkable
question that a bad-but-elegant proposal will fail. The best ones come from the
stakeholder's own goal statement, restated as a walkthrough ("narrate how X would have been
added under this design"). This turns an aesthetic architecture debate into a checkable one.

## Phase 5 — Decide the launch repo, and say why

Claude Code memory is scoped per project path (`~/.claude/projects/<path-key>/memory/`),
and the counts are usually lopsided between repos in the same feature. Compare them:

```
for d in ~/.claude/projects/*; do echo "$d $(ls "$d/memory" 2>/dev/null | wc -l)"; done
```

Launch from the repo with the accumulated memory and the substantial auto-loading
CLAUDE.md, even if the feature is multi-repo — every learned rule lives there and a sibling
repo starts near-empty. State the choice and the reason in your handoff, and note in the
prompt which CLAUDE.md files do NOT auto-load and must be read explicitly.

## The prompt's required sections

Write the prompt inside a single fenced block so it can be copied cleanly. Include, in
order:

1. **Role + work item identity** — who they are, the item's key + URL + current
   status/assignee, and that this is the manual multi-window relay with the operator
   relaying artifacts.
2. **Standing responsibilities** — author every downstream prompt (self-contained,
   absolute paths, facts with as-of times and sources); review every artifact by verifying
   load-bearing claims at file:line against origin, never the working tree, never a
   subordinate's summary; the operator approves specs/plans and merges every PR, the
   supervisor never merges. Include the relay's idempotent-receiver rule: with many
   windows, the operator will occasionally re-deliver a message — recognize the repeat and
   answer "already reviewed, verdict stands" rather than re-running the work.
3. **The dossier** — its path under `<journal>/dossiers/`, dated filename, created in the
   first session, and the requirement that it be resumable from itself alone via an opening
   RESUME BLOCK (current phase, live threads, pending prompts verbatim, standing rules).
4. **Read these first, in order** — absolute paths, with which auto-load and which do not.
5. **What the feature is** — lead with the north star in the stakeholder's own words.
6. **The hard parts, in the stakeholder's order of concern** — not yours. Include their
   stated hunches and stated fallbacks, marked as such.
7. **Verified starting facts** from Phase 2, with file:line, and an instruction to
   re-verify rather than trust.
8. **Already decided — do not re-open**, from Phase 3, each with its boundary.
9. **Phase sequence** from Phase 4, including where the shape deliberately deviates and
   where it reverts.
10. **Standing rules that bit before** — the concrete ones from HOUSE_RULES.md and recent
    scorecards, beyond what the repo's CLAUDE.md carries. Prefer rules that cost real time
    when violated.
11. **Adjacent but out of scope** — related commitments that exist so they are not folded
    in.
12. **Framing/stakes** — the operator's own words on how big or risky this is; it licenses
    the right amount of rigour.
13. **START BY** — exactly what to report back first, and confirmation that nothing is
    blocked.

For a complete worked example, see `references/example-kickoff.md` beside this file. Match
its altitude and specificity, not its content.

## Output

Write the prompt to `<journal>/plans/YYYY-MM-DD-<work-item>-supervisor-kickoff-prompt.md` with a
one-line instruction above the fence saying which repo to launch from. Then tell the
operator: the path, the launch repo and why, what the new window should report back first,
and any decision still open. Do not paste the whole prompt into chat — they are about to
copy it from the file.

## Quality bar

The prompt has failed if the new window's first act is to ask a question the skill should
have answered, or to rediscover a fact you could have verified. Before handing it over,
reread it as if you had no context at all and check every proper noun, path, and claim is
either present or explicitly delegated.
