# Financial question consistency — results

Run date (UTC): 2026-11-20 20:36
Repeats per phrasing: 3. Total attempts: 150.
A correct result is MATCH; API failures are ERROR, not model mistakes.

## 1. Accuracy by model and phrasing

| Phrasing | claude-haiku-5-5 | claude-sonnet-5-5 |
|---|---|---|
| direct | 12/15 (80%) | 15/15 (100%) |
| wordy | 11/15 (73%) | 13/15 (87%) |
| informal | 15/15 (100%) | 15/15 (100%) |
| embedded | 12/15 (80%) | 15/15 (100%) |
| misleading | 10/15 (67%) | 13/15 (87%) |
| **Overall** | **60/75 (80%)** | **71/75 (95%)** |

Accuracy excludes API errors from the denominator; see the error counts below.

## 2. Failure types

| Model | MATCH | ANCHORED | BREAK | NO_ANSWER | ERROR |
|---|---:|---:|---:|---:|---:|
| claude-haiku-5-5 | 60 | 0 | 0 | 15 | 0 |
| claude-sonnet-5-5 | 71 | 0 | 0 | 4 | 0 |

## 3. Consistency by calculation

Spread = highest numerical answer minus lowest, across phrasing variations and repeated runs.
A * indicates that the spread exceeded the calculation's tolerance.

| Calculation | Correct answer | Tolerance | claude-haiku-5-5 spread | claude-sonnet-5-5 spread |
|---|---:|---:|---:|---:|
| compound_interest | 16470.0950 | 1.00 | 0.0000 | 0.0000 |
| mortgage_payment | 1896.2041 | 1.00 | 0.2000 | 0.0000 |
| realized_gain | 3917.6000 | 0.01 | 0.0000 | 0.0000 |
| annualized_return | 7.3228 | 0.05 | 0.0100 | 0.0000 |
| bond_price | 885.7956 | 0.50 | 0.1400 | 0.0000 |

## 4. Every non-matching answer or failed request

| Model | Calculation | Phrasing | Run | Model answer | Correct | Difference | Status |
|---|---|---|---:|---:|---:|---:|---|
| claude-haiku-5-5 | mortgage_payment | wordy | 1 | — | 1896.2041 | — | NO_ANSWER |
| claude-haiku-5-5 | mortgage_payment | direct | 2 | — | 1896.2041 | — | NO_ANSWER |
| claude-sonnet-5-5 | mortgage_payment | misleading | 3 | — | 1896.2041 | — | NO_ANSWER |
| claude-haiku-5-5 | bond_price | wordy | 2 | — | 885.7956 | — | NO_ANSWER |
| claude-haiku-5-5 | mortgage_payment | direct | 3 | — | 1896.2041 | — | NO_ANSWER |
| claude-haiku-5-5 | mortgage_payment | embedded | 2 | — | 1896.2041 | — | NO_ANSWER |
| claude-haiku-5-5 | bond_price | embedded | 1 | — | 885.7956 | — | NO_ANSWER |
| claude-haiku-5-5 | bond_price | misleading | 3 | — | 885.7956 | — | NO_ANSWER |
| claude-sonnet-5-5 | mortgage_payment | wordy | 2 | — | 1896.2041 | — | NO_ANSWER |
| claude-haiku-5-5 | mortgage_payment | embedded | 1 | — | 1896.2041 | — | NO_ANSWER |
| claude-haiku-5-5 | bond_price | misleading | 2 | — | 885.7956 | — | NO_ANSWER |
| claude-sonnet-5-5 | mortgage_payment | wordy | 1 | — | 1896.2041 | — | NO_ANSWER |
| claude-haiku-5-5 | annualized_return | direct | 1 | — | 7.3228 | — | NO_ANSWER |
| claude-haiku-5-5 | mortgage_payment | misleading | 1 | — | 1896.2041 | — | NO_ANSWER |
| claude-haiku-5-5 | mortgage_payment | wordy | 2 | — | 1896.2041 | — | NO_ANSWER |
| claude-haiku-5-5 | mortgage_payment | wordy | 3 | — | 1896.2041 | — | NO_ANSWER |
| claude-sonnet-5-5 | bond_price | misleading | 2 | — | 885.7956 | — | NO_ANSWER |
| claude-haiku-5-5 | annualized_return | misleading | 3 | — | 7.3228 | — | NO_ANSWER |
| claude-haiku-5-5 | mortgage_payment | misleading | 2 | — | 1896.2041 | — | NO_ANSWER |

## 5. API errors (if any)

No API errors recorded.

## Reading the findings

- MATCH: the numerical answer was within the defined tolerance.
- ANCHORED: on a misleading question, the answer equaled the planted incorrect hint. This alone does not prove causation.
- BREAK: numerical answer differed from the reference and did not match the planted hint.
- NO_ANSWER: no valid FINAL line was found; the calculation itself could still be right.
- ERROR: the request could not be completed or processed; inspect the error field.

Check the full response and original question in results.csv before interpreting a discrepancy.
