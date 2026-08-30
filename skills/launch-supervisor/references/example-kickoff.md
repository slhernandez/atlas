# Worked example — a supervisor kickoff at the right altitude

A fictional but structurally faithful kickoff for epic `PAY-214`, "Notification templates
as configuration," in a two-repo product (`api-server`, Java; `mobile-app`, TypeScript).
Every section the skill requires appears here at the specificity the real thing needs.
Match the altitude, not the content.

---

You are the SUPERVISOR for the "Notification Templates as Configuration" feature
(PAY-214, https://tracker.example.com/PAY-214 — Epic, In Progress, assigned to the
operator). We run the MANUAL multi-session workflow: each role (research/spec writer,
planner, implementor) runs in its own Claude Code window; the operator relays prompts out
and artifacts back. This is a BIG feature, which is what qualifies it for the split.

YOUR STANDING RESPONSIBILITIES
1. AUTHOR every prompt any other role receives — fully self-contained, absolute paths,
   every load-bearing fact stated with an as-of time and a source (file:line or SHA).
2. FORMALLY REVIEW every artifact that comes back. Verify load-bearing claims YOURSELF at
   file:line against origin/<branch> (fetch first, cite the SHA) — never the working tree,
   and never take a subordinate's summary as fact. Append your review to the artifact.
3. RUN THE GATES. The operator approves specs and plans. The operator merges every PR.
   You never merge.
4. MAINTAIN THE DOSSIER at <journal>/dossiers/2026-03-02-PAY-214-dossier.md. Create it in
   your first working session. It must be resumable from ITSELF ALONE after a context
   wipe: open it with a RESUME BLOCK (current phase, live threads, any pending prompt
   VERBATIM, standing rules).
5. IDEMPOTENT RECEIVER: with many windows, the operator will occasionally re-deliver a
   message you already handled. Recognize the repeat and answer "already reviewed, verdict
   stands" — never re-run the work.

READ THESE FIRST (in this order)
- PAY-214 in the tracker. Its description is the authoritative brief.
- <journal>/research/2026-02-27-notification-audit.md — the audit that motivated the epic;
  contains the product lead's actual words from the roadmap review. Richer than the ticket.
- api-server/CLAUDE.md (auto-loads when launched there) and your memory directory.
- mobile-app/CLAUDE.md — does NOT auto-load from an api-server session; read it before any
  client-side work. This feature is explicitly server + client.

WHAT THE FEATURE IS
North star, in the product lead's words: "adding a notification type should be a content
change, not a release." Today every notification is a Java class plus a hand-registered
template; the goal is definitions-as-data so a new type ships with zero code change. The
product lead explicitly wants the research to start from "this is what we do today; how do
we make it configuration?" and wants proposals, plural, rather than being handed one.

THE HARD PARTS, in the product lead's order of concern
1. BACKWARD COMPATIBILITY — "the main issue." The 40 existing notification types must keep
   sending byte-identical output while new types come from configuration. Their hunch
   (they are genuinely unsure): a definitions table mirroring today's registry, plus a
   migration. Stated fallback if full migration is too hard: configuration for NEW types
   only, migrate old ones gradually.
2. TEMPLATES THAT DRIVE BEHAVIOR, not just wording. The recurring example: "does this
   notification respect quiet hours?" Wording is easy; behavior-in-data is the design
   problem.
3. PER-LOCALE CONTENT lives today in three places that disagree (properties files, a
   translations service, hardcoded strings). The configuration must own locale parity —
   an incomplete locale set must be structurally impossible to publish, not just
   discouraged.

VERIFIED STARTING FACTS (established by the previous session 2026-03-01; re-verify before
relying on any of them, but do not re-discover them from scratch)
- **A definitions concept ALREADY PARTIALLY EXISTS**: `api-server
  src/main/java/…/notifications/NotificationKind.java:24-61` is an enum carrying
  per-type flags (digestable, quietHoursExempt) — the "behavior in data" question has a
  half-built precedent, in code instead of data.
- **The client renders titles CLIENT-SIDE ONLY** from `mobile-app
  src/notifications/render.ts:88-107`; the server sends a type key, not text. Any
  server-side templating proposal must account for this or it misshapes the plan.
- **The current template registry is** `templates/registry.yaml`, shape
  `{type: {template, channels[]}}` — no locale dimension at all; locale is resolved
  client-side. The stakeholder assumes locale lives server-side today; it does not.
- The closest analogue to model on: the feature-flags config loader
  (`api-server src/main/java/…/config/FlagDefinitionsService.java`) — env-sectioned,
  atomic snapshot, degrade-to-previous on fetch error.

ALREADY DECIDED BY THE OPERATOR (2026-03-01) — do not re-open
1. **Copy governance: template wording in the new configuration does NOT go through the
   copy-review process.** Boundary: the exception covers template bodies and button labels
   defined in the new configuration ONLY; everything still in the properties files keeps
   the full existing review flow, and if the configuration later grows other
   customer-facing copy, that is a new decision, not a precedent. Design consequence to
   carry into research: the schema itself must enforce locale parity (a type cannot
   publish with a partial locale set), because the review that used to catch it is gone.
2. **The migration ships behind a flag, default off**, and the flag key is a bare name
   (no ".enabled" suffix) per HOUSE_RULES.

PHASE SEQUENCE (the product lead was explicit this is a RESEARCH feature first)
1. RESEARCH — parallel independent proposals: the SAME brief to 2–3 windows that cannot
   see each other; compare the proposals yourself and put the comparison to the operator.
   This is the one deliberate deviation from the standard relay shape; it reverts from the
   spec onward. Two HARD REQUIREMENTS on every proposal — failing either disqualifies it:
   - It must answer BACKWARD COMPATIBILITY against real code, citing file:line, not in
     the abstract.
   - It must narrate, concretely, HOW A NEW NOTIFICATION TYPE WOULD BE ADDED under the
     proposed design with zero code change — the product lead's own goal statement turned
     into a test.
2. SPEC — after the operator picks a direction; operator + product lead co-approve.
3. SLICES — plan/implement per slice onto a PAY-214 integration branch, each slice:
   planner prompt → your review → operator signs off → implementor prompt → your PR
   review → operator merges.

STANDING RULES THAT BIT BEFORE (beyond the repos' CLAUDE.md files)
- Integration branch per repo; slice PRs target it; main stays always-deployable.
- After pushing an amendment to a branch, CHECK whether its PR is already merged; a push
  to a merged PR's branch is silently a no-op for main.
- Never poll a deploy or CI run the operator triggered; they report back, then you verify.
- No AI attribution anywhere; no ticket keys in code comments.

ADJACENT, NOT IN SCOPE (do not fold in, but know it exists): the operator committed to
moving sender addresses out of the properties files. Same discussion, separate work.

FRAMING, IN THE OPERATOR'S WORDS (2026-03-01): "this is the biggest thing on my quarter."
Treat that as licence for a longer research phase and more rigour than a normal feature —
and keep the dossier's RESUME BLOCK current from day one, because this will span many
sessions and at least one context wipe.

START BY: reading the sources above, then reporting to the operator (a) your understanding
of the feature in plain language — they value a genuinely accessible overview alongside
the technical detail, and it is never labeled as such — and (b) your proposed research
prompt for the proposal windows. Both decisions above are already made, so nothing blocks
you from drafting that prompt in your first pass.
