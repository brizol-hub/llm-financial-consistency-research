"""Recompute primary two-run study metrics from original API-result CSVs."""
import csv
from collections import Counter
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
files = [ROOT / "experiment_01_initial/actual_run/results.csv", ROOT / "experiment_02_diagnostic/actual_run/results.csv"]
sets = []
for i, path in enumerate(files, 1):
    with path.open(encoding="utf-8-sig", newline="") as f: rows = list(csv.DictReader(f))
    assert len(rows) == 150, (i, len(rows))
    counts = Counter(row["status"] for row in rows)
    print(f"Run {i}: {len(rows)} attempts, {dict(counts)}")
    for model in sorted(set(row["model"] for row in rows)):
        c = Counter(row["status"] for row in rows if row["model"] == model)
        print("  ", model, dict(c))
    sets.append(rows)
key = lambda x: (x["model"], x["case"], x["style"], x["run"])
a = {key(r): r for r in sets[0]}
b = {key(r): r for r in sets[1]}
assert len(a) == len(b) == 150 and set(a) == set(b)
old_missing = [r for r in a.values() if r["status"] == "NO_ANSWER"]
print("First-run missing answers:", len(old_missing))
print("Empty first-run text:", sum(not r["raw_response"].strip() for r in old_missing))
print("Their second-run status:", dict(Counter(b[key(r)]["status"] for r in old_missing)))
print("Second-run outputs >1000 tokens:", sum(int(r["output_tokens"]) > 1000 for r in b.values()))
print("Original missing cases with second-run outputs >1000:",sum(int(b[key(r)]["output_tokens"]) > 1000 for r in old_missing))
print("Second-run stop reasons:", dict(Counter(r["stop_reason"] for r in b.values())))
