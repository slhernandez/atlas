#!/bin/bash
# lint-isms — fail if any origin-specific term appears anywhere in this tree.
# The blocklist is deliberately NOT part of this repository (it would leak the
# very terms it guards). Point ATLAS_ISMS_BLOCKLIST_FILE at your private copy;
# CI materializes it from the ATLAS_ISMS_BLOCKLIST repository secret.
set -euo pipefail

list="${ATLAS_ISMS_BLOCKLIST_FILE:-}"
if [ -z "$list" ] || [ ! -f "$list" ]; then
  echo "lint-isms: ATLAS_ISMS_BLOCKLIST_FILE is not set or not a file" >&2
  exit 2
fi

root="$(cd "$(dirname "$0")/.." && pwd)"
hits=$(grep -rniF --exclude-dir=.git --exclude-dir=.github -f "$list" "$root" || true)
# .github excluded only for the workflow that names the secret; scan it for
# everything except the secret's own name.
gh_hits=$(grep -rniF -f "$list" "$root/.github" 2>/dev/null | grep -v 'ATLAS_ISMS_BLOCKLIST' || true)

all="${hits}${gh_hits:+
$gh_hits}"
if [ -n "$all" ]; then
  echo "lint-isms: origin-specific terms found:" >&2
  printf '%s\n' "$all" >&2
  exit 1
fi
echo "lint-isms: clean"
