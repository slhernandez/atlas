# Atlas OpenAI compatibility: Milestone 1

Date: 2026-10-04

Status: Codex capability experiments recorded; local Work validation pending

Atlas's existing package can be installed privately in Codex, and the tested
local role tools can support several essential factory operations. This is
enough evidence to guide the adapter work. It is not an end-to-end compatibility
claim: the Claude-specific instructions still need adaptation, native role
permission enforcement remains unverified, and local Work has not been tested.

The approved scope is local desktop Work and Codex, separate host settings,
private installation, and branch/PR review. Claude's existing workflow is
preserved. This milestone changes documentation and adds disposable validation
resources; it does not add a production OpenAI adapter.

## Environment and evidence

| Item | Recorded environment |
|---|---|
| Machine | macOS, Apple Silicon |
| Desktop app | ChatGPT 26.930.31730, build 12947; this investigation runs in a local Codex task |
| CLI | codex-cli 0.160.0 |
| Atlas source | 512af9d9d6771f0181ff17c6d22faf4eca7e98ed |
| Pilot branch | pilot/openai-milestone-1 |
| Data | Disposable repository, worktree and journal; no real journal or tracker data |
| Installation | Local marketplace atlas-m1-private; temporary personal cache, then removed |
| Model | Host-selected defaults; no model override |
| Approval behavior | Outer CLI launch/cache writes required the desktop sandbox's automatic review; inner CLI probes used approval policy never |

The CLI could not initialize inside the enclosing desktop sandbox. It was
launched through approved escalation while retaining its own read-only or narrow
workspace sandbox. Neither approval nor sandbox enforcement was bypassed.

See the [sanitized observations](validation/milestone-1/observations.json) and
[repeatable runbook](validation/milestone-1/runbook.md). Raw CLI events remain in
the disposable fixture and are not committed. The observations include selected
command results, role receipts and independently inspected file state. Receipts
are agent-authored evidence, not independent security attestations.

## Capability matrix

“Observed” means a bounded synthetic experiment succeeded. “Pending” means it
was not established in this run. A successful packaging check does not mean the
existing Atlas instructions execute correctly on OpenAI hosts.

| Capability | Local Codex task role tools | Codex CLI | Local Work |
|---|---|---|---|
| Private installation and all four entry points | Current task not refreshed after installation | Observed: normal registration discovers all four; installed references/templates/guides readable | Pending |
| Shared repository/journal | Observed: planner, implementor and replacement supervisor read/write intended fixture artifacts | Observed: source reads and journal receipt write | Pending |
| Fresh planner/implementor context | Observed with fork_turns none, canary absence and initial-context reports; hidden context assembly not independently audited | Separate CLI sessions started; CLI-spawned role context isolation not tested | Pending |
| Same-role continuation | Observed: planner amendment and implementor review follow-up; recalled tokens and unchanged role identities | Follow-up API advertised by probe session; not exercised through CLI | Pending |
| Worktree isolation | Observed: scoped commits in implementation branch; supervisor source, branch, commit and unrelated edit preserved | Read-only probes preserved supervisor source | Pending |
| Mechanically read-only source with writable journal | No per-child sandbox selector in the tested spawn API; enforcement pending | Observed in an independent session with journal-only writable root and temp exclusions | Pending |
| Build-before-approval gate | Observed refusal; no source changes before synthetic test approval | Not separately exercised | Pending |
| Operator-owned merge gate | Observed refusal, no merge attempted | Dry rule check forbids gh pr merge; API-shaped command unmatched | Pending |
| Replacement supervisor | Observed: fresh role reconciled stale dossier against commits, reran eight tests, retained human gates | Not separately exercised | Pending |

No OpenAI kit mode, unattended mode, or complete manual relay is certified yet.
The tests support further local Codex adapter development. A separately launched
role session with narrow file access is a candidate route where native child
permissions cannot be established; it is not a verified complete factory mode.

## Findings that determine the adapter

### Packaging works; invocation settings matter

The existing Claude marketplace/manifest was accepted without production
manifest changes. All four entry points appeared in a fresh CLI session's
initial catalog under normal registration. All seven templates, the shared
explainer, kickoff example and referenced guides were readable from the installed
cache. Hash comparison matched 125 copied supporting resources.

