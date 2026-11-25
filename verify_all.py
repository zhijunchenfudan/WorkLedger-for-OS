#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WorkLedger reproduction package -- verification script.

Checks the two technical documents in the deposit (WorkLedger.md and
WorkLedger_demo_report.md) against the interview transcripts they cite.

Standard library only. No network, no model, no installation.
Runtime on the deposited corpus: under one second.

Usage
-----
    python3 verify_all.py [path]

`path` may be any one of:
    * the deposited zip   Partner Company CEO_Interviews_Appendix.zip
    * a folder holding 00_README.md ... 99_index.md
    * the combined file   Partner Company CEO_Interviews_Appendix_combined.md

With no argument the script looks for these next to itself, then one level up.

Exit code 0 = every check passed or was reported as a documented difference.
Exit code 1 = at least one check failed in a way the README does not cover.
"""

import hashlib
import json
import os
import re
import sys
import textwrap
import zipfile

# --------------------------------------------------------------------------
# What the deposit says, recorded here so the check does not depend on it.
# Left column: declared in the appendix table (section 2). Right: the demo
# report's own statements (§0 and §1).
# --------------------------------------------------------------------------

MANIFEST = {
    "00_README.md": "5f9f284c75ba0a3c8083533b3d2a93b9ce8dcd0891c12faf276578826ad8db18",
    "01_interview_INT-01.md": "1cbf4ad5425ecf346f91a824a38042a96e768cee7f09c568c2983dc0685a0eff",
    "02_interview_INT-02.md": "09c6838331bfb136be15cc4c96e1e181d408c627dd11781ef1f481b4830e3f22",
    "03_interview_INT-03.md": "aab53eecaae00a2b849e017141d78a83f8d12b5433954c67030941b9354d577e",
    "04_interview_INT-04.md": "10d0c1f37818ff2d9a6ca4496d2410475241d506f6b6c30adaaf5c42874840d6",
    "99_index.md": "2d4ae04f4858a1288ba5206a1715e2dfbd549560fb54801696a84b41c1650c2b",
}

DECLARED = {
    "INT-01": {"minutes": 117, "words": 19000, "sections": 12},
    "INT-02": {"minutes": 60, "words": 9750, "sections": 19},
    "INT-03": {"minutes": 10, "words": 1750, "sections": 4},
    "INT-04": {"minutes": 7, "words": 1350, "sections": 5},
}

# Demo report, §0: "INT-03: 10 minutes, 30 speaker turns, 1,756 words".
DEMO_TURNS_INT03 = 30

# Demo report, §1 table.
DEMO_STRATA = {
    "source fragment": 30,
    "claim": 17,
    "fact (work event)": 0,
    "evaluation": 0,
    "derived assessment": 1,
}

# Every quotation the demo report attributes to INT-03, with the turn it
# should sit in. Speaker is enforced where the report names one.
QUOTES = [
    ("INT-03", "06:07", "R1",
     "we four never thanked them properly, and people stop doing a thing that nobody acknowledges",
     "demo report §2, SourceFragment INT-03:06:07:R1"),
    ("INT-03", "01:18", None,
     "we mistake the platform for our own capability",
     "demo report §4, row C-INT03-004; index §A"),
    ("INT-03", "07:48", None,
     "one-to-one service",
     "demo report §4, row C-INT03-017"),
    ("INT-03", "08:41", None,
     "the service is genuinely better",
     "demo report §3, first evaluative turn"),
    ("INT-03", "09:34", None,
     "coordination is genuinely hard",
     "demo report §3, second evaluative turn"),
    ("INT-03", "01:18", None,
     "three years of lead",
     "demo report §4, row C-INT03-004"),
]

VERDICTS = {"supported", "partially supported", "contradicted", "insufficient evidence"}
OBJECTS = {"SourceFragment", "Claim", "Fact", "Evaluation", "DerivedAssessment", "CoverageReport"}

# Differences this script is expected to report on the deposited version.
# They are argued in README.md section 5; any other DIFF is a new finding.
DOCUMENTED = {"C4", "C7"}

# --------------------------------------------------------------------------
# Loading
# --------------------------------------------------------------------------

TURN = re.compile(r"^\*\*(R\d) \((\d{1,2}:\d{2}(?::\d{2})?)\)\*\*")
SECTION = re.compile(r"^### (\d+)\. .*\((\d{1,2}:\d{2}(?::\d{2})?)[\u2013\-](\d{1,2}:\d{2}(?::\d{2})?)\)\s*$")
CODE = re.compile(r"\*\*Interview code:\*\*\s*(INT-\d{2})")
DURATION = re.compile(r"\*\*Duration:\*\*\s*approx\.\s*(\d+)\s*minutes")


def secs(ts):
    parts = [int(p) for p in ts.split(":")]
    while len(parts) < 3:
        parts.insert(0, 0)
    return parts[0] * 3600 + parts[1] * 60 + parts[2]


def candidate_paths(arg):
    here = os.path.dirname(os.path.abspath(__file__))
    up = os.path.dirname(here)
    names = [
        "Partner Company CEO_Interviews_Appendix.zip",
        "Partner Company CEO_Interviews_Appendix_combined.md",
        "transcripts",
    ]
    if arg:
        return [arg]
    out = []
    for base in (here, up):
        for n in names:
            p = os.path.join(base, n)
            if os.path.exists(p):
                out.append(p)
    return out


def load(path):
    """Return (files, transcript-texts, label, hashed)."""
    files = {}
    if os.path.isdir(path):
        for name in sorted(os.listdir(path)):
            if name.lower().endswith(".md"):
                files[name] = open(os.path.join(path, name), encoding="utf-8").read()
        return files, files, os.path.basename(path) + "/", True

    if path.lower().endswith(".zip"):
        with zipfile.ZipFile(path) as z:
            for name in sorted(z.namelist()):
                if name.lower().endswith(".md"):
                    files[os.path.basename(name)] = z.read(name).decode("utf-8")
        return files, files, os.path.basename(path), True

    raw = open(path, encoding="utf-8").read()
    texts = {}
    for block in re.split(r"(?m)^(?=# )", raw):
        if block.startswith("# Interview "):
            m = CODE.search(block)
            if m:
                texts[m.group(1) + ".md"] = block
        elif block.startswith("# Thematic index"):
            texts["99_index.md"] = block
        elif block.strip():
            texts.setdefault("00_README.md", block)
    return texts, texts, os.path.basename(path), False


def split_interviews(files):
    out = {}
    for name, text in files.items():
        m = CODE.search(text)
        if m:
            out[m.group(1)] = text
    return out


def turns_of(text):
    """Return [(speaker, timestamp)] for the transcript body only."""
    body = text.split("## Transcript", 1)[-1].split("## Notes for analysis", 1)[0]
    return [(m.group(1), m.group(2)) for m in
            (TURN.match(l) for l in body.split("\n") if l.strip()) if m]


def sections_of(text):
    body = text.split("## Transcript", 1)[-1].split("## Notes for analysis", 1)[0]
    return [(int(m.group(1)), m.group(2), m.group(3)) for m in
            (SECTION.match(l) for l in body.split("\n")) if m]


# --------------------------------------------------------------------------
# Checks. Each returns (status, detail). status in PASS / DIFF / INFO.
# --------------------------------------------------------------------------

def check_manifest(files, hashed):
    if not hashed:
        return "INFO", "combined file -- per-file hashes not applicable"
    bad = []
    for name, want in MANIFEST.items():
        if name not in files:
            bad.append(name + " missing")
        elif hashlib.sha256(files[name].encode("utf-8")).hexdigest() != want:
            bad.append(name + " altered")
    if bad:
        return "DIFF", "; ".join(bad)
    return "PASS", "6 files, sha256 as recorded in README table 1"


def check_census(ivs):
    notes = []
    ok = True
    summary = []
    for code in sorted(DECLARED):
        text = ivs[code]
        ts = turns_of(text)
        secs_ = sections_of(text)
        spk = {}
        for s, _ in ts:
            spk[s] = spk.get(s, 0) + 1
        summary.append("%s %d turns (%s), %d sections" % (
            code, len(ts), " / ".join("%s %d" % (k, spk[k]) for k in sorted(spk)), len(secs_)))
        if len(secs_) != DECLARED[code]["sections"]:
            ok = False
            notes.append("%s sections %d != %d" % (code, len(secs_), DECLARED[code]["sections"]))
        if code == "INT-03" and len(ts) != DEMO_TURNS_INT03:
            ok = False
            notes.append("INT-03 turns %d != %d" % (len(ts), DEMO_TURNS_INT03))
    if not ok:
        return "DIFF", "; ".join(notes)
    return "PASS", "; ".join(summary)


def check_words(files, ivs, demo_text=""):
    notes = []
    worst = 0.0
    for code in sorted(DECLARED):
        # count on the interview file itself, whole file, whitespace tokens
        n = len(ivs[code].split())
        want = DECLARED[code]["words"]
        drift = abs(n - want) / float(want) * 100
        worst = max(worst, drift)
        if drift > 1.0:
            notes.append("%s %d vs %d (%.1f%%)" % (code, n, want, drift))
        else:
            notes.append("%s %d vs %d (%.2f%%)" % (code, n, want, drift))
    status = "PASS" if worst <= 1.0 else "DIFF"
    detail = "wc -w within 1% of the appendix table: " + "; ".join(notes)
    m = re.search(r"([\d,]+) words of edited English", demo_text)
    if m and "INT-03" in ivs:
        stated = int(m.group(1).replace(",", ""))
        n = len(ivs["INT-03"].split())
        detail += " | demo report states %s, file counts %d (%.2f%%)" % (
            m.group(1), n, abs(n - stated) / float(stated) * 100)
    return status, detail


def check_duration(ivs):
    """Header 'Duration: approx. N minutes' against the last timestamp."""
    bad = []
    seen = []
    for code in sorted(ivs):
        text = ivs[code]
        m = DURATION.search(text.split("## Summary")[0])
        ts = turns_of(text)
        if not m or not ts:
            continue
        declared = int(m.group(1))
        measured = secs(ts[-1][1]) / 60.0
        seen.append("%s %d vs %.1f" % (code, declared, measured))
        if abs(declared - measured) > 1.0:
            bad.append("%s header says %d min, last turn at %s" % (code, declared, ts[-1][1]))
    if bad:
        return "DIFF", "; ".join(bad) + " | measured: " + "; ".join(seen)
    return "PASS", "header durations match the last timestamp: " + "; ".join(seen)


def check_quotes(ivs):
    bad = []
    for code, ts, speaker, quote, where in QUOTES:
        text = ivs[code]
        if quote.lower() not in text.lower():
            bad.append("%s not found (%s)" % (quote[:40], where))
            continue
        if speaker:
            line = None
            for l in text.split("\n"):
                m = TURN.match(l)
                if m and m.group(2) == ts and m.group(1) == speaker:
                    line = l
                    break
            if line is None or quote.lower() not in line.lower():
                bad.append("quote not in %s (%s) at %s" % (speaker, ts, where))
    if bad:
        return "DIFF", "; ".join(bad)
    return "PASS", "%d quotations resolve to the cited turn and speaker" % len(QUOTES)


def check_ids(ivs, demo_text=""):
    """Every INT-03:MM:SS:R# cited anywhere must resolve to a real turn."""
    if not demo_text:
        return "INFO", "demo report not found next to this script -- identifier check skipped"
    text = ivs["INT-03"]
    ts_by_speaker = {}
    for s, t in turns_of(text):
        ts_by_speaker.setdefault(t, set()).add(s)
    cited = set()
    for src in (text, demo_text):
        for m in re.finditer(r"INT-03:(\d{2}:\d{2}):(R\d)", src):
            cited.add((m.group(1), m.group(2)))
    bad = [c for c in cited if c[0] not in ts_by_speaker or c[1] not in ts_by_speaker[c[0]]]
    if bad:
        return "DIFF", "unresolved: " + ", ".join("%s %s" % b for b in bad)
    return "PASS", "%d evidence identifiers resolve to a turn with the stated speaker" % len(cited)


