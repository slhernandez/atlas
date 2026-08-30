# Permissions — the doorman pattern

Atlas's implementor runs long unattended stretches, which is only safe inside boundaries.
Claude Code gives you three layers; Atlas never edits any of them for you.

1. **The deny rail** — commands that never run, no discussion. Recommended floor:

```json
{
  "permissions": {
    "deny": [
      "Bash(git push --force:*)", "Bash(git push -f:*)",
      "Bash(git reset --hard:*)", "Bash(git clean:*)",
      "Bash(git worktree remove --force:*)",
      "Bash(gh pr merge:*)", "Bash(gh repo delete:*)",
      "Bash(rm -rf:*)"
    ]
  }
}
```

`gh pr merge` on the deny rail is the mechanical form of Atlas's core promise: merge is
never automated — the deny rail makes that true even if a prompt goes wrong.

2. **The allow list** — the safe regulars (reads, searches, your build/test commands) so
   agents run at full speed without paging you constantly. Build yours from what you
   actually approve during the first few runs; approvals accumulate.

3. **Everything else prompts.** That's the design, not a defect: you are only interrupted
   for decisions with a blast radius. Expect the first run to ask often, and expect that
   to fade. If a prompt appears for something the allow list should obviously cover,
   that's an allow-list gap — fix the list, and note it in the run's scorecard friction
   log.

Deliberate non-defaults: no service-level cloud wildcards (an `aws *`-style allow is how
write access sneaks in); mutating one-offs stay literal, never generalized.
