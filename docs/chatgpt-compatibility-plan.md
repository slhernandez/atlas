# Plan: adapt Atlas for ChatGPT and Codex

Date: 2026-10-03

Status: approved 2026-10-04; Milestone 1 Codex evidence recorded, Work validation pending

Atlas should retain one factory protocol, with small adapters for each execution environment. The adaptation succeeds when an OpenAI run preserves the same independent checks, durable records, scope discipline, and human gates as a Claude Code run.

## Proposed first release

Start with the ChatGPT desktop app: ChatGPT Work with local access and local Codex. Prove each mode separately before claiming support. Keep Claude Code working throughout. The operator approved this target on 2026-10-04.

Use the existing four entry points: setup, research, feature workflow, and launch supervisor. Their purpose and outputs stay the same; invocation and execution depend on the host. Ordinary ChatGPT conversations can explain findings and discuss scope. Full factory execution requires verified access to the repository, journal, build tools, and permitted actions.

Initially validate manual briefs and GitHub Issues. Add Jira to the verified support matrix after a live tracker test. Cloud-only execution, a custom UI, an API-based orchestrator, and public-directory publication are later decisions. They are not prerequisites for a local pilot.

## What must survive the adaptation

- Research describes live code, verifies important claims at file:line, consults journal history, and includes the skeptic when required.
- The planner and implementor start without the supervisor's conversation history. The implementor receives the signed-off plan and required operating instructions, without the research.
- The supervisor checks artifacts directly, maintains the plan, and filters feedback into scoped fix tasks.
- Planner sign-off and operator approval remain distinct. No implementation begins before explicit operator approval of the current plan.
- Merge belongs to the operator. Cleanup waits for merge confirmation and never force-removes unfinished work.
- HOUSE_RULES outranks Atlas defaults, within the host's instruction and security boundaries. Setup preserves operator content and does not silently modify host permissions.
- Dossiers, plans, ledgers, reviews, and scorecards remain durable files. Current code outranks journal history.
- Human smoke tests, isolated commits, declared deviations, and independent grading remain part of the contract.

## Evidence and the main uncertainty

