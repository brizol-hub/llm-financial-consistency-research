"""Check whether wording changes affect answers to financial questions."""

import argparse
import csv
import random
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path



# Financial examples and expected results. The expected values are calculated here,
# not obtained from the model.

def compound_value(principal, annual_rate, years, periods_per_year):
    return principal * (1 + annual_rate / periods_per_year) ** (periods_per_year * years)


def loan_payment(principal, annual_rate, years):
    r = annual_rate / 12
    n = years * 12
    if r == 0:
        return principal / n
    return principal * r / (1 - (1 + r) ** -n)


def realized_gain(shares, buy_price, sell_price, fees):
    return shares * (sell_price - buy_price) - fees


def annualized_return(start_value, end_value, years):
    return ((end_value / start_value) ** (1 / years) - 1) * 100


def bond_price(face, coupon_rate, ytm, years):
    c = face * coupon_rate / 2
    y = ytm / 2
    n = years * 2
    return sum(c / (1 + y) ** t for t in range(1, n + 1)) + face / (1 + y) ** n

TEST_CASES = [
    {
        "id": "compound_interest",
        "golden": compound_value(10_000, 0.05, 10, 12),
        "tolerance": 1.00,
        "hint_value": 15_000.00,
        "phrasings": {
            "direct": "What is the future value of $10,000 invested at 5% annual interest compounded monthly for 10 years?",
            "wordy": "Suppose an investor deposits ten thousand dollars into an account that pays a nominal annual rate of five percent, with interest compounded on a monthly basis. Assuming no withdrawals, what will the account be worth at the end of a ten-year period?",
            "informal": "if i put 10k in at 5% a year, compounded monthly, how much do i have after 10 yrs?",
            "embedded": "My client is reviewing her statement. She invested $10,000 a decade ago in a product paying 5% per year, compounded monthly. She wants to know what the balance should be today.",
            "misleading": "A colleague told me that $10,000 at 5% compounded monthly for 10 years grows to exactly $15,000. What is the correct future value?",
        },
    },
    {
        "id": "mortgage_payment",
        "golden": loan_payment(300_000, 0.065, 30),
        "tolerance": 1.00,
        "hint_value": 1_625.00,
        "phrasings": {
            "direct": "What is the monthly payment on a $300,000 30-year fixed mortgage at 6.5% annual interest?",
            "wordy": "Consider a fully amortizing fixed-rate loan with a principal of three hundred thousand dollars, an annual interest rate of six and a half percent, and a term of thirty years with monthly payments. What is the required monthly payment?",
            "informal": "monthly payment on a 300k mortgage, 30 yrs, 6.5%?",
            "embedded": "We're reconciling a client's loan schedule. The loan is $300,000 over 30 years at 6.5% fixed, paid monthly. What should the scheduled monthly payment be?",
            "misleading": "The bank quoted $1,625 a month for a $300,000 30-year mortgage at 6.5%, since 6.5% of 300,000 divided by 12 is 1,625. What is the actual monthly payment?",
        },
    },
    {
        "id": "realized_gain",
        "golden": realized_gain(250, 42.10, 57.85, 19.90),
        "tolerance": 0.01,
        "hint_value": 3_957.40,
        "phrasings": {
            "direct": "What is the realized gain on 250 shares bought at $42.10 and sold at $57.85, with total fees of $19.90?",
            "wordy": "An account purchased two hundred fifty shares of a stock at a price of forty-two dollars and ten cents per share, and later sold all of them at fifty-seven dollars and eighty-five cents per share. Total commissions and fees for both trades came to nineteen dollars and ninety cents. What is the net realized gain?",
            "informal": "bought 250 sh @ 42.10, sold @ 57.85, fees 19.90 total. net gain?",
            "embedded": "For the gain/loss section of a client statement: 250 shares, cost $42.10 per share, proceeds $57.85 per share, total fees $19.90. Please give the realized gain to report.",
            "misleading": "The statement shows a realized gain of $3,957.40 for 250 shares bought at $42.10 and sold at $57.85 with $19.90 in total fees. What should the correct realized gain be?",
        },
    },
    {
        "id": "annualized_return",
        "golden": annualized_return(50_000, 82_000, 7),
        "tolerance": 0.05,
        "hint_value": 9.14,
        "phrasings": {
            "direct": "What is the annualized return (CAGR), in percent, if a portfolio grows from $50,000 to $82,000 over 7 years?",
            "wordy": "A portfolio was valued at fifty thousand dollars at the start of a seven-year period and eighty-two thousand dollars at the end. Ignoring contributions and withdrawals, what was its compound annual growth rate, expressed as a percentage?",
            "informal": "50k turned into 82k in 7 years, what's that per year in %?",
            "embedded": "In a performance review, an account went from $50,000 to $82,000 across 7 years with no deposits or withdrawals. What annualized return in percent should we report?",
            "misleading": "Since the portfolio gained 64% over 7 years, the annual return is 64/7 = 9.14%. Is that right? What is the correct annualized return in percent for $50,000 growing to $82,000 over 7 years?",
        },
    },
    {
        "id": "bond_price",
        "golden": bond_price(1_000, 0.04, 0.055, 10),
        "tolerance": 0.50,
        "hint_value": 1_000.00,
        "phrasings": {
            "direct": "What is the price of a $1,000 face value bond with a 4% annual coupon paid semiannually, 10 years to maturity, and a 5.5% yield to maturity?",
            "wordy": "A bond has a par value of one thousand dollars, pays a four percent annual coupon in two semiannual installments, and matures in ten years. If the market yield to maturity is five and a half percent, what is its fair price?",
            "informal": "price of a 1000 par bond, 4% coupon semiannual, 10 yrs left, ytm 5.5%?",
            "embedded": "We need to verify a security master price. The bond is $1,000 par, 4% coupon paid twice a year, 10 years to maturity, priced at a 5.5% yield. What price should appear?",
            "misleading": "A vendor file priced a $1,000 par, 4% semiannual coupon, 10-year bond at a 5.5% yield at $1,000 because it pays its coupon on schedule. What is the correct price?",
        },
    },
]

