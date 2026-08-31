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
skills/             /atlas:feature-workflow (single-session subagent mode, phases 0-7)
agents/             workflow-planner · workflow-implementor (fresh-context roles)
templates/          plan · research · review · scorecard · HOUSE_RULES seed · dossier (multi-session mode — Phase 2)
scripts/            atlas-workflow.sh launcher · lint-isms.sh scrub gate
docs/               (Phase 2)
```

## Configuration (hand-setup until the Phase 2 wizard)

Create `~/.claude/atlas.json`:

```json
{ "journal": "~/AtlasJournal", "tracker": "github", "tracker_detail": "owner/repo" }
```

`tracker` is `jira-mcp` | `github` | `manual`; `tracker_detail` is the Jira project key or
the GitHub repo that holds issues (omit for `manual`). Seed the journal by copying this
plugin's `templates/` into it, with `HOUSE_RULES.md` at the journal root.

## Maintainers

`scripts/lint-isms.sh` guards this tree against origin-specific terms. It requires
`ATLAS_ISMS_BLOCKLIST_FILE` to point at your private blocklist (never committed here);
CI supplies it from the `ATLAS_ISMS_BLOCKLIST` repository secret. The check fails
closed — including on fork PRs, which cannot see the secret; that is deliberate while
the repo is private.
