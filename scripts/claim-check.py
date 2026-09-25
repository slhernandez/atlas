#!/usr/bin/env python3
"""claim-check — shadow verification of a research document's code references.

Reads a finished research document, pulls every `path:lines — claim` bullet from its
references section, fetches the cited lines from the repository at the commit the document
was written against, and asks a judge one question per claim: does this excerpt support,
contradict, or say nothing about this claim? It writes a report and a JSONL log next to
your journal. It never edits the document and never gates anything.

    claim-check.py DOC.md [DOC2.md ...] [--repo PATH] [--repos name=path,...]
                   [--judge dry|jev] [--out DIR] [--context 3] [--max-lines 40]
    claim-check.py --self-test

Judges:
  dry   parse + excerpts only, no network (default)
  jev   TypeSafe Jev, needs TYPESAFE_API_KEY in the environment; the key is never logged

Repository resolution: relative paths are looked up first in the document's own repository
(frontmatter `repository`, matched by name against --repos / $CLAIM_CHECK_REPOS
`name=path,name=path`, or --repo), then in the other mapped repositories, since a backend
document may cite client files. A `name/` prefix that matches a mapped repository selects it.
Files are read only from inside a mapped repository root; absolute paths outside every root
are skipped, never read.

Output directory, in order: --out; $CLAIM_CHECK_OUT; $ATLAS_JOURNAL/claim-check; the
`journal` in ~/.claude/atlas.json + /claim-check; ./claim-check.

Python 3.8+, standard library only, so the request and response are fully visible in the log.
"""
import argparse
import json
import os
import random
import re
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib import error, request

API_URL = "https://api.typesafe.ai/v1/systemone"
AUTO_PASS = 0.8  # supports at or above this confidence would auto-pass if this were live
MAX_LINE_CHARS = 300

RELATION_CRITERIA = {
    "supports": "The excerpt states or directly implies that the claim is true.",
    "contradicts": "The excerpt states the opposite of the claim, or implies the claim is false.",
    "says_nothing": "The excerpt does not address the claim either way, or is not enough to judge it.",
}

# ── document parsing ──────────────────────────────────────────────────────────

FRONTMATTER_RE = re.compile(r"\A﻿?---\r?\n(.*?)\r?\n---\r?\n", re.S)
HEADING_RE = re.compile(r"^(#{1,4})\s+(.*)$")
REF_HEADING_RE = re.compile(r"references", re.I)
BULLET_RE = re.compile(r"^\s*[-*]\s+(.*)$")
REF_RE = re.compile(r"`([^`\s]+?)(?::([0-9][0-9,\-–\s]*))?`")
CONT_RE = re.compile(r"^\s*,?\s*`:([0-9][0-9,\-–\s]*)`")
LINE_SPEC_RE = re.compile(r"^\d+(?:[-–]\d+)?(?:\s*,\s*\d+(?:[-–]\d+)?)*$")
REF_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/@-]*$")  # git refs and shas we are willing to pass to git


def parse_frontmatter(text: str) -> Dict[str, str]:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}
    fm = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.startswith((" ", "\t", "-")):
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip().strip("'\"")
    return fm


def parse_line_spec(spec: str) -> List[Tuple[int, int]]:
    """'195-214' -> [(195,214)]; '53,76,85' -> [(53,53),(76,76),(85,85)]; mixed OK."""
    ranges = []
    for part in re.split(r"\s*,\s*", spec.strip()):
        if not part:
            continue
        a, _, b = part.replace("–", "-").partition("-")
        lo = int(a)
        hi = int(b) if b else lo
        if hi < lo:
            lo, hi = hi, lo
        ranges.append((lo, hi))
    return ranges


def split_claim(rest: str) -> str:
    return re.sub(r"^\s*(?:—|–|-|:)\s*", "", rest.strip()).strip()


