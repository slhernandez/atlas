---
name: grade
description: Independently grade one finished feature-workflow run (Part 3 of its scorecard, the measurement rows and the grade) from a fresh session that did not run the work. Use when the operator says "grade the run", "grade <work item>", or "/atlas:grade". Takes a work-item key. Never used by the run's own session.
---

# Grade a run

The writer is never the grader. A feature-workflow run fills Parts 1, 2, 4 and 5 of its own scorecard. Part 3, the grade and the measurement rows come from **this** skill, in a session that did not run the work. It re-reads the outcome, re-runs the new tests, breaks the code on purpose to prove the tests catch it, and measures cost and time from the run's transcript.

**Writes only:** the run's scorecard and files in this session's scratchpad. Never the run's code, its PR, the tracker, or the operator's working trees.

Resolve `<journal>` from `~/.claude/atlas.json` (or `$ATLAS_JOURNAL`). Read `<journal>/HOUSE_RULES.md` first; it is senior to this file.

## Step 0 — Stop if you are not independent

Locate the run session with the script in this skill's `scripts/` folder:

```bash
python3 <this skill's directory>/scripts/run_stats.py --find <work-item>
```

**Stop and say so** if any of these is true:
- the session it finds is this one;
- you took part in the run;
- the scorecard already has an independent grade, unless the operator asked for a re-grade.

## Step 1 — Gather the record

- **Scorecard:** `<journal>/scorecards/*-<work-item>-*.md`. It may not exist yet if the run is graded at PR submission.
- **Artifacts:** the research doc, plan and review under `<journal>/research/`, `plans/` and `reviews/`.
- **Grader notes:** `<journal>/grader/`, if the operator staged expectations there. The run's journal search skips that folder. Grade against them, and never copy their private lines into anything the run can read.
- **The work item:** read it from the configured tracker. Grade against what was asked, not against the plan alone.

## Step 2 — The PR, on the remote

Find the PR by work-item key, then note its state, base, head SHA, merge commit and its changed-file, addition and deletion counts. Fetch the base and the PR head.

**Find the PR's own base (`B`) before diffing.** A merged PR's head is already inside `origin/<base>`, so `origin/<base>...<head-sha>` comes back **empty** after a merge.
- **Open PR:** `B=$(git merge-base origin/<base> <head-sha>)`.
- **Merged PR:** take the parent of the commit it landed in: `B=$(git merge-base <merge-commit>^1 <head-sha>)`. This works for merge commits, squash merges and rebase merges alike.
- **Check `B`:** `git diff --shortstat $B <head-sha>` must match the PR's own counts. If it doesn't, stop and work out why before grading.

Read the whole `git diff $B <head-sha>`, not hunks, and every commit message (`git log $B..<head-sha>`). The scorecard cites the head SHA and `B` you graded.

## Step 3 — Re-run the tests and break the code

Work in a **scratch worktree in this session's scratchpad**, never in the operator's checkout:

```bash
git -C <repo> worktree add --detach <scratchpad>/grade-<work-item> <head-sha>
```

1. **Run the PR's new and changed tests**, using the repo's test command (from its CLAUDE.md or HOUSE_RULES). If a test selector can match nothing and still pass, confirm the count is above zero.
2. **Mutation checks.** Take the checks the plan or the implementor listed, plus **up to two of your own** aimed at the behaviour the work item cares about most. For each check:
   - break the guarded line;
   - confirm the guarding test **fails for the right reason**;
   - restore the line (`git -C <scratch> checkout -- .`) and confirm the test passes again.

   A test that still passes with its guard removed protects nothing; record it as a finding.
3. **Clean up:** `git -C <repo> worktree remove <scratch>`. The worktree must be clean first; never use `--force`.

If a check can't run, say which and why. Don't skip it silently.

## Step 4 — Measure the run

```bash
python3 <this skill's directory>/scripts/run_stats.py <session-id-from-step-0> --key <work-item>
```

`--key` starts every timing and the cost-to-PR at that work item's launch, even when the session held earlier work. It prints:
- launch → PR open, and how much of that was waiting on a person;
- spawns by agent type, with model and effort, verified from the transcript;
- active minutes per role;
- tokens per role and the cost at list price.

Copy the numbers into the scorecard's **Models / effort**, **Tokens and cost** and **Time** rows. Two limitations to note on the scorecard:
- **The cost is transcript-based** and runs slightly under `/usage`; a `/usage` reading the run recorded wins.
- **The session may contain other work** after the run. Say so when it does.

## Step 5 — Write the grade

**Never replace an existing scorecard.** If the run's close-out already wrote one, edit only these parts of it:
- the frontmatter `graded:` and `grade:` lines;
- the measurement rows (Models / effort, Tokens and cost, Success, Time);
- **Part 3**;
- one grader line at the top of **Part 5**.

Leave the rest as written. If no scorecard exists yet, copy `<journal>/scorecards/_template.md`, fill only the parts above, and leave the rest for the close-out.

**Part 3** answers, with file:line and the head SHA:
- **Fresh re-read:** defects the run's own review missed, each with a concrete failure scenario. Anything without one is a question.
- **Alignment, both ways:** everything asked was delivered or explicitly deferred at a gate, and nothing shipped that wasn't asked.
- **Tests:** which ran, how many, and each mutation check with its result.
- **Grader-note expectations:** each one, met or missed.
- **Redundancy:** which components were spawned, and whether each earned its keep this run (verified from Step 4).

**Grades:**
- **A:** outcome clean on independent re-read, mutation checks reproduce, both hard gates held.
- **B:** shipped correctly, but with process slips, a defect caught only late, or a test that doesn't guard what it claims.
- **C:** a defect reached merge, or a hard gate was broken.
- **F:** aborted, or shipped broken.

## Step 6 — Report in chat

Open with 3–6 sentences a reader who never saw the run can follow: what was asked, what shipped, the grade and why. Then:
- the measurement rows;
- every defect or weak test, with file:line;
- the redundancy answers;
- the scorecard path.

Post nothing on the PR or the tracker.