def check_arithmetic(demo_text):
    rows = re.findall(
        r"^\|\s*(Source|Claim|Fact \(work event\)|Evaluation|Derived assessment)\s*\|\s*\*\*(\d+)\*\*",
        demo_text, re.M)
    counted = {}
    for name, n in rows:
        counted[name.lower()] = int(n)
    if len(counted) != 5:
        return "DIFF", "stratum table not found (%d rows)" % len(counted)
    total = sum(counted.values())
    stated_sentence = re.search(r"all (\d+) records", demo_text)
    stated_29 = "twenty-nine records" in demo_text
    detail = "table sums to %d objects (%d with the coverage report)" % (total, total + 1)
    if stated_sentence or stated_29:
        found = []
        if stated_29:
            found.append("twenty-nine")
        if stated_sentence:
            found.append(stated_sentence.group(1))
        return "DIFF", detail + "; report says " + " and ".join(found) + " (erratum, README §5)"
    return "PASS", detail


def check_index(ivs, files):
    idx = files.get("99_index.md")
    if not idx:
        return "INFO", "99_index.md not in this copy"
    bad = []
    n = 0
    for m in re.finditer(r"^\|\s*(INT-\d{2})\s*§(\d+)\s*,\s*(\d{1,2}:\d{2}(?::\d{2})?)(?:[\u2013\-](\d{1,2}:\d{2}(?::\d{2})?))?", idx, re.M):
        code, sec, start, end = m.group(1), int(m.group(2)), m.group(3), m.group(4)
        if code not in ivs:
            bad.append("%s absent" % code)
            continue
        text = ivs[code]
        secs_ = sections_of(text)
        if sec > len(secs_):
            bad.append("%s §%d absent" % (code, sec))
            continue
        stamps = {t for _, t in turns_of(text)}
        if start not in stamps:
            bad.append("%s §%d start %s is not a turn" % (code, sec, start))
            continue
        n += 1
    if bad:
        return "DIFF", "; ".join(bad)
    return "PASS", "%d index locators resolve to a section and a real turn" % n


