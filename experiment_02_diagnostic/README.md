# Financial answer consistency: does wording change the result?

Aleksandr Kobichev: independent experiment, November 2026

## Why I started this

In financial reporting, I learned not to assume a number is correct just because the report ran without errors. When something didn't reconcile, I needed to find the source, reproduce the calculation, and figure out where the difference came from. That was often more useful than simply marking a report as failed.

I wanted to try a similar check with language models. If I ask the same financial question in different ways, will the model keep giving the right answer? And what happens when I include an incorrect number in the question itself?

This is a small study, not a general assessment of model reliability. I kept the individual responses so I could investigate exceptions instead of relying only on an accuracy percentage.

## What I am testing

I use five calculations that I can verify independently in Python: compound interest, monthly mortgage payment, realized gain, annualized return, and bond pricing.

Each calculation is asked five ways: `direct`, `wordy`, `informal`, `embedded` in a business request, and `misleading` (the question includes a wrong answer). The financial inputs stay the same. I also repeat each question to see whether the answer changes on a second or third attempt.

The expected values come from Python formulas in `experiment.py`, not from the model. I allow a small difference for rounding. The tolerance is specific to each calculation.

## How I check the answers

The model is asked to end its response with `FINAL: number`. I extract that number and compare it with my calculated result.

| Status | What it tells me |
| --- | --- |
| `MATCH` | The answer is within the allowed tolerance. |
| `ANCHORED` | For a *misleading* question only, the answer matches the deliberately incorrect hint. This is a flag for investigation, not proof of influence. |
| `BREAK` | The answer is outside tolerance for another reason. |
| `NO_ANSWER` | The expected `FINAL:` line wasn't found; I still need to inspect the response. |
| `ERROR` | The API request failed; this is not counted as a numerical model error. |

Each attempt is recorded in `results.csv`, along with the exact question and full response. I can then compare versions of the same calculation, look at the arithmetic, and check whether the model misunderstood the assumptions or simply used a different final-answer format.

## Running it on Windows PowerShell

From the folder containing `experiment.py`:

```powershell
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python experiment.py --dry-run --runs 1 --output sample_run
```

The dry run compares two **simulated models** to test the comparison and report generation. These are not Anthropic results.

Set your API key in the same PowerShell window:

```powershell
$env:ANTHROPIC_API_KEY="your-api-key"
```

For a small live check, use a model ID supported by your Anthropic account:

```powershell
python experiment.py --models claude-haiku-5-5 --runs 1 --output first_live_run
```

For the full comparison:

```powershell
python experiment.py --models claude-haiku-5-5 claude-sonnet-5-5 --runs 3 --output full_live_run
```

If you leave out `--models`, the program uses the two model IDs from the original experiment (`claude-haiku-5-5` and `claude-sonnet-5-5`). Check whether your API account supports those IDs before running; a missing model will be recorded as an API error. With two models and three repetitions, the script makes **150 API requests** (5 cases × 5 phrasings × 3 repeats × 2 models). API usage is billed by Anthropic. The script does not set temperature explicitly, so the model/API default applies. It shuffles request order with a fixed seed (`--seed 42` by default). Model settings and SDK versions can make it harder to reproduce the same results.

## Files and results

The main experiment lives in **one file**: `experiment.py`. It includes the calculations, questions, API calls, response parsing, reconciliation, and summary-report logic.

- `tests/test_experiment.py`: a few local checks for the formulas, parsing, classifications, and reports. No API requests.
- `REVIEW_NOTES.md`: completed investigation notes based on the actual API results.
- `requirements.txt`: Anthropic SDK dependency.
- `.gitignore`: prevents local results, credentials, and Python cache files from being committed by accident.

Each run creates the same three report files as the initial experiment:

- `results.csv`: every response, the expected value, difference, status, the complete question, and the full raw response.
- `results.md`: accuracy by wording, failure breakdown, answer spread by calculation, non-matching answers, and API errors.
- `summary.txt`: the same complete summary in a text file.

The complete summary is also printed in the terminal. By default, files are written to the **current working directory**, like the original script. Use `--output folder_name` to keep runs separate rather than overwrite previous results.

## What the completed second run showed

The actual follow-up contains 150 API requests, 75 per model. All 150 were recorded as `MATCH`. There were no `NO_ANSWER`, `BREAK`, `ANCHORED`, or API `ERROR` records, and every stop reason was `end_turn`. All 19 matching test cases that had `NO_ANSWER` in the first run received `MATCH` here.

Nineteen second-run responses used more than 1,000 total output tokens, including 11 tasks previously marked `NO_ANSWER`. The other eight previously unsuccessful tasks used 1,000 or fewer output tokens in this run. This supports the output-limit hypothesis for some responses, but does not establish that increasing the limit alone caused all the improvement. See `REVIEW_NOTES.md` and `../analysis/ANALYSIS_NOTES.md` for the detailed comparison.

This is a small sample of five financial problems, five phrasings, and three repetitions per model. It does not prove universal numerical accuracy or fully isolate the effect of the response length limit.

### Order of results

The API requests are shuffled during execution. `results.csv` keeps that execution order so the raw run can be audited. The exception table in `results.md` and `summary.txt` is sorted by model, calculation, phrasing, then repeat number. A `NO_ANSWER` means the parser did not find a properly formatted `FINAL:` line; inspect `raw_response` in `results.csv` before drawing conclusions about the model's calculation.

## Reviewing a run that already finished

Do not repeat 150 API calls just to check the original results. From the project folder:

```powershell
python review_previous_run.py actual_run/results.csv --output original_run_review
```

This creates a sorted `exceptions_to_review.csv` and a separate `review_summary.md` without modifying the source data. It deliberately does not call a number correct merely because that number happens to appear somewhere in the reasoning.

## Diagnosing missing answers on a new run

The original run used 1,000 output tokens per request and did not save API stop reasons. The updated runner uses 3,000 by default (change with `--max-tokens`) and saves `stop_reason`, token usage, and response content types in `results.csv`. A missing `FINAL:` line remains `NO_ANSWER`, with a separate reason for empty text, token limit, or missing format.

Use a **new output folder** for the next run. Different token budgets change the testing conditions and should not be mixed with the original baseline. More output tokens may increase cost; the maximum is a cap, not a guarantee of usage.
