# Pattern: the generated-client dependency

When a client repo consumes a **generated** API client (OpenAPI or similar), a feature
spanning both repos has a fixed order, not two parallel tracks:

1. Server half ships **inert** — endpoints exist, nothing calls them. Reviewable alone,
   sits harmlessly on the default branch.
2. Server PR merges FIRST.
3. **Regenerate the client from a deployed or production-profile spec** — never from a
   local dev profile. Feature-flagged controllers that are gated off locally silently drop
   out of the generated spec, and the client build fails (or worse, quietly lacks
   endpoints) with no signal pointing at the cause.
4. The regenerated client lands as its own commit, named as such in the PR body, so any
   drift is reviewable in one place.
5. Only then does the client half build against the new types. Client PR merges second —
   the merge order is part of the protocol, not a preference.

Generated-code merge conflicts are not hand-mergeable: regenerate, never edit.