def parse_references(text: str) -> Tuple[List[dict], List[dict]]:
    """Return (claims, skipped). A claim: {path, spec, ranges, claim, raw}.

    The references section starts at a heading whose text contains "references" and ends at
    the next heading of the same or higher level; deeper sub-headings stay inside it. Lines
    inside fenced code blocks are ignored."""
    claims, skipped = [], []
    in_section, level, fenced = False, 0, False
    for raw in text.split("\n"):
        if raw.lstrip().startswith("```"):
            fenced = not fenced
            continue
        if fenced:
            continue
        hm = HEADING_RE.match(raw)
        if hm:
            depth = len(hm.group(1))
            if REF_HEADING_RE.search(hm.group(2)):
                in_section, level = True, depth
            elif in_section and depth <= level:
                in_section = False
            continue
        if not in_section:
            continue
        bm = BULLET_RE.match(raw)
        if not bm:
            continue
        body = bm.group(1)
        m = REF_RE.search(body)
        if not m:
            skipped.append({"raw": raw.strip(), "reason": "no `path` token"})
            continue
        path, spec = m.group(1), m.group(2)
        rest = body[m.end():]
        if "..." in path or "…" in path:
            skipped.append({"raw": raw.strip(), "reason": "abbreviated path"})
            continue
        if not spec:
            cm = CONT_RE.match(rest)  # `path`, `:53-60` continuation form
            if cm:
                spec = cm.group(1)
                rest = rest[cm.end():]
        if not spec:
            skipped.append({"raw": raw.strip(), "reason": "no line spec"})
            continue
        spec = spec.strip()
        if not LINE_SPEC_RE.match(spec):
            skipped.append({"raw": raw.strip(), "reason": "unparseable line spec '%s'" % spec})
            continue
        claim = split_claim(rest)
        if len(claim) < 8:
            skipped.append({"raw": raw.strip(), "reason": "claim text too short"})
            continue
        claims.append({"path": path, "spec": spec, "ranges": parse_line_spec(spec), "claim": claim, "raw": raw.strip()})
    return claims, skipped


# ── excerpts ──────────────────────────────────────────────────────────────────

def git_env() -> Dict[str, str]:
    env = {k: v for k, v in os.environ.items() if k != "TYPESAFE_API_KEY"}
    env["GIT_TERMINAL_PROMPT"] = "0"
    return env


def git_bytes(repo: Path, *args: str) -> Optional[bytes]:
    """Run a read-only git command; document content never reaches git as an option."""
    try:
        out = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, timeout=30, env=git_env())
    except (OSError, subprocess.TimeoutExpired):
        return None
    return out.stdout if out.returncode == 0 else None


def git_blob(repo: Path, ref: str, rel: str) -> Optional[str]:
    if not REF_NAME_RE.match(ref) or rel.startswith("-"):
        return None
    if (git_bytes(repo, "cat-file", "-t", "--end-of-options", "%s:%s" % (ref, rel)) or b"").strip() != b"blob":
        return None
    data = git_bytes(repo, "cat-file", "blob", "--end-of-options", "%s:%s" % (ref, rel))
    return None if data is None else data.decode("utf-8", errors="replace")


def split_ref(path: str) -> Tuple[Optional[str], str]:
    """'origin/feature:src/x.java' -> ('origin/feature', 'src/x.java'); plain paths -> (None, path)."""
    if ":" in path and not path.startswith("/"):
        ref, _, rest = path.partition(":")
        if rest and ("/" in ref or re.fullmatch(r"[0-9a-f]{7,40}", ref)):
            return ref, rest
    return None, path


def inside(root: Path, p: Path) -> bool:
    try:
        p.resolve().relative_to(root.resolve())
        return True
    except (ValueError, OSError):
        return False


def repo_names_in(field: str, repos: Dict[str, Path]) -> List[str]:
    """Repo names mentioned as whole words in a free-text frontmatter field, in order of appearance."""
    hits = []
    for n in repos:
        m = re.search(r"(?<![\w-])%s(?![\w-])" % re.escape(n), field)
        if m:
            hits.append((m.start(), n))
    return [n for _, n in sorted(hits)]


def resolve_repos(fm: Dict[str, str], path: str, args, repos: Dict[str, Path]) -> Tuple[List[Path], Optional[Path], str]:
    """Return (candidate repos in order, the document's own repo or None, relative path)."""
    explicit_ref, path = split_ref(path)
    if explicit_ref:
        path = "%s:%s" % (explicit_ref, path)  # re-joined; file_lines splits it again
    own: Optional[Path] = None
    if args.repo:
        own = Path(args.repo).expanduser()
    else:
        named = repo_names_in(fm.get("repository", ""), repos)
        if named:
            own = repos[named[0]]
    first = path.split("/", 1)[0]
    if first in repos and "/" in path:
        prefixed = repos[first]
        rest = [p for p in [own] + list(repos.values()) if p and p != prefixed]
        return [prefixed] + rest, own, path.split("/", 1)[1]
    cands = ([own] if own else []) + [p for p in repos.values() if p != own]
    if not cands:
        cands = [Path.cwd()]
    return cands, own, path


