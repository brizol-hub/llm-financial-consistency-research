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

If you leave out `--models`, the program uses the two IDs from my first script (`claude-haiku-5-5` and `claude-sonnet-5-5`). Check whether your API account supports those IDs before running; a missing model will be recorded as an API error. With two models and three repetitions, the script makes **150 API requests** (5 cases × 5 phrasings × 3 repeats × 2 models). API usage is billed by Anthropic. The script does not set temperature explicitly, so the model/API default applies. It shuffles request order with a fixed seed (`--seed 42` by default). Model settings and SDK versions can make it harder to reproduce the same results.

## Files and results

The main experiment lives in **one file**: `experiment.py`. It includes the calculations, questions, API calls, response parsing, reconciliation, and summary-report logic.

- `tests/test_experiment.py`: a few local checks for the formulas, parsing, classifications, and reports. No API requests.
- `REVIEW_NOTES.md`: completed investigation notes based on the actual API results.
- `requirements.txt`: Anthropic SDK dependency.
- `.gitignore`: prevents local results, credentials, and Python cache files from being committed by accident.

Each run creates the same three reports as my first script:

- `results.csv`: every response, the expected value, difference, status, the complete question, and the full raw response.
- `results.md`: accuracy by wording, failure breakdown, answer spread by calculation, non-matching answers, and API errors.
- `summary.txt`: the same complete summary in a text file.

The complete summary is also printed in the terminal. By default, files are written to the **current working directory**, like the original script. Use `--output folder_name` to keep runs separate rather than overwrite previous results.

## What the completed first run showed

The real first run made 150 API requests, 75 per model. It recorded 131 `MATCH` and 19 `NO_ANSWER`, with no extracted `BREAK` or `ANCHORED` values and no recorded API errors. I examined all 19 exceptions: six had no saved text, six contained a correct value without a valid `FINAL:` line, and seven had text from which I could not establish a correct final answer. Those exceptions are not 19 proven calculation mistakes.

This finding led to a follow-up with a larger response length limit and response-completion diagnostics. All 19 previously unsuccessful matching test cases received `MATCH` in that second run. See `REVIEW_NOTES.md` in this folder and `../experiment_02_diagnostic/REVIEW_NOTES.md` for what was investigated and the remaining uncertainty about the cause.

The questions and sample are limited: five financial problems, five phrasings, three repetitions, and one misleading hint per calculation. I do not generalize the observed success rates to other models, financial problems, or future deployments.
