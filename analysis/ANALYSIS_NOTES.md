# What the two real runs show

In the first experiment, 131 of the 150 API responses had a correct number on a valid `FINAL:` line. The other 19 were marked `NO_ANSWER`. That label means the program could not extract a final number, not that 19 calculations were proven wrong.

After I raised the response limit from 1,000 to 3,000 tokens and saved more information about each API response, all 150 responses in the second experiment were classified `MATCH`. **The second run had no recorded numerical errors, missing final answers, or API errors.** This is the observed result, not a claim about all possible questions or future runs.

## What I checked

* Both original CSV files have 150 unique test identifiers and contain real API responses rather than simulated data.
* Both sets use the same model IDs, questions, calculations, hint values, tolerances, parsing rules, and system prompt.
* The 19 test identifiers without a final answer in the first run all returned `MATCH` in the second run.
* Of the first run's 19 `NO_ANSWER` responses, six have no saved text. Six others visibly contain the correct number without the required final line. Seven remain unresolved from their saved text. These observations do not change the original results.
* In the second run, 19 responses used more than 1,000 output tokens. Eleven corresponded to test identifiers that had `NO_ANSWER` in the first run. The other eight previously unsuccessful identifiers used 1,000 or fewer tokens in the second run.
* All 150 second-run responses have the API stop reason `end_turn`.

## Why the token counts do not prove the cause

The API's output usage includes generated output not always shown in the saved text. In the second run, 132 responses reported both `thinking` and `text` content blocks. The 1,000-token threshold refers to total output usage, not the length of the visible final explanation.

A longer allowance plausibly helped some responses finish, but the experiments ran at different times. The first run did not record stop reasons or token counts, and the second run generated fresh responses. I cannot prove that the token limit alone caused all 19 first-run exceptions.

## How the paired file works

`paired_runs.csv` puts the first and second run side by side for each combination of model, financial problem, wording, and repeat number. The two rows represent the same test setup, but each API call generated a new answer. The original records are not changed.

## How to verify

From the repository's top folder:

```powershell
python analysis/verify_results.py
python analysis/recompute_metrics.py
```

The first command checks original source-file hashes, formulas, responses, classification rules, counts, paired records, and file checksums. The second prints the main comparison totals. Neither calls the Anthropic API.