def read_text_inside(root: Path, rel: str) -> Optional[str]:
    p = (root / rel) if not os.path.isabs(rel) else Path(rel)
    if not inside(root, p) or not p.is_file():
        return None
    try:
        return p.read_bytes().decode("utf-8", errors="replace")
    except OSError:
        return None


def file_lines(cands: List[Path], own: Optional[Path], rel: str, fm: Dict[str, str]) -> Tuple[Optional[List[str]], str]:
    """Return (lines, source). Source is 'repo-name@ref' or 'repo-name@disk', or a reason when missing."""
    if os.path.isabs(rel):
        for repo in cands:
            text = read_text_inside(repo, rel)
            if text is not None:
                return text.split("\n"), "%s@disk" % repo.name
        return None, "outside every repository root"
    explicit_ref, rel = split_ref(rel)
    if rel.startswith("-") or ".." in Path(rel).parts:
        return None, "unsafe path"
    sha = (fm.get("git_commit") or fm.get("as_of_commit") or "").split()[:1]
    branch = (fm.get("branch") or "").split()[:1]
    if branch and branch[0].startswith("origin/"):
        branch = [branch[0][len("origin/"):]]
    if explicit_ref:
        for repo in cands:
            text = git_blob(repo, explicit_ref, rel)
            if text is not None:
                return text.split("\n"), "%s@%s" % (repo.name, explicit_ref[:24])
        return None, "pinned ref not found"
    for repo in cands:
        refs = ([sha[0]] if sha and repo == own else []) + ([("origin/" + branch[0])] if branch else []) + ["HEAD"]
        for ref in refs:
            text = git_blob(repo, ref, rel)
            if text is not None:
                return text.split("\n"), "%s@%s" % (repo.name, ref[:12])
        text = read_text_inside(repo, rel)
        if text is not None:
            return text.split("\n"), "%s@disk" % repo.name
    return None, "file not found in %s" % ", ".join(p.name for p in cands)


def build_excerpt(lines: List[str], ranges: List[Tuple[int, int]], context: int, max_lines: int) -> Tuple[str, bool, Optional[str]]:
    """Return (excerpt, truncated, error). Lines are 1-based; a cited line past EOF is an error."""
    if lines and lines[-1] == "":
        lines = lines[:-1]  # trailing newline
    n = len(lines)
    for lo, hi in ranges:
        if lo > n:
            return "", False, "cited line %d is past end of file (%d lines)" % (lo, n)
    wanted = sorted((max(1, lo - context), min(n, hi + context)) for lo, hi in ranges)
    merged: List[List[int]] = []
    for lo, hi in wanted:
        if merged and lo <= merged[-1][1] + 1:
            merged[-1][1] = max(merged[-1][1], hi)
        else:
            merged.append([lo, hi])
    out, count, truncated = [], 0, False
    for i, (lo, hi) in enumerate(merged):
        if i:
            out.append("…")
        for ln in range(lo, hi + 1):
            if count >= max_lines:
                truncated = True
                break
            text = lines[ln - 1]
            if len(text) > MAX_LINE_CHARS:
                text = text[:MAX_LINE_CHARS] + " …"
            out.append("%d: %s" % (ln, text))
            count += 1
        if truncated:
            break
    return "\n".join(out), truncated, None


# ── judges ────────────────────────────────────────────────────────────────────

def dry_judge(row: dict) -> dict:
    return {"choice": None, "probabilities": None, "confidence": None, "sufficient": None,
            "latency_ms": 0, "input_tokens": 0, "output_tokens": 0, "model": "dry"}