Official documentation provides a direct packaging route: skills can serve ChatGPT and Codex, and a plugin can distribute them. A skill needs a SKILL.md with name and description; OpenAI UI metadata is optional. [Build skills](https://learn.chatgpt.com/docs/build-skills).

New plugin packages use root plugin.json; OpenAI-specific settings belong in extensions.com.openai. Claude-compatible and older Codex manifests are also accepted. This makes a shared package plausible, but installation alone does not prove Atlas's orchestration works. [Package your plugin](https://developers.openai.com/plugins/build/plugins).

ChatGPT Work and Codex expose subagents. Work's subagents run in a hosted environment; local Codex also supports custom agents and follow-up orchestration. These facts do not establish identical file access or context isolation across hosts. [Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents).

Desktop Work can use available local tools. Eligible cloud-coordinated Work can continue in a container when the computer is unavailable; that container cannot access the computer's files or tools. Atlas must detect a missing execution environment and stop rather than treat it as equivalent. [Get started with Work](https://learn.chatgpt.com/docs/get-started-with-work).

The first implementation decision therefore depends on an experiment: can each role independently read and update the same intended artifacts, maintain its identity through revisions, and operate within Atlas's boundaries?

## Milestone 1 — prove the execution contract

Progress: [the capability report](compatibility.md) records local Codex experiments,
permission limits and the outstanding Work validation. No production adapter or
end-to-end supported OpenAI mode is claimed by this milestone.

Use a disposable repository and journal. Record the client version, execution environment, available tools, approval behavior, and supported modes in a compatibility report. No private journal or real user data is needed.

| Check | Evidence required | Consequence if it fails |
|---|---|---|
| Skill installation | All four entry points resolve their packaged references and templates | Fix packaging before any workflow pilot |
| Shared files | Parent and child read the same fixture; allowed progress writes return to the intended journal | Do not advertise kit mode on that environment |
| Fresh context | A private supervisor-only marker is absent from a child's initial history; inspect context behavior as well as its answer | Use independently started role sessions if they can pass the same check |
| Role continuity | The same planner accepts amendments; the same implementor accepts a fix round | Document the supported relay and recovery procedure |
| Branch isolation | An implementor works in the intended worktree; unrelated checkout edits remain untouched | Block unattended construction |
| Permissions | Research cannot change source; required journal writes and verification commands are permitted | Specify the least necessary access or use a manual route |
| Human gates | A request to build before approval is refused; a merge request is refused | Do not release that mode |
| Recovery | A replacement supervisor resumes using rules and files, without the old transcript | Repair the artifact contract before long-running support |

Test tool/API paths as well as shell commands. A blocked gh command does not prove that a GitHub connector cannot merge. Use harmless fixtures and policy checks rather than attempting destructive operations.

Output: a capability matrix distinguishing verified support, planned support, and unsupported behavior. Do not simulate independent roles inside one conversation as a fallback. Where shared files or isolation cannot be established, offer a verified manual relay or stop with an explanation.

## Milestone 2 — separate factory rules from host instructions

Extract shared workflow and role contracts into reusable references. Keep entry-point skills short enough to discover reliably. Each adapter supplies how to read files, ask questions, start and continue roles, wait for completion, and report failures.

| Existing coupling | Proposed adaptation |
|---|---|
| Claude slash commands | Document actual invocation on each host; test natural-language discovery and explicit selection |
| Claude-specific tool names and SendMessage | Describe the operation in the shared protocol; map it to verified host tools |
| Agent Markdown frontmatter | Preserve Claude definitions; provide OpenAI role resources or optional custom-agent configuration where tested |
| CLAUDE.md assumed to auto-load | Resolve host guidance explicitly; on Codex respect the AGENTS.md hierarchy, and read legacy project guidance when needed |
| Claude project-memory paths | Choose the launch repository from durable project context, with host memory only as an optional pointer |
| Launcher always invokes claude | Add an explicit host selection while retaining the current default and argument handling |
| Claude permission JSON | Supply separate host guidance with tested limits |

Codex discovers repository instructions through AGENTS.md and its overrides. The adapter must respect that hierarchy, not replace it with a global Atlas instruction file. [AGENTS.md guidance](https://learn.chatgpt.com/docs/agent-configuration/agents-md).

Keep one authoritative version of each factory rule. If native agent formats need generated copies, document their source and verify they remain consistent. Do not assume a plugin's agents directory automatically registers Claude-style roles in OpenAI hosts. Model and effort settings should use available host choices and remain operator-configurable.

Output: shared contracts plus Claude and OpenAI adapters. A Claude regression run must pass before progressing.

## Milestone 3 — add packaging, setup, and separate host configuration

Add the portable manifest and a tested OpenAI installation path. Retain the existing Claude marketplace entry. Verify installed-cache behavior and resolve references relative to the installed package, without paths into the developer's checkout. Publish publicly only after local validation.

Preserve separate host configurations. Claude Code keeps ~/.claude/atlas.json. The recommended OpenAI location is ~/.codex/atlas.json, shared by local Work and Codex only where its access has been verified. This path is a proposal for Milestone 3, not an installed configuration. Preserve journal, tracker, and tracker_detail as existing concepts. Resolve the journal with ATLAS_JOURNAL first, then the active host's Atlas config, then the documented default.

Both hosts may point at the same journal, so research and standing rules travel between them without coupling their installation or permission settings. Setup offers an explicit copy of confirmed Atlas values when onboarding a second host; it never migrates, overwrites, or silently falls back to the other host's config. Distinct tracker settings are allowed and must be recorded with each run's work-item identity. Only one supervisor owns a run at a time. Keep credentials and native permissions in the host or connector's own controls, outside Atlas's config and journal.

The OpenAI setup wizard should:

1. Identify the execution environment and which Atlas modes it can support.
2. Check git, repository access, identity, remote access, tracker access, and available verification tools.
3. Confirm journal and tracker choices; verify journal access for the roles that need it.
4. Seed missing templates without overwriting operator documents.
5. Prove the tracker with a real read, or state the manual-mode skip.
6. Write confirmed Atlas configuration last and explain permission setup separately.

When needed, provide narrow, reviewable access to the selected journal and worktree locations. Do not suggest unrestricted home-directory access or automatic edits to host security configuration.

## Milestone 4 — adapt gates, permissions, and recovery

Keep the existing plan status handshake. Add optional runtime metadata and an approval receipt identifying the exact plan revision the operator approved. The receipt records a human decision; an agent-written field is not independent proof of authorization. A substantive amendment must go through the applicable approval gate before construction continues.

Separate workflow approval from tool approval. Permission to write files or run commands never substitutes for plan approval. Automatic tool approval never permits Atlas to merge.

Codex command rules govern execution outside the sandbox; Work's local/cloud policies differ. Do not present a translated prefix list as universal enforcement. [Rules](https://learn.chatgpt.com/docs/agent-configuration/rules). Permission profiles also have version and configuration constraints. [Permissions](https://learn.chatgpt.com/docs/permissions).

Document and test the actual protective boundary on each supported host: shell, connectors, browser actions, and any enabled API tools. Preserve Atlas's deny-rail floor and its honest limits. If a proposed unattended mode cannot meet that floor, label it unsupported and offer the verified manual route.

Recovery must record artifact paths, branch/worktree identity, current phase, pending questions, and last verified revision. Prevent concurrent supervisors from owning the same run. Re-delivered messages return the recorded verdict. Host changes require verification of files and branch state; an unavailable computer must not cause a silent restart against an empty cloud environment.

Output: working plan and merge gates, host-specific permission guidance, recovery procedure, and truthful start/finish/blocked notices.

## Milestone 5 — validate complete factory runs

Run the same bounded work item through Claude Code and each claimed OpenAI mode. Compare protocol and outcome, without requiring identical code or language. Manually launched, genuinely independent graders remain sufficient for this release.

Required scenarios:

- Setup from an empty environment, setup rerun, and explicit legacy-config import.
- Research with journal history, stale findings, and a skeptic objection.
- Plan hold, amendments, planner sign-off, and explicit operator approval.
- Construction in a worktree, pre-existing verification failures, and a declared deviation.
- A design-change halt and a scoped reviewer-fix round.
- A deferred work item that must remain open after the PR merges.
- Human merge confirmation followed by close-out; unfinished worktrees are preserved.
- Session replacement, duplicate relay delivery, and loss of local access.
- A multi-slice manual-mode run with dossier and ledger updates.
- Independent review and a mutation check proving the regression test detects removal of the fix.

Use small fixtures for deterministic checks and real supervised pilot runs for behavior that static tests cannot prove. Preserve the existing lint-isms gate; its private blocklist requirement remains in force.

Release acceptance: every advertised mode has an end-to-end record; both human gates hold; role isolation is verified; artifacts survive replacement sessions; no permission settings or operator content are overwritten; and Claude support still passes.

## Milestone 6 — document and release

Update README, quick start, Deck, glossary, two-modes guide, permissions, and launcher examples with separate host paths and a clear support matrix. Distinguish the manual tracker option from the manual multi-session workflow.

Publish supported versions and environments, known limitations, config precedence, installation/update behavior, and recovery instructions. Validate on a fresh machine or profile. Use a compatibility release version chosen after the pilots. Public plugin submission is a separate action after the package is reviewable and the operator authorizes publication.

## Suggested implementation slices

| Slice | Deliverable | Likely files |
|---|---|---|
| 1 | Capability report and disposable validation fixtures | docs/compatibility.md; validation resources |
| 2 | Shared contracts and Claude-preserving adapters | references/; skills/; agents/ |
| 3 | OpenAI package, setup, config resolution, launcher | plugin.json; adapter resources; skills/setup/; scripts/ |
| 4 | Full workflow gates and recovery | skills/feature-workflow/; skills/launch-supervisor/; templates/; docs/permissions.md |
| 5 | Pilot evidence and independent grading | validation resources; pilot journal artifacts |
| 6 | User documentation and release preparation | README.md; docs/; manifests |

These are planning boundaries. The capability report determines the final adapter layout and whether OpenAI kit mode can ship alongside manual mode.

## Operator decisions — 2026-10-04

1. Local desktop Work and Codex first; cloud-only support is deferred.
2. Accept a verified manual relay if Work cannot satisfy the kit-mode contract. An execution bridge is not part of the pilot.
3. Preserve separate host configs. A shared journal is recommended; the OpenAI config path is finalized during setup work after access testing.
4. Keep installation personal/private during the pilot. Work on a branch and review through a PR; leave main unchanged and never merge automatically.
5. The plan is approved. Proceed with Milestone 1; later milestones are not implemented by this probe.

Milestone 1 resolves the costly uncertainties before Atlas's instructions or packaging are restructured. The capability report must distinguish observed behavior, documented capabilities, and tests still pending operator participation.
