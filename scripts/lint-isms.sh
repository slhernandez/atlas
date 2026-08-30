#!/usr/bin/env bash
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

# Sanitize: a blank line in a -F pattern file matches EVERYTHING under GNU
# grep (and an empty pattern file matches everything under BSD grep). A
# tripwire must also refuse to run with no patterns at all.
patterns="$(mktemp)"
trap 'rm -f "$patterns"' EXIT
grep -v '^[[:space:]]*$' "$list" > "$patterns" || true
if ! grep -q '[^[:space:]]' "$patterns"; then
  echo "lint-isms: blocklist has no usable patterns" >&2
  exit 2
fi

root="$(cd "$(dirname "$0")/.." && pwd)"

# Main scan. The CI workflow file is excluded here only because it must name
# the secret; it is scanned separately below with just that name removed, so
# a real term sharing a line with it cannot hide. grep exit >= 2 is a scan
# failure and must never read as "clean".
set +e
hits=$(grep -rniF --exclude-dir=.git --exclude=lint-isms.yml -f "$patterns" "$root")
rc=$?
set -e
if [ "$rc" -ge 2 ]; then
  echo "lint-isms: scan failed (grep exit $rc)" >&2
  exit 2
fi
# Never self-match a blocklist file kept (gitignored) inside the tree.
hits=$(printf '%s\n' "$hits" | awk -v p="$list:" 'index($0, p) != 1' || true)

wf="$root/.github/workflows/lint-isms.yml"
wf_hits=""
if [ -f "$wf" ]; then
  set +e
  wf_hits=$(sed 's/ATLAS_ISMS_BLOCKLIST//g' "$wf" | grep -niF -f "$patterns")
  wrc=$?
  set -e
  if [ "$wrc" -ge 2 ]; then
    echo "lint-isms: scan failed on workflow file (grep exit $wrc)" >&2
    exit 2
  fi
  if [ -n "$wf_hits" ]; then
    wf_hits=$(printf '%s\n' "$wf_hits" | sed "s|^|$wf:|")
  fi
fi

all="$(printf '%s\n%s' "$hits" "$wf_hits" | grep -v '^[[:space:]]*$' || true)"
if [ -n "$all" ]; then
  echo "lint-isms: origin-specific terms found:" >&2
  printf '%s\n' "$all" >&2
  exit 1
fi
echo "lint-isms: clean"
