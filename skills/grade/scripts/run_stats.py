#!/usr/bin/env python3
"""Measure one kit run from its Claude Code transcript, for the scorecard's
Tokens and cost, Time and Models / effort rows.

  run_stats.py --find <work-item>          # locate the run session(s) by work-item key
  run_stats.py <session.jsonl | session-id> [--gate-gap-min 10]

Reads ~/.claude/projects/*/<session>.jsonl and <session>/subagents/*.jsonl
(+ .meta.json for each subagent's agent type). Read-only; prints markdown.

Costs are list prices (USD per million tokens) from
https://platform.claude.com/docs/en/about-claude/pricing, checked 2026-10-29.
Update PRICES when the page changes; a model missing here is reported unpriced.
"""
import glob, json, os, re, sys
from collections import defaultdict
from datetime import datetime

PRICES = {  # input, 5m cache write, 1h cache write, cache read, output
    "claude-opus-5-5":   (4.00, 5.00, 8.00, 0.20, 20.00),
    "claude-opus-5":     (5.00, 6.25, 10.00, 0.50, 25.00),
    "claude-sonnet-5-5": (2.00, 2.50, 4.00, 0.10, 10.00),
    "claude-sonnet-5":   (2.00, 2.50, 4.00, 0.20, 10.00),
    "claude-fable-5-1":  (10.00, 12.50, 20.00, 0.25, 50.00),
    "claude-fable-5":    (10.00, 12.50, 20.00, 1.00, 50.00),
}
PROJECTS = os.path.expanduser("~/.claude/projects")


def m_content(d):
    m = d.get("message")
    return m.get("content") if isinstance(m, dict) else None


MACHINE_PREFIXES = ("<task-notification", "<agent-message", "<system-reminder", "<command-", "<local-command")


def kind_of(d):
    """'person' for a message a human typed (directly or queued while the model was busy),
    'tool_result' for tool output, else the entry type."""
    kind, c = d.get("type"), m_content(d)
    if kind == "queue-operation":
        text = str(d.get("content") or "")
        return "person" if d.get("operation") == "enqueue" and text and not text.lstrip().startswith(MACHINE_PREFIXES) else kind
    if kind != "user" or d.get("isSidechain"):
        return kind
    if isinstance(c, list) and c and isinstance(c[0], dict):
        if c[0].get("type") == "tool_result":
            return "tool_result"
        c = c[0].get("text", "")
    text = c if isinstance(c, str) else ""
    return "person" if text.strip() and not text.lstrip().startswith(MACHINE_PREFIXES) else kind


def ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def read(path):
    """Assistant usage (deduplicated by message id), models, efforts, timestamps."""
    usage, models, efforts, stamps, turns = {}, defaultdict(int), defaultdict(int), [], []
    for line in open(path, encoding="utf-8", errors="replace"):
        try:
            d = json.loads(line)
        except ValueError:
            continue
        if d.get("timestamp"):
            stamps.append(d["timestamp"])
            turns.append((d["timestamp"], kind_of(d)))
        m = d.get("message") or {}
        if d.get("type") == "assistant" and m.get("usage"):
            key = m.get("id") or d.get("uuid")
            if key not in usage:
                models[m.get("model")] += 1
                if d.get("effort"):
                    efforts[d["effort"]] += 1
            usage[key] = (m.get("model"), m["usage"])
    return usage, models, efforts, stamps, turns


def tokens(usage):
    t = defaultdict(int)
    cost, unpriced = 0.0, set()
    for model, u in usage.values():
        cc = u.get("cache_creation") or {}
        w5 = cc.get("ephemeral_5m_input_tokens", 0)
        w1 = cc.get("ephemeral_1h_input_tokens", 0)
        if not cc:  # older entries: no split, treat as 5m
            w5 = u.get("cache_creation_input_tokens", 0)
        row = (u.get("input_tokens", 0), w5, w1, u.get("cache_read_input_tokens", 0), u.get("output_tokens", 0))
        for k, v in zip(("in", "w5", "w1", "read", "out"), row):
            t[k] += v
        p = PRICES.get(model)
        if p:
            cost += sum(a * b for a, b in zip(row, p)) / 1e6
        elif model and model != "<synthetic>":
            unpriced.add(model)
    return t, cost, unpriced


def minutes(stamps):
    return (ts(max(stamps)) - ts(min(stamps))).total_seconds() / 60 if stamps else 0.0


def waits(turns, gap_min, until=None):
    """Gaps over gap_min minutes after which the next substantive entry is a person's message:
    time the run sat waiting on a human (gates, questions). Gaps that end in a subagent hand-back,
    a task notification or a tool result are machine time and are not counted."""
    total, n = 0.0, 0
    turns = sorted(t for t in turns if until is None or t[0] <= until)
    for i, ((a, _), (b, _)) in enumerate(zip(turns, turns[1:])):
        g = (ts(b) - ts(a)).total_seconds() / 60
        if g <= gap_min:
            continue
        nxt = next((k for _, k in turns[i + 1:i + 8] if k not in ("attachment", "system", "file-history-delta")), None)
        if nxt == "person":
            total, n = total + g, n + 1
    return total, n


def active(stamps, cap_min=5.0):
    """Working minutes: the sum of gaps between entries, each capped at cap_min,
    so a subagent resumed hours later does not count its idle time."""
    s = sorted(ts(x) for x in stamps)
    return sum(min((b - a).total_seconds() / 60, cap_min) for a, b in zip(s, s[1:]))


