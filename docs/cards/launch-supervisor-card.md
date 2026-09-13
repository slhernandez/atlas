# 🚌 /atlas:launch-supervisor

**Boots a supervisor for the biggest features. Researched, ruled, and ready before the window opens.**

| | |
|---|---|
| **Card** | Atlas Skill Card 04 |
| **Invoke** | `/atlas:launch-supervisor <epic>` |
| **Mode it serves** | Manual multi-window relay: separate windows per role, you as the bus |
| **Output** | One copy-paste kickoff prompt in `<journal>/plans/` |
| **Not for** | Work that fits one plan and one PR; that's `/atlas:feature-workflow` |

## What it does

Rung three. For a feature too large for one session, the roles run as separate Claude Code windows and you relay the artifacts between them. This skill writes the **kickoff prompt for the supervisor window**: a self-contained brief with the feature's north star in the stakeholders' own words, verified starting facts cited at file:line, decisions settled before work begins with their boundaries written down, the phase sequence, and the standing rules that cost time last time.

The hard rule that earns the skill: **research before writing**. A prompt assembled from the work item alone is worth little; the new window would read the item anyway. The value is the verified facts, especially the ones that correct a likely assumption.

## How to run it

```
/atlas:launch-supervisor EPIC-7
```

It gathers the brief and any richer sources in the journal, establishes facts in the code, puts before-work decisions to you as specific questions, chooses the phase shape honestly (execution relay, or independent proposal windows with a disqualifier test when the first phase is genuinely research), and picks the launch repository by where your accumulated memory lives. Then it writes the prompt to a file and tells you the path. You paste it into a new window.

## What the supervisor window inherits

- **The dossier**, created in its first session, resumable from itself alone through an opening RESUME BLOCK: current phase, live threads, pending prompts verbatim, standing rules.
- **The commit ledger**: every commit on every branch in plain language plus a summary for QA and product, so humans can exercise a real merge gate over work too large to read as a diff. Events and decisions go in the dossier, never the ledger.
- **The idempotent-receiver rule**: with many windows, you will re-deliver a message now and then. The supervisor answers "already reviewed, verdict stands" instead of re-running the work.

## Ground rules

- The supervisor authors every downstream prompt and verifies every artifact at file:line against origin, never a subordinate's summary.
- You approve specs and plans; you merge every PR. The supervisor never merges.
- Sessions are expected to die. The dossier, not the conversation, is the memory.
- A worked example ships beside the skill at `references/example-kickoff.md`. Match its altitude, not its content.

---
*rung three: brief → verified facts → rulings → one prompt that boots a supervisor window · [Deck index](../deck.html) · [README](../../README.md)*