class _NoRedirect(request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None  # a redirect becomes an HTTPError; the bearer key is never re-sent elsewhere


def num(x) -> Optional[float]:
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def make_jev_judge(model: str):
    key = (os.environ.get("TYPESAFE_API_KEY") or "").strip()
    if not key:
        sys.exit("claim-check: --judge jev needs TYPESAFE_API_KEY in the environment (never pass it on the command line)")
    if not re.fullmatch(r"[\x21-\x7e]+", key):
        sys.exit("claim-check: TYPESAFE_API_KEY contains whitespace or non-printable characters; fix the export")
    opener = request.build_opener(_NoRedirect())

    def judge(row: dict) -> dict:
        body = {
            "state": {"claim": row["claim"], "file": row["path"], "cited_lines": row["spec"], "excerpt": row["excerpt"]},
            "model": model,
            "questions": {
                "relation": {"type": "choice",
                             "instructions": "How does the excerpt relate to the claim? Judge only from the excerpt.",
                             "criteria": RELATION_CRITERIA},
                "sufficient": {"type": "noul",
                               "instructions": "Is the excerpt alone enough to judge the claim, without reading other files or other parts of this file?"},
            },
        }
        data = json.dumps(body).encode()
        delay = 1.0
        last = "gave up"
        for attempt in range(5):
            req = request.Request(API_URL, data=data, method="POST", headers={"Content-Type": "application/json"})
            req.add_unredirected_header("Authorization", "Bearer " + key)
            t0 = time.time()
            try:
                with opener.open(req, timeout=60) as r:
                    resp = json.loads(r.read().decode("utf-8", errors="replace"))
                ms = int((time.time() - t0) * 1000)
                answers = resp.get("answers") or {}
                rel = answers.get("relation") or {}
                suff = answers.get("sufficient") or {}
                usage = resp.get("usage") or {}
                choice = rel.get("choice")
                conf = num(rel.get("confidence"))
                if choice not in RELATION_CRITERIA or conf is None:
                    return {"error": "unexpected response shape: %s" % json.dumps(resp)[:200], "latency_ms": ms, "model": model}
                return {"choice": choice, "probabilities": rel.get("probabilities"), "confidence": conf,
                        "sufficient": num(suff.get("noul")), "latency_ms": ms,
                        "input_tokens": usage.get("input_tokens"), "output_tokens": usage.get("output_tokens"),
                        "model": resp.get("model", model)}
            except error.HTTPError as e:
                last = "HTTP %d" % e.code
                if e.code in (429, 500, 502, 503, 529) and attempt < 4:
                    ra = num(e.headers.get("Retry-After")) if e.headers else None
                    time.sleep((ra if ra else delay) + random.uniform(0, 0.5))
                    delay *= 2
                    continue
                try:
                    detail = e.read().decode("utf-8", errors="replace")[:200]
                except Exception:  # noqa: BLE001 — never let a read error surface anything else
                    detail = ""
                return {"error": "%s: %s" % (last, detail), "latency_ms": int((time.time() - t0) * 1000), "model": model}
            except Exception as e:  # noqa: BLE001 — network, decode, shape: log the class, never the request
                last = "%s: %s" % (type(e).__name__, str(e)[:120].replace(key, "<key>"))
                if attempt < 4 and isinstance(e, (error.URLError, TimeoutError, OSError)):
                    time.sleep(delay + random.uniform(0, 0.5))
                    delay *= 2
                    continue
                return {"error": last, "model": model}
        return {"error": last, "model": model}

    return judge


# ── reporting ─────────────────────────────────────────────────────────────────

def bucket(row: dict) -> str:
    if row.get("error"):
        return "error"
    if row.get("choice") is None:
        return "dry"
    if row["choice"] == "supports" and (num(row.get("confidence")) or 0) >= AUTO_PASS:
        return "would-pass"
    return "would-flag"


def pct(xs: List[float], q: float) -> float:
    if not xs:
        return 0.0
    xs = sorted(xs)
    return xs[max(0, min(len(xs) - 1, int(round(q * (len(xs) - 1)))))]


def md_cell(s: str) -> str:
    return s.replace("|", "\\|").replace("`", "'").replace("\n", " ")


def write_report(doc: Path, rows: List[dict], skipped: List[dict], out_dir: Path, judge_name: str) -> Path:
    rep = out_dir / (doc.stem + ".report.md")
    counts: Dict[str, int] = {}
    for r in rows:
        counts[bucket(r)] = counts.get(bucket(r), 0) + 1
    lat = [r["latency_ms"] for r in rows if r.get("latency_ms")]
    toks_in = sum(r.get("input_tokens") or 0 for r in rows)
    toks_out = sum(r.get("output_tokens") or 0 for r in rows)
    srcs: Dict[str, int] = {}
    for r in rows:
        srcs[r["excerpt_source"]] = srcs.get(r["excerpt_source"], 0) + 1
    lines = ["# Claim check (shadow) — %s" % doc.name, "",
             "*Judge:* `%s` · *run:* %s · *claims:* %d · *skipped bullets:* %d" % (judge_name, datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%MZ"), len(rows), len(skipped)),
             "", "**This is a shadow.** Nothing here changed the research document, and none of these verdicts gate anything. "
             "`would-pass` = supports with confidence ≥ %.2f; everything else `would-flag`." % AUTO_PASS, "",
             "| bucket | n |", "|---|---|"]
    for k in ("would-pass", "would-flag", "dry", "error"):
        if counts.get(k):
            lines.append("| %s | %d |" % (k, counts[k]))
    lines += ["", "*Excerpt sources:* " + ", ".join("%s=%d" % kv for kv in sorted(srcs.items())),
              "*Tokens:* in %d · out %d · *latency ms:* p50 %d · p95 %d" % (toks_in, toks_out, pct(lat, .5), pct(lat, .95)), "",
              "## Claims — flags first, then least confident", "",
              "| # | relation | conf | sufficient | file:lines | claim | source | trunc |", "|---|---|---|---|---|---|---|---|"]

    def key(i: int):
        r = rows[i]
        rank = {"error": 0, "would-flag": 1, "dry": 2, "would-pass": 3}[bucket(r)]
        c = num(r.get("confidence"))
        return (rank, c if c is not None else 2.0)

    for i in sorted(range(len(rows)), key=key):
        r = rows[i]
        c, s = num(r.get("confidence")), num(r.get("sufficient"))
        conf = "%.2f" % c if c is not None else "—"
        suff = "%.2f" % s if s is not None else "—"
        rel = r.get("choice") or ("ERR" if r.get("error") else "—")
        lines.append("| %d | %s | %s | %s | %s | %s | %s | %s |" % (i + 1, rel, conf, suff, md_cell("%s:%s" % (r["path"], r["spec"])), md_cell(r["claim"][:110]), md_cell(r["excerpt_source"]), "y" if r["truncated"] else ""))
    if skipped:
        lines += ["", "## Skipped bullets", ""] + ["- %s — %s" % (s["reason"], md_cell(s["raw"][:120])) for s in skipped]
    errs = [(i, r) for i, r in enumerate(rows) if r.get("error")]
    if errs:
        lines += ["", "## Errors", ""] + ["- #%d %s" % (i + 1, md_cell(r["error"])) for i, r in errs]
    rep.write_text("\n".join(lines) + "\n")
    return rep


# ── main ──────────────────────────────────────────────────────────────────────

def resolve_out(args) -> Path:
    if args.out:
        return Path(args.out).expanduser()
    if os.environ.get("CLAIM_CHECK_OUT"):
        return Path(os.environ["CLAIM_CHECK_OUT"]).expanduser()
    if os.environ.get("ATLAS_JOURNAL"):
        return Path(os.environ["ATLAS_JOURNAL"]).expanduser() / "claim-check"
    cfg = Path.home() / ".claude" / "atlas.json"
    if cfg.is_file():
        try:
            j = json.loads(cfg.read_text()).get("journal")
            if j:
                return Path(j).expanduser() / "claim-check"
        except ValueError:
            pass
    return Path.cwd() / "claim-check"


def parse_repos(spec: Optional[str]) -> Dict[str, Path]:
    repos: Dict[str, Path] = {}
    for item in (spec or "").split(","):
        if "=" in item:
            k, v = item.split("=", 1)
            repos[k.strip()] = Path(v.strip()).expanduser()
    return repos


def process_doc(doc: Path, args, repos: Dict[str, Path], judge, out_dir: Path) -> Tuple[List[dict], List[dict], Path]:
    text = doc.read_bytes().decode("utf-8", errors="replace")
    fm = parse_frontmatter(text)
    claims, skipped = parse_references(text)
    rows = []
    for c in claims:
        cands, own, rel = resolve_repos(fm, c["path"], args, repos)
        lines, source = file_lines(cands, own, rel, fm)
        if lines is None:
            rows.append({**c, "excerpt": "", "excerpt_source": "missing", "truncated": False, "error": "%s: %s" % (source, rel)})
            continue
        excerpt, truncated, err = build_excerpt(lines, c["ranges"], args.context, args.max_lines)
        row = {**c, "excerpt": excerpt, "excerpt_source": source, "truncated": truncated}
        if err:
            row["error"] = err
        rows.append(row)
    todo = [r for r in rows if not r.get("error")]
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as ex:
        for r, verdict in zip(todo, ex.map(judge, todo)):
            r.update(verdict)
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).isoformat()
    with (out_dir / "log.jsonl").open("a") as f:
        for r in rows:
            entry = {k: v for k, v in r.items() if k not in ("ranges", "raw")}
            entry.update({"doc": doc.name, "run": stamp, "bucket": bucket(r)})
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    rep = write_report(doc, rows, skipped, out_dir, args.judge)
    return rows, skipped, rep


def check(cond: bool, msg: str, detail=None) -> None:
    if not cond:
        raise SystemExit("claim-check self-test FAILED: %s%s" % (msg, "" if detail is None else "\n  " + repr(detail)[:400]))


def self_test() -> int:
    fake_key = "TSK-selftest-" + "%08x" % random.getrandbits(32)
    os.environ["TYPESAFE_API_KEY"] = fake_key  # a dry run must never write this anywhere
    with tempfile.TemporaryDirectory() as td:
        def mkrepo(name: str, content: str) -> Tuple[Path, str]:
            repo = Path(td) / name
            (repo / "src").mkdir(parents=True)
            g = ["git", "-C", str(repo), "-c", "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null"]
            subprocess.run(g + ["init", "-q"], check=True)
            subprocess.run(g + ["config", "user.email", "t@t"], check=True)
            subprocess.run(g + ["config", "user.name", "t"], check=True)
            (repo / "src" / "a.py").write_text(content)
            subprocess.run(g + ["add", "."], check=True)
            subprocess.run(g + ["commit", "-q", "-m", "init"], check=True)
            sha = subprocess.run(g + ["rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
            return repo, sha

        main_repo, sha = mkrepo("mainrepo", "\n".join("line %d" % i for i in range(1, 61)) + "\n")
        other_repo, _ = mkrepo("otherrepo", "\n".join("other %d" % i for i in range(1, 21)) + "\n")
        (main_repo / "src" / "a.py").write_text("CHANGED\n")  # working tree drift: excerpt must come from the commit
        (Path(td) / "secret.txt").write_text("outside\n")
        doc = Path(td) / "2026-01-01-T-1-x.md"
        doc.write_text("---\nrepository: mainrepo (+ otherrepo @ deadbeef)\ngit_commit: %s\nbranch: main\n---\n# R\n\n## Code References\n\n"
                       "- `src/a.py:10-12` — three lines in the middle of the file\n"
                       "- `src/a.py:5,50` — two single lines far apart\n"
                       "- `src/a.py`, `:20–21` — continuation form with an en-dash\n"
                       "- `otherrepo/src/a.py:3` — prefixed path form resolves the other repo\n"
                       "- `src/a.py` — no line spec so this one is skipped\n"
                       "- plain prose bullet with no reference at all\n"
                       "- `src/a.py:1-59` — a very long range that gets truncated\n"
                       "\n### Sub-heading stays inside the section\n\n"
                       "- `src/a.py:2` — a claim under a deeper heading is still collected\n"
                       "- `src/a.py:500` — a line past the end of the file is an error row\n"
                       "- `../secret.txt:1` — a path escaping the repository is refused\n"
                       "- `%s:1` — an absolute path outside every root is refused\n"
                       "- `--output=/tmp/pwned:src/a.py:1` — an option-shaped ref is refused\n"
                       "- `.../a.py:1` — abbreviated paths are skipped\n"
                       "\n```\n- `src/a.py:7` — inside a fence, ignored\n```\n"
                       "\n## Other\n\n- `src/a.py:2` — outside the section, must be ignored\n" % (sha, Path(td) / "secret.txt"))
        before = doc.read_bytes()
        ns = argparse.Namespace(repo=None, context=1, max_lines=8, workers=2, judge="dry", out=str(Path(td) / "out"))
        repos = {"mainrepo": main_repo, "otherrepo": other_repo}
        rows, skipped, rep = process_doc(doc, ns, repos, dry_judge, Path(ns.out))
        check(len(rows) == 10, "expected 10 claim rows", [r["path"] for r in rows])
        check(len(skipped) == 3, "expected 3 skipped bullets", skipped)
        r0 = rows[0]
        check(r0["excerpt"].split("\n")[0] == "9: line 9" and r0["excerpt"].split("\n")[-1] == "13: line 13", "context slicing", r0["excerpt"])
        check(r0["excerpt_source"] == "mainrepo@" + sha[:12], "excerpt from the document's commit, not the working tree", r0["excerpt_source"])
        check("…" in rows[1]["excerpt"] and "50: line 50" in rows[1]["excerpt"], "multi-range join", rows[1]["excerpt"])
        check(rows[2]["spec"] == "20–21" and "20: line 20" in rows[2]["excerpt"] and "21: line 21" in rows[2]["excerpt"], "continuation + en-dash", rows[2])
        check(rows[3]["excerpt_source"].startswith("otherrepo@") and "3: other 3" in rows[3]["excerpt"], "prefixed path resolves the other repo", rows[3])
        check(rows[4]["truncated"] is True and len(rows[4]["excerpt"].split("\n")) == 8, "truncation", rows[4])
        check("2: line 2" in rows[5]["excerpt"], "sub-heading kept inside the section", rows[5])
        check("past end of file" in (rows[6].get("error") or ""), "past-EOF line is an error row", rows[6])
        check("unsafe path" in (rows[7].get("error") or ""), "../ path refused", rows[7])
        check("outside every repository root" in (rows[8].get("error") or ""), "absolute path outside roots refused", rows[8])
        check("pinned ref not found" in (rows[9].get("error") or "") and not Path("/tmp/pwned").exists(), "option-shaped ref refused, nothing written", rows[9])
        check(all(bucket(r) in ("dry", "error") for r in rows), "buckets in dry mode")
        check(doc.read_bytes() == before, "document unchanged")
        check((main_repo / "src" / "a.py").read_text() == "CHANGED\n", "repository working tree unchanged")
        log = (Path(ns.out) / "log.jsonl").read_text()
        check(log.count("\n") == 10 and rep.is_file(), "log + report written")
        check(fake_key not in log and fake_key not in rep.read_text(), "key never written to log or report")
        check(fake_key not in "".join(str(r) for r in rows), "key never in rows")
    print("claim-check self-test: OK")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0], formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    ap.add_argument("docs", nargs="*", help="research document(s)")
    ap.add_argument("--repo", help="the document's own repository root (overrides frontmatter)")
    ap.add_argument("--repos", default=os.environ.get("CLAIM_CHECK_REPOS"), help="name=path,name=path map for frontmatter `repository` and path prefixes")
    ap.add_argument("--judge", choices=["dry", "jev"], default="dry")
    ap.add_argument("--model", default="jev-latest")
    ap.add_argument("--out", help="output directory (default: journal/claim-check)")
    ap.add_argument("--context", type=int, default=3)
    ap.add_argument("--max-lines", type=int, default=40)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    if not args.docs:
        ap.error("give at least one research document, or --self-test")
    repos = parse_repos(args.repos)
    if args.repo:
        repos.setdefault(Path(args.repo).expanduser().name, Path(args.repo).expanduser())
    judge = dry_judge if args.judge == "dry" else make_jev_judge(args.model)
    out_dir = resolve_out(args)
    total = {"claims": 0, "skipped": 0, "would-pass": 0, "would-flag": 0, "error": 0}
    failed = 0
    for d in args.docs:
        doc = Path(d).expanduser()
        if not doc.is_file():
            print("skip (not a file): %s" % doc, file=sys.stderr)
            continue
        try:
            rows, skipped, rep = process_doc(doc, args, repos, judge, out_dir)
        except Exception as e:  # noqa: BLE001 — one bad document must not stop the run
            failed += 1
            print("FAILED %s: %s: %s" % (doc.name, type(e).__name__, str(e)[:200]), file=sys.stderr)
            continue
        b: Dict[str, int] = {}
        for r in rows:
            b[bucket(r)] = b.get(bucket(r), 0) + 1
        total["claims"] += len(rows)
        total["skipped"] += len(skipped)
        for k in ("would-pass", "would-flag", "error"):
            total[k] += b.get(k, 0)
        print("%-60s claims=%-3d skipped=%-2d %s -> %s" % (doc.name[:60], len(rows), len(skipped), " ".join("%s=%d" % kv for kv in sorted(b.items())), rep))
    print("TOTAL claims=%(claims)d skipped=%(skipped)d would-pass=%(would-pass)d would-flag=%(would-flag)d errors=%(error)d" % total + (" failed-docs=%d" % failed if failed else ""))
    print("log: %s" % (out_dir / "log.jsonl"))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