def fmt(n):
    return f"{n / 1e6:.1f}M" if n >= 1e6 else f"{n / 1e3:.0f}k"


def find(key):
    """Sessions whose /feature-workflow launch names the ticket (as typed, URL or key)."""
    pat = re.compile(r"<command-name>/(?:atlas:)?feature-workflow</command-name>(?:\\n|\s)*<command-args>[^<]*" + re.escape(key))
    hits = []
    for path in glob.glob(f"{PROJECTS}/*/*.jsonl"):
        with open(path, encoding="utf-8", errors="replace") as f:
            for line in f:
                if '"type":"user"' in line and pat.search(line) and '"isSidechain":false' in line:
                    hits.append((json.loads(line).get("timestamp", ""), path))
                    break
    for when, p in sorted(hits):
        print(f"{when[:16]}  {os.path.getsize(p) / 1e6:6.1f} MB  {p}")
    if not hits:
        print(f"No session launched /feature-workflow with {key}.")


def main(argv):
    if len(argv) >= 2 and argv[0] == "--find":
        return find(argv[1])
    if not argv:
        sys.exit(__doc__)
    gap = float(argv[argv.index("--gate-gap-min") + 1]) if "--gate-gap-min" in argv else 10.0
    path = argv[0]
    if not path.endswith(".jsonl"):
        matches = glob.glob(f"{PROJECTS}/*/{path}.jsonl")
        if len(matches) != 1:
            sys.exit(f"session {path}: {len(matches)} matches")
        path = matches[0]
    base = path[:-len(".jsonl")]

    usage, models, efforts, stamps, turns = read(path)
    t, cost, unpriced = tokens(usage)
    pr_open = min((t for t, k in turns if k == "pr-link"), default=None)
    print(f"## Run measurements — `{os.path.basename(path)}`\n")
    print(f"- **Supervisor session:** {len(usage)} replies · models {dict(models)} · effort {dict(efforts)}")
    if pr_open:
        to_pr = (ts(pr_open) - ts(min(stamps))).total_seconds() / 60
        w, n = waits(turns, gap, until=pr_open)
        print(f"- **Launch → PR open** ({min(stamps)[:16]} → {pr_open[:16]}Z): {to_pr:.0f} min, of which "
              f"{w:.0f} min in {n} waits over {gap:.0f} min (waiting on a person) → {to_pr - w:.0f} min of machine and gate time")
    w, n = waits(turns, gap)
    print(f"- **Whole session** (first → last entry, includes anything after the PR): {minutes(stamps):.0f} min, "
          f"of which {w:.0f} min in {n} waits")

    roles = defaultdict(lambda: {"n": 0, "min": 0.0, "usage": {}, "models": defaultdict(int), "efforts": defaultdict(int)})
    for sub in sorted(glob.glob(f"{base}/subagents/*.jsonl")):
        meta_path = sub[:-len(".jsonl")] + ".meta.json"
        meta = json.load(open(meta_path)) if os.path.exists(meta_path) else {}
        u, m, e, s, _ = read(sub)
        r = roles[meta.get("agentType", "unknown")]
        r["n"] += 1
        r["min"] += active(s)
        r["usage"].update({f"{sub}:{k}": v for k, v in u.items()})
        for k, v in m.items():
            r["models"][k] += v
        for k, v in e.items():
            r["efforts"][k] += v

    print("\n| Role | Spawns | Active min | Model | Effort | Cache-read | Cache-write | Output | Cost |")
    print("|---|---|---|---|---|---|---|---|---|")
    print(f"| supervisor | — | — | {', '.join(k for k in models if k)} | {', '.join(efforts) or '?'} | "
          f"{fmt(t['read'])} | {fmt(t['w5'] + t['w1'])} | {fmt(t['out'])} | ${cost:.2f} |")
    sub_t, sub_cost, sub_min = defaultdict(int), 0.0, 0.0
    for name, r in sorted(roles.items(), key=lambda kv: -kv[1]["min"]):
        rt, rc, ru = tokens(r["usage"])
        unpriced |= ru
        for k, v in rt.items():
            sub_t[k] += v
        sub_cost += rc
        sub_min += r["min"]
        print(f"| {name} | {r['n']} | {r['min']:.1f} | {', '.join(k for k in r['models'] if k)} | "
              f"{', '.join(r['efforts']) or '?'} | {fmt(rt['read'])} | {fmt(rt['w5'] + rt['w1'])} | {fmt(rt['out'])} | ${rc:.2f} |")
    print(f"| **subagents total** | {sum(r['n'] for r in roles.values())} | {sub_min:.1f} | | | "
          f"{fmt(sub_t['read'])} | {fmt(sub_t['w5'] + sub_t['w1'])} | {fmt(sub_t['out'])} | ${sub_cost:.2f} |")
    print(f"\n- **Total at list price:** ${cost + sub_cost:.2f} · total cache-read {fmt(t['read'] + sub_t['read'])}")
    if unpriced:
        print(f"- **Unpriced models** (add to PRICES): {sorted(unpriced)}")
    print("- Active minutes sum the gaps between a subagent's entries, each capped at 5 min, so idle time before a resume is excluded.")
    print("- Transcript-based: calls that leave no transcript entry (auto-mode safety checks, titles) are not counted."
          " In one measured run the transcript total was about 9% under the /usage reading; prefer a /usage reading when the run recorded one.")
    print("- The session also contains anything else done in it (follow-ups, grading questions); say so on the scorecard if it does.")


if __name__ == "__main__":
    main(sys.argv[1:])
