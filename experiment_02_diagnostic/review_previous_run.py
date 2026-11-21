"""Summarize a completed results.csv without rerunning any API requests."""
import argparse
import csv
from collections import Counter
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_file", help="Path to an existing results.csv")
    parser.add_argument("--output", default="baseline_review", help="Review output folder")
    args = parser.parse_args()
    with open(args.csv_file, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    required = {"model", "case", "style", "run", "status", "raw_response"}
    if not rows or not required.issubset(rows[0]):
        parser.error("File is empty or missing the required results.csv columns")
    cases = {"compound_interest":0,"mortgage_payment":1,"realized_gain":2,"annualized_return":3,"bond_price":4}
    styles = {"direct":0,"wordy":1,"informal":2,"embedded":3,"misleading":4}
    models = list(dict.fromkeys(r["model"] for r in rows))
    problems = sorted((r for r in rows if r["status"] != "MATCH"),
        key=lambda r:(models.index(r["model"]), cases.get(r["case"],99), styles.get(r["style"],99), int(r["run"])))
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    # No reassignment to MATCH: the original classifications remain intact.
    fields = ["model","case","style","run","status","review_category","stop_reason","raw_response"]
    reviewed=[]
    for r in problems:
        raw = r.get("raw_response", "")
        if r["status"] != "NO_ANSWER": category = "OTHER_EXCEPTION"
        elif not raw.strip(): category = "EMPTY_TEXT"
        elif r.get("stop_reason") == "max_tokens": category = "TOKEN_LIMIT"
        else: category = "NEEDS_MANUAL_REVIEW"
        reviewed.append({**r,"review_category":category})
    with (out/"exceptions_to_review.csv").open("w",encoding="utf-8",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore")
        writer.writeheader();writer.writerows(reviewed)
    lines=["# Review of the existing API run","",
        "No API requests were made. No previous result was reclassified as correct.","",
        "## Results by model","",
        "| Model | MATCH | NO_ANSWER | BREAK | ANCHORED | ERROR |",
        "|---|---:|---:|---:|---:|---:|"]
    for model in models:
        c=Counter(r["status"] for r in rows if r["model"]==model)
        lines.append(f"| {model} | {c['MATCH']} | {c['NO_ANSWER']} | {c['BREAK']} | {c['ANCHORED']} | {c['ERROR']} |")
    lines += ["",f"Total attempts: {len(rows)}; exceptions: {len(problems)}.","",
        "The older CSV does not include stop reasons or token usage. Do not assume that an empty response or a response without FINAL is an arithmetic error.","",
        "## Exceptions by category","", "| Review category | Count |", "|---|---:|"]
    for category, count in Counter(r["review_category"] for r in reviewed).most_common():
        lines.append(f"| {category} | {count} |")
    lines += ["", "Read the original response in exceptions_to_review.csv before recording conclusions.", ""]
    (out/"review_summary.md").write_text("\n".join(lines),encoding="utf-8")
    print("\n".join(lines))
    print(f"Saved review files in {out}")


if __name__=="__main__": main()