def check_prohibitions(demo_text):
    """The samples must instantiate WorkLedger.md §5 (no score, gate withheld)."""
    problems = []
    if '"gate": "withheld' not in demo_text:
        problems.append("derived assessment not withheld")
    if re.search(r"^\s*Systems thinking:\s*[\d.]+", demo_text, re.M):
        problems.append("a scalar capability score is printed as output")
    if '"object": "Evaluation"' in demo_text:
        problems.append("an Evaluation object appears on interview data")
    if problems:
        return "DIFF", "; ".join(problems)
    return "PASS", "no scalar score, derivation withheld, no Evaluation object"


def check_jsonl(files, path):
    """Optional: record-level checks when demo_objects.jsonl is in the deposit."""
    target = None
    for base in [os.path.dirname(os.path.abspath(__file__)),
                 os.path.dirname(os.path.abspath(path))]:
        p = os.path.join(base, "demo_objects.jsonl")
        if os.path.exists(p):
            target = p
            break
    if not target:
        return "INFO", "demo_objects.jsonl not in this copy -- record-level checks skipped"

    recs = []
    with open(target, encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                recs.append(json.loads(line))
            except ValueError as e:
                return "DIFF", "line %d is not valid JSON: %s" % (i, e)

    bad = []
    counts = {}
    for r in recs:
        obj = r.get("object")
        counts[obj] = counts.get(obj, 0) + 1
        if obj not in OBJECTS:
            bad.append("unknown object type %r" % obj)
        if not r.get("id"):
            bad.append("record without id: %r" % obj)
        if obj == "Claim":
            adj = r.get("adjudication") or {}
            if adj.get("verdict") not in VERDICTS:
                bad.append("%s verdict %r" % (r.get("id"), adj.get("verdict")))
            if adj.get("verdict") == "supported" and not adj.get("supported_by"):
                bad.append("%s supported without evidence" % r.get("id"))
        if obj == "SourceFragment":
            for k in ("speaker", "timestamp", "text"):
                if k not in r:
                    bad.append("%s missing %s" % (r.get("id"), k))
    if bad:
        return "DIFF", "; ".join(bad[:5]) + (" (+%d)" % (len(bad) - 5) if len(bad) > 5 else "")
    return "PASS", "%d records: %s" % (
        len(recs), ", ".join("%s %d" % (k, v) for k, v in sorted(counts.items())))


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def main():
    paths = candidate_paths(sys.argv[1] if len(sys.argv) > 1 else None)
    paths = [p for p in paths if os.path.exists(p)]
    if not paths:
        print("No deposit found. Pass the zip, the folder, or the combined .md as the first argument.")
        return 1
    path = paths[0]

    files, _texts, label, hashed = load(path)
    ivs = split_interviews(files)
    missing = [c for c in DECLARED if c not in ivs]
    if missing:
        print("Could not find transcripts for: " + ", ".join(missing))
        return 1

    demo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "WorkLedger_demo_report.md")
    if not os.path.exists(demo_path):
        demo_path = os.path.join(os.path.dirname(os.path.abspath(path)), "WorkLedger_demo_report.md")
    demo = open(demo_path, encoding="utf-8").read() if os.path.exists(demo_path) else ""

    results = []
    results.append(("C1", "deposit integrity (sha256)", check_manifest(files, hashed)))
    results.append(("C2", "turn and section census", check_census(ivs)))
    results.append(("C3", "word census vs appendix table", check_words(files, ivs, demo)))
    results.append(("C4", "duration vs last timestamp", check_duration(ivs)))
    results.append(("C5", "quotation fidelity", check_quotes(ivs)))
    results.append(("C6", "evidence identifiers resolve", check_ids(ivs, demo)))
    if demo:
        results.append(("C7", "ledger arithmetic", check_arithmetic(demo)))
        results.append(("C8", "the instrument's prohibitions hold", check_prohibitions(demo)))
    results.append(("C9", "index locators resolve", check_index(ivs, files)))
    results.append(("C10", "record-level checks (optional)", check_jsonl(files, path)))

    print("WorkLedger reproduction package -- verification")
    print("source: %s" % label)
    print("-" * 78)
    width = max(len(name) for _, name, _ in results)
    failed, undocumented = 0, 0
    for cid, name, (status, detail) in results:
        if status == "DIFF":
            failed += 1
            if cid not in DOCUMENTED:
                undocumented += 1
        prefix = "%-4s %-*s %-5s " % (cid, width, name, status)
        lines = textwrap.wrap(prefix + detail, width=98,
                              break_long_words=False, break_on_hyphens=False,
                              subsequent_indent=" " * len(prefix)) or [""]
        for line in lines:
            print(line)
    print("-" * 78)
    print("%d checks, %d difference(s), %d not covered by README section 5"
          % (len(results), failed, undocumented))
    if failed:
        print("Each difference is discussed in README.md section 5.")
    return 1 if undocumented else 0


if __name__ == "__main__":
    sys.exit(main())
