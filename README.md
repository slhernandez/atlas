# Atlas

**The supervised software factory for AI-assisted engineering.**

A Claude Code plugin: three AI roles (supervisor, planner, implementor) run a ticket from
research to open PR with fresh-context verification at every handoff — and a human
signature on everything that matters. Merge is never automated.

> Private during construction. Structure and docs land phase by phase; installability
> arrives with the setup wizard in Phase 2.

## Structure

```
.claude-plugin/     plugin + marketplace manifests
skills/             setup (first-run wizard) · feature-workflow (single-session subagent
                    mode, phases 0-7) · launch-supervisor (multi-session kickoff generator)
agents/             workflow-planner · workflow-implementor (fresh-context roles)
templates/          plan · research · review · scorecard · HOUSE_RULES seed · dossier
                    (the multi-session supervisor's durable memory)
scripts/            atlas-workflow.sh launcher · lint-isms.sh scrub gate
docs/               two-modes guide · permissions · patterns/
```

## Install

Three commands in any Claude Code session, run from inside a git repository:

```
/plugin marketplace add slhernandez/atlas
/plugin install atlas@atlas
/atlas:setup
```

**Or the one-paste install** — paste this into Claude Code and let it do the first two for
you (every command still asks your permission; the wizard's questions stay yours to answer):

```
Install the Atlas plugin for me: run `claude plugin marketplace add slhernandez/atlas`,
then `claude plugin install atlas@atlas --yes`. If the install succeeds, tell me whether
/atlas:setup is available in this session; if it isn't, tell me to start a new session
and run /atlas:setup — that's the first-run wizard, which checks this machine, asks me a
few questions, and verifies the setup with a real tracker read. Don't run the wizard
yourself; I want to answer its questions.
```

## Configuration

`/atlas:setup` — the first-run wizard — configures everything below interactively and
verifies the tracker with a real read. The file it writes, for reference (`$ATLAS_JOURNAL`
overrides the journal path):

```json
{ "journal": "~/AtlasJournal", "tracker": "github", "tracker_detail": "owner/repo" }
```

`tracker` is `jira-mcp` | `github` | `manual`; `tracker_detail` is the Jira project key or
the GitHub repo that holds issues (omit for `manual`). The wizard seeds the journal from
`templates/`, with `HOUSE_RULES.md` at the journal root.

## Maintainers

`scripts/lint-isms.sh` guards this tree against origin-specific terms. It requires
`ATLAS_ISMS_BLOCKLIST_FILE` to point at your private blocklist (never committed here);
CI supplies it from the `ATLAS_ISMS_BLOCKLIST` repository secret. The check fails
closed — including on fork PRs, which cannot see the secret; that is deliberate while
the repo is private.
