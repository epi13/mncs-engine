#!/usr/bin/env python3
"""conformance.py — run engine corpora across backends and report the matrix.

Orchestration only: every assertion lives in the corpus JSON (expected
values) and every implementation lives in .mncs sources. This script invokes
`mncs experiment run`, classifies each case as PASS / KNOWN-DIVERGENT (listed
in tests/known-divergences.json with a pressure ID) / FAIL, and prints a
backend matrix. Exit status is nonzero when any non-listed failure occurs.

Usage:
  python3 scripts/conformance.py --backend BACKEND CORPUS...
  python3 scripts/conformance.py --all BACKEND...
  python3 scripts/conformance.py --matrix   # every corpus x every backend
"""
import json
import os
import subprocess
import sys

ENGINE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LANG_ROOT = os.environ.get(
    "MNCS_LANGUAGE_ROOT", "/home/epi13/Documents/Projects/mncs-language")
MNCS_BIN = os.environ.get("MNCS_BIN",
                           os.path.join(LANG_ROOT, "target", "debug", "mncs"))
BACKENDS = [
    "mncs-research-bytecode",
    "mncs-portable-wasm-mvp",
    "mncs-llvm-ir",
    "mncs-c11",
    "mncs-cranelift",
]
# Module roots keyed by corpus name prefix: corpus file -> .mncs root.
# Defaults to language/mncs/engine/<area>/<mod>.mncs derived from the corpus
# target module (engine.<area>.<mod>); override here when they differ.
CORPUS_DIR = os.path.join(ENGINE_ROOT, "tests", "corpora")

env = dict(os.environ)
env["MNCS_LIBRARY_PATH"] = (LANG_ROOT + "/library:"
                             + ENGINE_ROOT + "/language/mncs")


def load_known():
    path = os.path.join(ENGINE_ROOT, "tests", "known-divergences.json")
    with open(path) as fh:
        data = json.load(fh)
    known = set()
    for entry in data.get("divergences", []):
        known.add((entry["corpus"], entry["case"], entry["backend"]))
    return known


def module_root(corpus_path):
    with open(corpus_path) as fh:
        corpus = json.load(fh)
    target = corpus["cases"][0]["request"]["target"]["module"]
    parts = target.split(".")
    # engine.<area>.<mod> -> language/mncs/engine/<area>/<mod>.mncs
    # pressure.<mod> -> language/mncs/pressure/<mod>.mncs
    assert parts[0] in ("engine", "pressure"), target
    stem = parts[-1]
    if parts[0] == "pressure":
        candidates = [
            os.path.join(ENGINE_ROOT, "language", "mncs", "pressure",
                         stem + ".mncs"),
        ]
    else:
        area = parts[1] if len(parts) > 2 else parts[1]
        candidates = [
            os.path.join(ENGINE_ROOT, "language", "mncs", "engine",
                         area, stem + ".mncs"),
        ]
    for cand in candidates:
        if os.path.exists(cand):
            return cand
    raise FileNotFoundError("no module root for " + target)


def run_corpus(corpus_name, backend, out_base):
    corpus_path = os.path.join(CORPUS_DIR, corpus_name + ".json")
    root = module_root(corpus_path)
    out_dir = os.path.join(out_base, corpus_name, backend)
    os.makedirs(out_dir, exist_ok=True)
    proc = subprocess.run(
        [MNCS_BIN, "experiment", "run", root, "--backend", backend,
         "--corpus", corpus_path, "--output-dir", out_dir],
        capture_output=True, text=True, env=env, timeout=600)
    if proc.returncode not in (0, 1):
        return {"error": proc.stderr[-2000:] + proc.stdout[-2000:]}
    try:
        return {"result": json.loads(proc.stdout)}
    except json.JSONDecodeError:
        return {"error": proc.stdout[-2000:] + proc.stderr[-2000:]}


def main(argv):
    args = list(argv)
    if "--matrix" in args:
        corpora = sorted(f[:-5] for f in os.listdir(CORPUS_DIR)
                          if f.endswith(".json"))
        backends = list(BACKENDS)
    elif "--all" in args:
        i = args.index("--all")
        backends = args[i + 1:] or list(BACKENDS)
        corpora = sorted(f[:-5] for f in os.listdir(CORPUS_DIR)
                          if f.endswith(".json"))
    else:
        backends, corpora = [], []
        i = 0
        while i < len(args):
            if args[i] == "--backend":
                backends.append(args[i + 1])
                i += 2
            else:
                corpora.append(args[i].removesuffix(".json"))
                i += 1
        if not backends:
            backends = list(BACKENDS)
    known = load_known()
    out_base = os.environ.get("MNCS_EVIDENCE_DIR",
                              "/tmp/mncs-engine-evidence")
    summary = {}
    failures = 0
    for corpus in corpora:
        summary[corpus] = {}
        for backend in backends:
            outcome = run_corpus(corpus, backend, out_base)
            if "error" in outcome:
                summary[corpus][backend] = "ERROR"
                failures += 1
                continue
            result = outcome["result"]
            cases = result.get("cases", [])
            if not cases:
                summary[corpus][backend] = "ERROR"
                failures += 1
                continue
            bad, known_bad = [], []
            for case in cases:
                if case.get("expectation_met"):
                    continue
                key = (corpus, case.get("case_id"), backend)
                if key in known:
                    known_bad.append(case.get("case_id"))
                else:
                    bad.append(case.get("case_id"))
            if bad:
                failures += 1
                summary[corpus][backend] = (
                    "FAIL(%d/%d:%s)" % (len(bad), len(cases), ",".join(bad)))
            elif known_bad:
                summary[corpus][backend] = (
                    "KNOWN(%s)" % ",".join(known_bad))
            else:
                summary[corpus][backend] = "PASS(%d)" % len(cases)
    header = "corpus".ljust(22) + "".join(b.replace("mncs-", "").ljust(22)
                                          for b in backends)
    print(header)
    for corpus in corpora:
        row = corpus.ljust(22)
        for backend in backends:
            row += summary[corpus].get(backend, "?").ljust(22)
        print(row)
    print("evidence:", out_base)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
