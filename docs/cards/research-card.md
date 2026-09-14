# 🔍 /atlas:research

**Research first. Then fix in-session, or escalate with the document in hand.**

| | |
|---|---|
| **Card** | Atlas Skill Card 02 |
| **Invoke** | `/atlas:research <work item or question>` |
| **Output** | A research document in `<journal>/research/` |
| **Team** | Codebase locator, analyzer, pattern-finder; journal locator and analyzer |
| **Exit** | Fix in-session, or hand the document to `/atlas:feature-workflow` |

## What it does

The first rung of the ladder. Give it a work item or a plain question and it fans out read-only subagents, verifies their load-bearing claims itself at file:line, and writes a research document future runs will trust: where things live, how they actually work today, the closest existing pattern, prior decisions from the journal, a scope assessment, and open questions.

Why research comes before any fix: the wrong-root-cause trap. Fixing the symptom a bug report names is the most common way assisted bug work goes wrong. Research separates what the report says from what the code does before anyone edits anything.

## How to run it

```
/atlas:research #42
/atlas:research "why does the history view skip days?"
```

It reads the work item's description **and** comments, decomposes the question, and scales the team to it. A one-file lookup gets no agents at all. A broad architectural question gets four or more in parallel. Substantial runs also get a skeptic: one independent agent whose only job is to disprove the conclusions; surviving objections become open questions.

## Two exits

- **The fix is now obvious and small.** Do it in the same session, no ceremony.
- **The research shows structural work** (three or more tasks, an open design question, shared code with many call sites). Hand the document to the feature workflow: `/atlas:feature-workflow #42 "research: <path>"`. Its Phase 0 starts from your document instead of from scratch.

## Ground rules

- Live code outranks the journal. Journal findings are history, never the source of truth.
- Every claim carries `file:line`. The document is persistent and will be trusted, so the load-bearing claims are re-read before they are written down.
- While the skeptic is still running the document is marked `pending-skeptic`; it becomes `current` only after the objections land. The answer is delivered meanwhile, with that caveat said aloud.
- The document must stand alone. A reader with none of this context should understand it.

---
*rung one of the ladder: question → verified document → fix in-session, or → /atlas:feature-workflow · [Deck index](../deck.html) · [README](../../README.md)*
