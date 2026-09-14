# Atlas

**The supervised software factory for AI-assisted engineering.**

A Claude Code plugin. A read-only research team scopes a work item before anyone edits;
three AI roles (supervisor, planner, implementor) then run it from research to open PR with
fresh-context verification at every handoff — and a human signature on everything that
matters. Merge is never automated.

> Private during construction; installable now (`/atlas:setup` is the front door). Docs and
> the companion site land before launch.

## Structure

```
.claude-plugin/     plugin + marketplace manifests
skills/             setup (first-run wizard) · research (rung one: scope before you build) ·
                    feature-workflow (single-session subagent mode, phases 0-7) ·
                    launch-supervisor (multi-session kickoff generator)
agents/             workflow-planner · workflow-implementor (fresh-context roles) · the
                    research team: codebase-locator · codebase-analyzer ·
                    codebase-pattern-finder · journal-locator · journal-analyzer
templates/          plan · research · review · scorecard · HOUSE_RULES seed · dossier
                    (the multi-session supervisor's durable memory) · ledger (plain-language
                    commit tables + QA/Product summary for integration-branch work)
scripts/            atlas-workflow.sh launcher · lint-isms.sh scrub gate
docs/               two-modes guide · permissions · patterns/
```

## Install

Three commands in any Claude Code session, run from inside a git repository. The marketplace
and the plugin are both named `atlas`, so the install string is exactly `atlas@atlas`:

```
/plugin marketplace add slhernandez/atlas
/plugin install atlas@atlas
/atlas:setup
```

**Or the one-paste install** — paste this into Claude Code and let it do the first two for
you (every command still asks your permission; the wizard's questions stay yours to answer):

```
Install the Atlas plugin for me: run `claude plugin marketplace add slhernandez/atlas`,
then `claude plugin install atlas@atlas --yes`. When the install succeeds, tell me that
/atlas:setup is ready — it is available in this same session, no restart needed. That's the
first-run wizard, which checks this machine, asks me a few questions, and verifies the setup
with a real tracker read. Don't run the wizard
yourself; I want to answer its questions.
```

After setup, the ladder: `/atlas:research <item>` for bugs and small tasks (then fix
in-session or escalate), `/atlas:feature-workflow <item>` for features, `/atlas:launch-supervisor`
for multi-week work. `docs/two-modes.md` has the decision table.

## Configuration

`/atlas:setup` — the first-run wizard — configures everything below interactively and
verifies the tracker with a real read. The file it writes, for reference (`$ATLAS_JOURNAL`
overrides the journal path):

```json
{ "journal": "~/AtlasJournal", "tracker": "github", "tracker_detail": "owner/repo" }
```

`tracker` is `jira-mcp` | `github` | `manual`; `tracker_detail` is the Jira project key or
the GitHub repo that holds issues (omit for `manual`).

## The journal

Everything Atlas produces lives outside your repos, in one place the wizard creates:

```
~/AtlasJournal/
├── HOUSE_RULES.md   your standing rules — every skill obeys them, they outrank the plugin's
│                    defaults, and they survive plugin updates (fold frictions in here)
├── research/        research docs — what the code actually does, verified at file:line
├── plans/           implementation plans (status handshake in frontmatter) + kickoff prompts
├── reviews/         the supervisor's PR reviews
├── dossiers/        multi-session feature dossiers + commit ledgers
└── scorecards/      graded runs — the friction log is where improvements come from
```

Skills consult the journal before starting anything, so the system's inputs get richer with
every run you complete. `_template.md` files are plugin-owned and refreshed by setup; your
own documents are never overwritten.

## Docs

- `docs/cards/quick-start-card.md` — what to type, from an empty machine to your first scorecard
- `docs/two-modes.md` — the ladder (research → single-session → multi-session) and when to use which
- `docs/permissions.md` — the doorman pattern and the recommended deny rail
- `docs/patterns/` — generated-client dependency order for multi-repo work; domain-owned content

## Maintainers

`scripts/lint-isms.sh` guards this tree against origin-specific terms. It requires
`ATLAS_ISMS_BLOCKLIST_FILE` to point at your private blocklist (never committed here);
CI supplies it from the `ATLAS_ISMS_BLOCKLIST` repository secret. The check fails
closed — including on fork PRs, which cannot see the secret; that is deliberate while
the repo is private.
