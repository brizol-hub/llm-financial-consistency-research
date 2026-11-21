# Review of Experiment 2: diagnostic follow-up

## Why I ran it

The first experiment had 19 `NO_ANSWER` records out of 150 requests. I wanted to see whether allowing longer outputs and recording completion diagnostics would make the answers reliably usable by the program. This was a follow-up to a specific problem observed in the first run, not a new set of financial questions.

I kept both model IDs (`claude-haiku-5-5`, `claude-sonnet-5-5`), all five calculations, all 25 question wordings, three attempts per wording and model, expected answers, tolerances, and the `FINAL:` extraction rule. The revised program increased the maximum response length limit from 1,000 to 3,000 tokens and recorded the stop reason, token usage, content types, and missing-answer diagnostics. The CSV does not record the exact launch command or execution timestamp, so the output setting is supported by the included source and run notes rather than a per-request command log.

**Evidence reviewed:** `actual_run/results.csv`, `actual_run/results.md`, `actual_run/summary.txt`, the included `experiment.py`, and the original first-run CSV. The saved rows are marked as real API responses, not dry-run data.

## Results of the follow-up

| Recorded outcome | Haiku | Sonnet | Total |
| --- | ---: | ---: | ---: |
| `MATCH` | 75 | 75 | 150 |
| `NO_ANSWER` | 0 | 0 | 0 |
| `BREAK` | 0 | 0 | 0 |
| `ANCHORED` | 0 | 0 | 0 |
| API `ERROR` | 0 | 0 | 0 |
| Total | 75 | 75 | 150 |

**Every recorded follow-up request was classified `MATCH`.** All 30 attempts in each wording category matched, and all 150 API stop reasons were `end_turn`. The program successfully extracted the required final number in every response, and each number was within the preset tolerance of the independently calculated answer.

The 19 test identities that had `NO_ANSWER` in the first run all received `MATCH` in this follow-up. The comparison matches requests by model, calculation, wording, and repeat number. It does not mean the second run reproduced or continued the exact same generated response.

## What the additional diagnostics showed

In the second run, 19 of 150 responses used **more than 1,000 total output tokens**. Eleven of those 19 correspond to test identities that had failed the parser in the first run. Eight of the previously unsuccessful test identities succeeded in the second run with 1,000 or fewer output tokens.

The saved content types show 132 responses with `thinking,text` and 18 with `text` only. This matters because the recorded output-token usage can include internal reasoning content not shown in the visible answer. It is not necessarily the number of tokens in the visible explanation.

The token evidence supports the idea that a larger allowance was useful for some requests. But it **does not prove** that the lower allowance caused every first-run exception. The first run did not retain token counts or stop reasons; the two runs happened at different times; and each request generated a fresh answer. Other factors, including normal response variability, could have contributed.

## What I would have done if this had not worked

If `NO_ANSWER` had continued, I would have inspected the new stop reasons and content types first. For `max_tokens` stops, I would have tested different token limits while holding the rest of the settings steady. For normally completed answers missing `FINAL:`, I would have tried a shorter response instruction or a separate, explicitly documented parsing experiment. For empty text, I would have examined the response content types and API metadata. I also would have repeated the affected tasks to see whether the failures were consistent.

These steps are a contingency plan, not experiments or results that I am claiming to have completed.

## What I learned and the limits of this result

The revised setup had **150 correct, machine-readable answers out of 150 observed requests**, with no missing final answers and no recorded numerical exceptions. That is the outcome of this follow-up, not a guarantee that the models will always give correct financial answers. The experiment covers only five calculations, five wording styles, and three repetitions.

The more important lesson for me was to separate mathematical correctness from the reliability of the evaluation process. The first run made some results look like failures because the program could not extract a final number. The second run showed that the revised setup handled every tested request successfully. I can report that improvement confidently, while remaining cautious about claiming a single proven cause.

Both real-run CSVs remain unchanged. See `../analysis/ANALYSIS_NOTES.md` and `../analysis/paired_runs.csv` for the paired comparison, and `../analysis/VERIFICATION_REPORT.md` for the data checks.