The first fixture omitted documentation. Its inspection correctly reported
missing permissions and two-modes guides. The fixture was corrected to include
docs, scripts and README, the private copy was reinstalled, and the final probe
reported no missing resources. This was a probe-construction error, not an Atlas
packaging defect. Sessions using --ignore-user-config did not discover the pilot
skills, even in the invocation-override attempt.

Official packaging guidance accepts Claude-compatible manifests and recommends
root plugin.json for new portable packages. The successful existing-package
installation lets Milestone 2 focus on the host adapter; the final portable
layout and installed-cache update behavior remain Milestone 3 work.
[Plugin packaging](https://developers.openai.com/plugins/build/plugins).

### Role operations have usable local primitives

The tested task API supplied fresh starts and same-role follow-ups. Planner
revision 1 became amended revision 2 and then signed-off without granting human
approval. The implementor initially refused construction, then made two scoped
fixture commits during the authorized positive experiment. Eight regression
tests passed when the supervisor and replacement supervisor reran them.

The replacement supervisor detected a stale implementation commit in the dossier
and reconciled it against the current worktree and durable receipts. It retained
review, human smoke-test and merge gates instead of declaring the run complete.

Fresh starts were requested explicitly. Child observations were recorded before
file reads; the parent's private marker value was never sent or written. This
checks behavior and the chosen context API, not the provider's hidden context
assembly. Recheck actual adapter roles before claiming fresh-context support.

### Role instructions do not substitute for permission boundaries

A read-only CLI source append failed with operation not permitted and unchanged
hashes. In a second CLI session, source outside the journal writable root was
denied while the journal receipt succeeded. Temporary-directory write exclusions
were necessary to avoid granting the sibling source access through a broad temp
root. They also blocked a shell here-document and produced tool-cache warnings;
the receipt was written directly without retrying the source append.

The tested task spawn API has no per-child sandbox setting. Instructing native
researchers to be read-only is therefore not equivalent to the CLI enforcement
experiment. Milestones 2 and 4 must prove a native role configuration or use a
separate session with the required boundary. The documented sandbox temp
exclusion settings informed the CLI experiment.
[Configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference).

The dry rule checker forbade gh pr merge and returned no match for gh api with a
merge endpoint. This reports a coverage gap, not an executed or permitted merge.
The tool inventory also exposed merge_pull_request and enable_auto_merge
connectors; neither was called. Shell rules do not establish a universal merge
barrier. Per-tool restrictions and actual adapter behavior need their own tests.
[Command rules](https://learn.chatgpt.com/docs/agent-configuration/rules).

### Preserve separate host settings

Recommended setup remains ~/.claude/atlas.json for Claude and ~/.codex/atlas.json
for local OpenAI use, subject to Work access validation in Milestone 3. Both may
point at the same journal. Explicitly copy confirmed journal/tracker choices
when onboarding; never silently migrate or fall back across host configs.
Keep credentials and permissions in native controls. A single supervisor owns
each run. This milestone installed no Atlas config at either host path.

## Work participation and remaining checks

The desktop-control tool explicitly blocked access to the ChatGPT app. We did
not route around that restriction. It prevents this session from launching a
live Work probe; it does not establish a product incompatibility. The runbook
contains an operator-run local Work prompt and the remaining test sequence.

Work's documented hosted subagents make shared local-file access a specific
uncertainty. Test the actual parent's and child's paths/environment before
offering kit mode or a manual relay. Do not substitute a cloud container for
local execution or simulate independent roles in one chat.
[Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents).

Before Milestone 1 is fully closed, record Work's results or explicitly revise
the supported target. Before advertising any mode, also repeat the pending
context/permission/tool-path checks on the actual adapter and run the later
end-to-end pilot. Existing Claude roles, skills, templates and manifests are
unchanged by this branch; a live Claude regression run remains a later gate.

Validation completed here: four probe-inspector tests, eight fixture regression
tests, cache/resource inspection, role experiments, file/branch/hash checks and
dry command-policy checks. lint-isms refused locally because the private blocklist
path was unavailable. CI rejected four raw-output evidence entries; those were
replaced with structured source/hash observations. The required gate is unchanged
and must pass on the updated PR before merge.