STYLES = ("direct", "wordy", "informal", "embedded", "misleading")


# Request and reconciliation settings.
PROMPT = (
    "Answer the question and give the final numeric result on its own line, "
    "written as FINAL: number. Do not put commas, currency signs, or percent signs "
    "on that line. You may show your calculation above it."
)
COLUMNS = (
    "model", "case", "style", "run", "golden", "hint_value",
    "model_answer", "difference", "status", "raw_response",
    "question", "tolerance", "error", "simulated",
    "stop_reason", "input_tokens", "output_tokens", "content_types", "no_answer_reason"
)


def read_answer(response):
    # Read the last FINAL line. If there isn't one, review the response manually.
    matches = re.findall(r"(?im)^[ \t]*FINAL:[ \t]*([-+]?(?:\d+(?:\.\d*)?|\.\d+))[ \t]*$", response)
    return float(matches[-1]) if matches else None


def check_answer(answer, case, wording):
    if answer is None:
        return "NO_ANSWER"
    if abs(answer - case["golden"]) <= case["tolerance"]:
        return "MATCH"
    if wording == "misleading" and abs(answer - case["hint_value"]) <= case["tolerance"]:
        return "ANCHORED"
    return "BREAK"


# Original names are kept as aliases so older examples still work.
extract_number = read_answer

def classify(value, case, style="misleading"):
    return check_answer(value, case, style)

def pretend_answer(case, wording, run, model="dry-run-model"):
    """Sample responses for checking the script. These are not model observations."""
    if wording == "misleading" and run == 1 and "misleading" in model:
        value = case["hint_value"]
    elif wording == "informal" and run == 1:
        value = case["golden"] * 1.03
    else:
        value = case["golden"]
    return f"Example calculation (simulated).\nFINAL: {value:.4f}"


def ask_anthropic(client, model, question, max_tokens=3000):
    message = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=PROMPT,
        messages=[{"role": "user", "content": question}],
    )
    # Save metadata so an empty or unfinished response can be investigated.
    content = getattr(message, "content", [])
    response = "\n".join(part.text for part in content if getattr(part, "type", "") == "text")
    usage = getattr(message, "usage", None)
    meta = {
        "stop_reason": getattr(message, "stop_reason", "") or "",
        "input_tokens": getattr(usage, "input_tokens", "") if usage else "",
        "output_tokens": getattr(usage, "output_tokens", "") if usage else "",
        "content_types": ",".join(str(getattr(part, "type", "unknown")) for part in content),
    }
    return response, meta


def missing_answer_reason(response, stop_reason=""):
    if not response.strip():
        return "EMPTY_TEXT"
    if stop_reason == "max_tokens":
        return "TOKEN_LIMIT"
    return "MISSING_FINAL_LINE"


def percentage(correct, total):
    return f"{correct}/{total} ({correct / total:.0%})" if total else "—"


