# Financial question consistency — results

Run date (UTC): 2026-11-20 21:27
Repeats per phrasing: 3. Total attempts: 150.
A correct result is MATCH; API failures are ERROR, not model mistakes.

## 1. Accuracy by model and phrasing

| Phrasing | claude-haiku-5-5 | claude-sonnet-5-5 |
|---|---|---|
| direct | 15/15 (100%) | 15/15 (100%) |
| wordy | 15/15 (100%) | 15/15 (100%) |
| informal | 15/15 (100%) | 15/15 (100%) |
| embedded | 15/15 (100%) | 15/15 (100%) |
| misleading | 15/15 (100%) | 15/15 (100%) |
| **Overall** | **75/75 (100%)** | **75/75 (100%)** |

Accuracy excludes API errors from the denominator; see the error counts below.

## 2. Failure types

| Model | MATCH | ANCHORED | BREAK | NO_ANSWER | ERROR |
|---|---:|---:|---:|---:|---:|
| claude-haiku-5-5 | 75 | 0 | 0 | 0 | 0 |
| claude-sonnet-5-5 | 75 | 0 | 0 | 0 | 0 |

## 3. Consistency by calculation

Spread = highest numerical answer minus lowest, across phrasing variations and repeated runs.
A * indicates that the spread exceeded the calculation's tolerance.

| Calculation | Correct answer | Tolerance | claude-haiku-5-5 spread | claude-sonnet-5-5 spread |
|---|---:|---:|---:|---:|
| compound_interest | 16470.0950 | 1.00 | 0.0100 | 0.0000 |
| mortgage_payment | 1896.2041 | 1.00 | 0.0100 | 0.0000 |
| realized_gain | 3917.6000 | 0.01 | 0.0000 | 0.0000 |
| annualized_return | 7.3228 | 0.05 | 0.0000 | 0.0000 |
| bond_price | 885.7956 | 0.50 | 0.0700 | 0.0000 |

## 4. Every non-matching answer or failed request

| Model | Calculation | Phrasing | Run | Model answer | Correct | Difference | Status |
|---|---|---|---:|---:|---:|---:|---|
No exceptions.

## 5. API errors (if any)

No API errors recorded.

## 6. Responses without a FINAL value

These are response-format or completion issues; not automatically numerical errors.

| Model | Empty text | Token limit | Missing FINAL line | Unknown cause |
|---|---:|---:|---:|---:|
| claude-haiku-5-5 | 0 | 0 | 0 | 0 |
| claude-sonnet-5-5 | 0 | 0 | 0 | 0 |

## Reading the findings

- MATCH: the numerical answer was within the defined tolerance.
- ANCHORED: on a misleading question, the answer equaled the planted incorrect hint. This alone does not prove causation.
- BREAK: numerical answer differed from the reference and did not match the planted hint.
- NO_ANSWER: no valid FINAL line was found; the calculation itself could still be right.
- ERROR: the request could not be completed or processed; inspect the error field.

Check the full response and original question in results.csv before interpreting a discrepancy.
