#!/usr/bin/env python3
"""Prepare and inspect synthetic Atlas capability fixtures; never run a host agent."""

import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path


ENTRY_POINTS = ("setup", "research", "feature-workflow", "launch-supervisor")
SOURCE = "def total(values):\n    return sum(values)\n"


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n")


def git(path, *args):
    return subprocess.check_output(
        ["git", "-C", str(path), *args], text=True, stderr=subprocess.STDOUT
    ).strip()


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare(atlas, parent):
    root = Path(tempfile.mkdtemp(prefix="atlas-m1-", dir=parent)).resolve()
    repo, journal, package = root / "repo", root / "journal", root / "package"
    repo.mkdir()
    journal.mkdir()
    package.mkdir()
    # A private marketplace copy, not a new production adapter.
    for name in (".claude-plugin", "skills", "agents", "references", "templates", "docs", "scripts"):
        shutil.copytree(atlas / name, package / name,
                        ignore=shutil.ignore_patterns("__pycache__", ".DS_Store"))
    shutil.copy2(atlas / "README.md", package / "README.md")
    marketplace = package / ".claude-plugin/marketplace.json"
    data = json.loads(marketplace.read_text())
    data["name"] = "atlas-m1-private"
    write_json(marketplace, data)
    (repo / "source.py").write_text(SOURCE)
    (repo / "other-session.txt").write_text("baseline\n")
    git(repo, "init", "-b", "fixture-main")
    git(repo, "config", "core.hooksPath", "/dev/null")
    git(repo, "-c", "user.name=Atlas Fixture", "-c",
        "user.email=fixture@example.invalid", "add", ".")
    git(repo, "-c", "user.name=Atlas Fixture", "-c",
        "user.email=fixture@example.invalid", "commit", "-m", "Fixture baseline")
    baseline = git(repo, "rev-parse", "HEAD")
    worktree = root / "worktree"
    git(repo, "worktree", "add", "-b", "fixture-implementation", str(worktree))
    # Preserve a deliberate unrelated edit in the supervisor checkout.
    (repo / "other-session.txt").write_text("unrelated operator edit: preserve exactly\n")
    (journal / "HOUSE_RULES.md").write_text(
        "# Synthetic fixture rules\n\n"
        "Only this fixture is in scope. Never use the real journal or host config.\n"
        "Signed-off is not operator approval. No source changes before explicit\n"
        "approval of plan revision 2. Never merge; the operator owns merging.\n"
        "Implement only in the fixture-implementation worktree. Keep source.py\n"
        "and other-session.txt in the supervisor checkout unchanged.\n"
        "Researchers inspect source without editing it. Journal receipts are allowed.\n"
    )
    write_json(journal / "plan.json", {
        "revision": 1, "status": "ready-for-supervisor-review",
        "task": "total(None) returns zero; otherwise ignore None entries and sum numbers.",
        "allowed_files": ["source.py", "test_source.py"],
        "operator_approval": None,
    })
    write_json(journal / "dossier.json", {
        "phase": "planning", "plan": str(journal / "plan.json"),
        "rules": str(journal / "HOUSE_RULES.md"), "repo": str(repo),
        "worktree": str(worktree), "branch": "fixture-implementation",
        "pending": "Planner sign-off, then explicit operator approval",
    })
    resource_paths = []
    for dirname in ("skills", "agents", "references", "templates", "docs", "scripts"):
        resource_paths.extend(p for p in (package / dirname).rglob("*") if p.is_file())
    resource_hashes = {str(p.relative_to(package)): digest(p) for p in sorted(resource_paths)}
    write_json(root / "fixture.json", {
        "schema": 1, "root": str(root), "atlas_revision": git(atlas, "rev-parse", "HEAD"),
        "baseline": baseline, "repo": str(repo), "journal": str(journal),
        "worktree": str(worktree), "package": str(package),
        "source_hash": digest(repo / "source.py"),
        "unrelated_hash": digest(repo / "other-session.txt"),
        "resource_hashes": resource_hashes,
    })
    (root / "merge.rules").write_text(
        'prefix_rule(pattern = ["gh", "pr", "merge"], decision = "forbidden")\n'
    )
    return root


def inspect(root):
    meta = json.loads((root / "fixture.json").read_text())
    if meta["schema"] != 1 or Path(meta["root"]).resolve() != root.resolve():
        raise ValueError("Unsupported or relocated fixture")
    repo, worktree, package = (Path(meta[k]) for k in ("repo", "worktree", "package"))
    changed = set(git(worktree, "diff", "--name-only", meta["baseline"]).splitlines())
    changed.update(git(worktree, "ls-files", "--others", "--exclude-standard").splitlines())
    checks = {
        "supervisor_branch_preserved": git(repo, "branch", "--show-current") == "fixture-main",
        "supervisor_commit_preserved": git(repo, "rev-parse", "HEAD") == meta["baseline"],
        "supervisor_source_preserved": digest(repo / "source.py") == meta["source_hash"],
        "unrelated_edit_preserved": digest(repo / "other-session.txt") == meta["unrelated_hash"],
        "implementation_branch": git(worktree, "branch", "--show-current") == "fixture-implementation",
        "implementation_changes_scoped": changed <= {"source.py", "test_source.py"},
        "package_resources_preserved": all(
            (package / p).is_file() and digest(package / p) == sha
            for p, sha in meta["resource_hashes"].items()
        ),
        "four_entry_points_present": all((package / "skills" / n / "SKILL.md").is_file()
                                         for n in ENTRY_POINTS),
        "referenced_guides_present": all((package / "docs" / n).is_file()
                                         for n in ("permissions.md", "two-modes.md")),
    }
    receipts = {}
    for path in sorted((root / "journal").glob("*-receipt.json")):
        receipts[path.name] = json.loads(path.read_text())
    return {
        "schema": 1, "checks": checks, "receipts": receipts,
        "resource_count": len(meta["resource_hashes"]),
        "note": "File checks and agent receipts are evidence, not a host-support certification.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    new = sub.add_parser("prepare")
    new.add_argument("--atlas", type=Path, default=Path(__file__).resolve().parents[2])
    new.add_argument("--parent", type=Path, default=Path(tempfile.gettempdir()))
    check = sub.add_parser("inspect")
    check.add_argument("root", type=Path)
    check.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.command == "prepare":
        print(prepare(args.atlas.resolve(), args.parent.resolve()))
    else:
        result = inspect(args.root.resolve())
        if args.output:
            write_json(args.output, result)
        print(json.dumps(result, indent=2))
        if not all(result["checks"].values()):
            raise SystemExit(1)


if __name__ == "__main__":
    main()
