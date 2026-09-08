---
name: research
description: Research the codebase to answer a question or scope a work item, using parallel read-only subagents and writing a durable research document to the journal. Use when the user says "research", "/atlas:research", "scope this ticket", "how does X work", or hands you a sparse bug report or small task before any fix. Takes a work item ID, a URL, or a free-text question as argument. The first rung of the ladder — research first, then fix in-session or escalate to /atlas:feature-workflow.
---

# Research

You answer a question about the codebase — or scope a work item — by fanning out read-only
subagents, verifying their load-bearing claims yourself, and writing a research document
that future runs will trust. Live code is the source of truth; the journal is history.

## Before anything: config, journal, house rules

Resolve the journal (`$ATLAS_JOURNAL`, else `journal` in `~/.claude/atlas.json`, else
`~/AtlasJournal`); if the directory or the config is missing, stop and point at
`/atlas:setup`. Read `<journal>/HOUSE_RULES.md` — binding, senior to this file. Read the
repo's CLAUDE.md for its layout and conventions. Pass three paths to every agent you
spawn: the journal root, `<journal>/HOUSE_RULES.md`, and the repo's CLAUDE.md (the
codebase agents use HOUSE_RULES only for search-scope rules; the journal agents use it for
extra notes directories).

## Steps

1. **Gather the inputs first, in the main context.** If the argument is a work item, fetch it
   per the config's tracker — description AND comments; on sparse work items the
   requirements hide in the comments. With tracker `manual`, ask for the brief. If the user names files
   (work items, docs, JSON), read them entirely so decomposition starts from full context.
2. **Decompose the question** into composable research areas — components, patterns,
   connections. **Scale to the question:** a single-component question needs one locator and
   one analyzer; only a broad architectural question justifies four or more parallel agents.
   A one-file lookup needs no agents at all — just answer.
3. **Spawn parallel read-only subagents**, each told WHAT to find, never HOW to search:
   - `atlas:codebase-locator` — where things live (first pass: what exists)
   - `atlas:codebase-analyzer` — how a component actually works, at file:line (launch as soon
     as its locator returns — don't wait for the slowest one)
   - `atlas:codebase-pattern-finder` — existing implementations to model new work on
   - `atlas:journal-locator` — prior research, plans, reviews, and decisions in the journal
   - `atlas:journal-analyzer` — deep read of one journal document a locator surfaced
   - the built-in `Explore` agent, if your Claude Code version has it — broad sweeps that
     fit none of the above
4. **Synthesize.** Live findings outrank journal findings. Connect components; keep every
   claim pinned to file:line. **Verify before writing:** re-read the load-bearing claims at their
   cited locations yourself (two or three for a small question; every one when scoping a
   work item) — the document is persistent and will be trusted.
   **Skeptic pass (substantial runs only):** for work-item scoping or multi-component research,
   spawn ONE independent agent whose sole job is to refute the load-bearing claims and scope
   conclusions ("try to disprove: <claim>, with file:line evidence"); fold surviving
   objections into Open Questions. Skip it for small single-component runs.
5. **Write the research document** from the journal's research template to
   `<journal>/research/YYYY-MM-DD-<work-item>-<desc>.md` (omit the work item when there is
   none). Frontmatter carries the real `date`, `as_of_commit`, and `branch` — never
   placeholders. Journal findings go under *Historical context* and *Related research*;
   the load-bearing file:line list goes under *Code references*. Include the Scope Assessment when researching a work item: what will change,
   blast radius (tests, migrations, other services or clients, generated code), a rough size,
   and the questions to ask the reporter before starting.
6. **Present findings:** the direct answer first, then the key file references, then the
   document path — and the exit: if the fix is now obvious and small, do it in this session;
   if the research shows structural work (3+ tasks, an open design question, shared code with
   many call sites), hand the research doc to `/atlas:feature-workflow` by passing its path as the
   run's extra context (`/atlas:feature-workflow <item> "research: <path>"`), and Phase 0
   starts from it instead of from scratch.
7. **Follow-ups** append a `## Follow-up Research <timestamp>` section to the same document
   and bump `last_updated`.

## Notes

- Always run fresh research — never rely solely on an existing research document; refresh it.
- Subagents are read-only; the main context synthesizes and verifies rather than deep-reading.
- Ask agents for examples and usage, not just definitions.
- The document must be self-contained: a reader with none of this context should understand it.
