# House Rules

Your standing rules. Every Atlas skill and agent reads this file before working and treats
it as **binding — senior to the plugin's own defaults**. It survives every plugin update.

Format: one bold rule per bullet, with the *why* — a rule whose reason is recorded outlives
the person who remembers it. Feed this file from scorecards' friction logs.

Who writes here: **you**. Atlas records a rule here only when you set it at a gate (with its
why); rules it derives from a run's frictions are proposed in RUN COMPLETE for you to accept
or reject.

- **Merge is never automated.** Why: judgment stays where judgment lives. (This one is not
  removable; it restates the plugin's own hard gate so the file starts non-empty and true.)
- **Test commands for each repo live in that repo's CLAUDE.md** — record them there, not
  here. Why: Claude Code loads CLAUDE.md automatically; this file is for cross-repo rules.
- **<your first real rule goes here>** Why: <the friction that taught it>.

## Extra notes directories
<absolute paths the research team should search beyond this journal — meeting notes, a
design/spec repo, ticket notes. Empty is fine.>

## Per-repo notes
<worktree bootstrap commands for repos whose toolchain files are gitignored; anything an
implementor needs that a fresh worktree won't carry>
