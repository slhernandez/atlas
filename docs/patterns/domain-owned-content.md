# Pattern: domain-owned content

Some strings in a codebase are not engineering's to word: customer-facing copy, legal
text, pricing language. Two rules keep them safe in an AI-speed workflow:

1. **Route every engineer-authored change to the content's owner** — non-blocking (ship
   with the work, review after the fact) but not optional. A path-triggered check (CI on
   the files that hold the content) beats a process people must remember, because it
   fires on every route to the default branch including the ones that bypass sessions.
2. **When the owner authors the wording themselves, do NOT route it back to them** — the
   review already happened; a new review of their own words is a loop, not a safeguard.
   Reference the originating decision instead, and give the automation a way to see that
   reference so it stands down.

And when a design moves owned content somewhere the old review can't see (config, a
database), rebuild the lost safety **as a schema constraint** — e.g. locale parity the
publisher cannot skip — rather than relying on discipline.
