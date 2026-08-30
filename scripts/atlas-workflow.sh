#!/usr/bin/env bash
# Launch the supervised three-role feature workflow (supervisor → planner → implementor)
# in a single interactive Claude Code session, from anywhere inside your repo.
#
# Usage:
#   atlas-workflow.sh TICKET-123 [extra context...]
#   atlas-workflow.sh 42 [extra context...]          (GitHub issue number)
#   atlas-workflow.sh <work item URL> [extra context...]
#
# The session runs interactively on purpose: the workflow has two human gates
# (plan approval, PR merge) that need you at the keyboard.

set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $(basename "$0") <work item id or URL> [extra context...]" >&2
  exit 1
fi

ITEM="$1"
shift
EXTRA="${*:-}"

# Normalize a tracker URL to a bare id where the shape is recognizable:
# Jira-style KEY-123 anywhere in the string, or a GitHub issue URL's number.
if [[ "$ITEM" =~ ([A-Z][A-Z0-9]+-[0-9]+) ]]; then
  ITEM="${BASH_REMATCH[1]}"
elif [[ "$ITEM" =~ /issues/([0-9]+) ]]; then
  ITEM="${BASH_REMATCH[1]}"
fi

# Run from the repo root so the session opens where the work is.
if ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"; then
  cd "$ROOT"
else
  echo "Atlas runs inside a git repository. cd into your project first." >&2
  exit 1
fi

PROMPT="/atlas:feature-workflow ${ITEM}"
if [[ -n "$EXTRA" ]]; then
  PROMPT+=" — additional context from the operator: ${EXTRA}"
fi

exec claude "$PROMPT"