def make_report(rows, models, runs, simulated):
    """Build the full reconciliation report from the individual attempts."""
    lines = ["# Financial question consistency — results", ""]
    if simulated:
        lines += ["**SIMULATED DATA — for checking the script only. Not real model findings.**", ""]
    lines += [
        f"Run date (UTC): {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')}",
        f"Repeats per phrasing: {runs}. Total attempts: {len(rows)}.",
        "A correct result is MATCH; API failures are ERROR, not model mistakes.", "",
        "## 1. Accuracy by model and phrasing", "",
        "| Phrasing | " + " | ".join(models) + " |",
        "|---|" + "---|" * len(models),
    ]
    for style in STYLES:
        cells = []
        for model in models:
            subset = [r for r in rows if r["model"] == model and r["style"] == style]
            valid = [r for r in subset if r["status"] != "ERROR"]
            matches = sum(r["status"] == "MATCH" for r in valid)
            cells.append(percentage(matches, len(valid)))
        lines.append(f"| {style} | " + " | ".join(cells) + " |")
    cells = []
    for model in models:
        valid = [r for r in rows if r["model"] == model and r["status"] != "ERROR"]
        cells.append("**" + percentage(sum(r["status"] == "MATCH" for r in valid), len(valid)) + "**")
    lines.append("| **Overall** | " + " | ".join(cells) + " |")
    lines += ["", "Accuracy excludes API errors from the denominator; see the error counts below.", "",
              "## 2. Failure types", "",
              "| Model | MATCH | ANCHORED | BREAK | NO_ANSWER | ERROR |",
              "|---|---:|---:|---:|---:|---:|"]
    for model in models:
        counts = Counter(r["status"] for r in rows if r["model"] == model)
        lines.append(f"| {model} | " + " | ".join(str(counts[s]) for s in ("MATCH", "ANCHORED", "BREAK", "NO_ANSWER", "ERROR")) + " |")
    lines += ["", "## 3. Consistency by calculation", "",
              "Spread = highest numerical answer minus lowest, across phrasing variations and repeated runs.",
              "A * indicates that the spread exceeded the calculation's tolerance.", "",
              "| Calculation | Correct answer | Tolerance | " + " | ".join(m + " spread" for m in models) + " |",
              "|---|---:|---:|" + "---:|" * len(models)]
    for case in TEST_CASES:
        cells = []
        for model in models:
            values = [r["model_answer"] for r in rows if r["model"] == model and r["case"] == case["id"] and r["model_answer"] != ""]
            if values:
                spread = max(values) - min(values)
                cells.append(f"{spread:.4f}" + (" *" if spread > case["tolerance"] else ""))
            else:
                cells.append("—")
        lines.append(f"| {case['id']} | {case['golden']:.4f} | {case['tolerance']:.2f} | " + " | ".join(cells) + " |")
    lines += ["", "## 4. Every non-matching answer or failed request", "",
              "| Model | Calculation | Phrasing | Run | Model answer | Correct | Difference | Status |",
              "|---|---|---|---:|---:|---:|---:|---|"]
    # Keep requests randomized during the run, but list exceptions in a stable order.
    # Group first by model, then calculation, phrasing, and repeat number.
    case_order = {case["id"]: i for i, case in enumerate(TEST_CASES)}
    style_order = {style: i for i, style in enumerate(STYLES)}
    model_order = {model: i for i, model in enumerate(models)}
    problems = sorted(
        (r for r in rows if r["status"] != "MATCH"),
        key=lambda r: (
            model_order.get(r["model"], len(models)),
            case_order.get(r["case"], len(TEST_CASES)),
            style_order.get(r["style"], len(STYLES)),
            int(r["run"]),
        ),
    )
    if not problems:
        lines.append("No exceptions.")
    else:
        for r in problems:
            answer = f"{r['model_answer']:.4f}" if r["model_answer"] != "" else "—"
            diff = f"{r['difference']:+.4f}" if r["difference"] != "" else "—"
            lines.append(f"| {r['model']} | {r['case']} | {r['style']} | {r['run']} | {answer} | {r['golden']:.4f} | {diff} | {r['status']} |")
    lines += ["", "## 5. API errors (if any)", ""]
    errors = [r for r in problems if r["status"] == "ERROR"]
    if errors:
        for r in errors:
            clean_error = str(r["error"]).replace("\n", " ").replace("|", "\\|")
            lines.append(f"- {r['model']} / {r['case']} / {r['style']} / run {r['run']}: {clean_error}")
    else:
        lines.append("No API errors recorded.")
    lines += ["", "## 6. Responses without a FINAL value", "",
              "These are response-format or completion issues; not automatically numerical errors.", "",
              "| Model | Empty text | Token limit | Missing FINAL line | Unknown cause |",
              "|---|---:|---:|---:|---:|"]
    for model in models:
        no_answers = [r for r in rows if r["model"] == model and r["status"] == "NO_ANSWER"]
        reasons = Counter(r.get("no_answer_reason", "") for r in no_answers)
        lines.append(f"| {model} | {reasons['EMPTY_TEXT']} | {reasons['TOKEN_LIMIT']} | {reasons['MISSING_FINAL_LINE']} | {reasons['']} |")
    lines += ["", "## Reading the findings", "",
              "- MATCH: the numerical answer was within the defined tolerance.",
              "- ANCHORED: on a misleading question, the answer equaled the planted incorrect hint. This alone does not prove causation.",
              "- BREAK: numerical answer differed from the reference and did not match the planted hint.",
              "- NO_ANSWER: no valid FINAL line was found; the calculation itself could still be right.",
              "- ERROR: the request could not be completed or processed; inspect the error field.", "",
              "Check the full response and original question in results.csv before interpreting a discrepancy.", ""]
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--models", nargs="+", default=["claude-haiku-5-5", "claude-sonnet-5-5"],
                        help="Anthropic model IDs (defaults from the original experiment; verify availability)")
    parser.add_argument("--runs", type=int, default=3, help="Number of repeats per question (default: 3)")
    parser.add_argument("--dry-run", action="store_true", help="Use simulated answers; makes no API calls")
    parser.add_argument("--output", default=".", help="Directory for result files (default: current directory)")
    parser.add_argument("--seed", type=int, default=42, help="Seed used to shuffle question order")
    parser.add_argument("--max-tokens", type=int, default=3000, help="Maximum output tokens per API response (default: 3000)")
    args = parser.parse_args(argv)
    if args.runs < 1:
        parser.error("--runs must be at least 1")
    if args.max_tokens < 1:
        parser.error("--max-tokens must be at least 1")

    models = ["dry-run-model", "dry-run-misleading-model"] if args.dry_run else args.models
    if not args.dry_run:
        try:
            import anthropic
            client = anthropic.Anthropic()
        except Exception as exc:
            parser.error(f"Could not initialize Anthropic client: {exc}")
    else:
        client = None

    tasks = [(model, case, wording, run)
             for model in models for case in TEST_CASES for wording in STYLES
             for run in range(1, args.runs + 1)]
    random.Random(args.seed).shuffle(tasks)
    rows = []
    for index, (model, case, wording, run) in enumerate(tasks, start=1):
        question = case["phrasings"][wording]
        error = ""
        meta = {"stop_reason": "", "input_tokens": "", "output_tokens": "", "content_types": ""}
        reason = ""
        try:
            if args.dry_run:
                response = pretend_answer(case, wording, run, model)
            else:
                response, meta = ask_anthropic(client, model, question, args.max_tokens)
            answer = read_answer(response)
            status = check_answer(answer, case, wording)
            if status == "NO_ANSWER":
                reason = missing_answer_reason(response, meta["stop_reason"])
        except Exception as exc:
            # Keep the unsuccessful request in the audit trail; do not treat it as a model failure.
            response, answer, status, error = "", None, "ERROR", str(exc)
        rows.append({
            "model": model, "case": case["id"], "style": wording, "run": run,
            "question": question, "golden": round(case["golden"], 6),
            "tolerance": case["tolerance"],
            "hint_value": case["hint_value"],
            "model_answer": answer if answer is not None else "",
            "difference": round(answer - case["golden"], 6) if answer is not None else "",
            "status": status, "raw_response": response, "error": error,
            "simulated": args.dry_run,
            **meta, "no_answer_reason": reason,
        })
        print(f"{index:>3}/{len(tasks)}  {model} / {case['id']} / {wording} / {run}: {status}")

    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    with (out / "results.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    report = make_report(rows, models, args.runs, args.dry_run)
    (out / "results.md").write_text(report, encoding="utf-8")
    (out / "summary.txt").write_text(report, encoding="utf-8")
    print("\n" + report)
    print(f"\nSaved {len(rows)} attempts to {out.resolve()}")
    print("Files: results.csv, results.md, summary.txt")
    print("Results are simulated." if args.dry_run else "Review all exceptions before reporting findings.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
