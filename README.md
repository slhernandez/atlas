# Atlas

**The supervised software factory for AI-assisted engineering.**

A Claude Code plugin: three AI roles (supervisor, planner, implementor) run a ticket from
research to open PR with fresh-context verification at every handoff — and a human
signature on everything that matters. Merge is never automated.

> Private during construction. Structure and docs land phase by phase; installability
> arrives with the setup wizard in Phase 2.

## Maintainers

`scripts/lint-isms.sh` guards this tree against origin-specific terms. It requires
`ATLAS_ISMS_BLOCKLIST_FILE` to point at your private blocklist (never committed here);
CI supplies it from the `ATLAS_ISMS_BLOCKLIST` repository secret.
