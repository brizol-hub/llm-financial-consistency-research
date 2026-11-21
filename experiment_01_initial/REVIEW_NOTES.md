# Review of Experiment 1: initial real API run

## What I was checking

I wanted to know whether two Claude models would calculate the same financial answers when I changed the wording of the questions. I used five calculations, five versions of each question, and three attempts per model and wording. This produced 150 API requests: 75 to `claude-haiku-5-5` and 75 to `claude-sonnet-5-5`.

The five wordings were direct, wordy, informal, embedded in a work request, and misleading (containing an intentionally incorrect number). I calculated the expected values in Python before sending the questions to the models. The program required each model response to finish with a line in the form `FINAL: 123.45`.

**Evidence reviewed:** `actual_run/results.csv`, `actual_run/results.md`, `actual_run/summary.txt`, and the included `experiment.py`. The CSV identifies these records as real responses rather than simulated ones. The source code used a maximum response length limit of 1,000 tokens. The CSV does not contain a per-request timestamp, API stop reason, or token usage. The project records the study in November 2026, but the precise execution time cannot be confirmed from this CSV.

## What the first run actually produced

| Recorded outcome | Haiku | Sonnet | Total |
| --- | ---: | ---: | ---: |
| `MATCH` | 60 | 71 | 131 |
| `NO_ANSWER` | 15 | 4 | 19 |
| `BREAK` | 0 | 0 | 0 |
| `ANCHORED` | 0 | 0 | 0 |
| API `ERROR` | 0 | 0 | 0 |
| Total | 75 | 75 | 150 |

The combined `MATCH` rate was 131 / 150, or 87.3%. This is the rate of *correct numbers appearing in the required final-line format*, not a pure measure of mathematical accuracy. A `NO_ANSWER` indicates that the parser could not extract a valid final number. It does not establish that the model calculated incorrectly.

The 19 `NO_ANSWER` records were concentrated in the longer calculations:

| Calculation | Haiku | Sonnet | Total |
| --- | ---: | ---: | ---: |
| Mortgage payment | 9 | 3 | 12 |
| Bond price | 4 | 1 | 5 |
| Annualized return | 2 | 0 | 2 |
| Compound interest | 0 | 0 | 0 |
| Realized gain | 0 | 0 | 0 |

By wording, the 19 exceptions were: misleading 7, wordy 6, direct 3, embedded 3, and informal 0. These are descriptive counts for this small experiment, not evidence that one wording is generally more difficult.

## What I found when I examined the exceptions

Six of the 19 records have no saved response text. Thirteen contain text but no final line the parser could read. In six of those text-containing records, the expected answer is visibly present in the response even though the required `FINAL:` line is missing. For example, some mortgage responses state approximately $1,896.20, and some bond responses state approximately $885.80. These observations do not change the original classifications. They show why I should not describe all 19 as calculation failures.

The other seven text-containing records end partway through an explanation or cannot be assigned a definitive final number from the stored text. Several responses appear incomplete. Because this run did not save the API stop reason or token usage, I cannot tell from the data alone whether the 1,000-token response length limit, model variability, or another factor produced a particular missing final answer.

No response was classified `BREAK`, and none was classified `ANCHORED`. This means no *successfully extracted* response was numerically wrong or matched the planted incorrect hint under the program's checks. It does not mean the 19 unparsed responses were all correct.

## What I decided to investigate next

I suspected that the 1,000-token response length limit might be too small for some of the longer mortgage and bond calculations. I also wanted to tell the difference between a response that was cut off, one that omitted the final line, and one that returned no saved text.

I planned a follow-up with the **same two models, five calculations, 25 wordings, three repeats, expected values, and parsing rule**. The revised runner would increase the response length limit to 3,000 tokens and record the API stop reason, token usage, content types, and a reason for a missing answer. I kept the original CSV and reports intact so that the two runs could be compared.

If the follow-up still produced missing answers, my next steps would have been to inspect the recorded stop reasons, isolate the affected questions, test a less verbose answer instruction, consider a separate numeric-answer extraction check, and repeat under controlled output limits. These were possible next investigations, not tests that were actually completed in this project.

## What this run did and did not establish

The run revealed a problem in the end-to-end evaluation process: some responses could not be used by the strict parser. It did not prove 19 mathematical errors. It also did not establish the exact cause of the missing answers. With five calculation types and one misleading hint per question, I cannot generalize these results to all financial questions or all language-model behavior.

The raw response records and original classifications remain in `actual_run/results.csv`. The paired comparison with the follow-up is documented in `../analysis/ANALYSIS_NOTES.md`.
