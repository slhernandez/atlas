# <Feature> — Commit Ledger

Every commit on the feature's branches and its default-branch PRs, in plain language, for
the people who cannot read 18,000 lines of diff: QA, product, reviewers, and you at the
merge gate. Maintained by the supervisor at every review or halt. Newest rows land at the
bottom of each table.

**Legend:** ✅ merged · 🔵 in PR, awaiting merge · 🟡 on a branch, PR not open yet

**Boundary:** this file holds the *summary* and the *commit tables* — nothing else. Events,
decisions, reviews, and state belong in the feature dossier (its History and RESUME BLOCK).
A ledger that starts logging events has become a second dossier; move the entry.

---

## Summary for QA and Product (updated YYYY-MM-DD)

**What this work is.** <two or three sentences a non-engineer can repeat in a meeting>

**What is live right now.** <what is merged, where it is deployed, whether any switch is on>

**What changes when it is switched on.** <the user-visible difference, per role if relevant>

**What QA should focus on.** <the cases that matter most, especially anything touching
*existing* behavior; name the regression that would be worst to miss>

**What was found and fixed along the way.** <bugs caught before release, pre-existing ones
called out separately, each with a regression test or an honest "none">

**What is still to come.** <numbered; include required drills or rollbacks, not just features>

**Documents:** <dossier path, plans, research, review docs — paths only>

---

## <repo name>

### <branch or "PRs straight to main"> → <PR link> into <target> (<slice/wave name>) — <status>

| Commit | What it does, plainly |
|---|---|
| `abc1234` | **<one bold clause naming the change>** — <what it does, why it is safe for existing behavior, what proves it (tests, byte-identical fixtures, gates)> |

### <next branch> …

## <second repo, if the feature spans repos>

…
