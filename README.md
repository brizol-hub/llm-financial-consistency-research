# LLM Financial Consistency Research

**Aleksandr Kobichev | November 2026**

I tested whether two language models could solve the same financial calculations when the questions were worded differently or included a misleading answer. I used five financial calculations and five question variations, then repeated each variation three times with each model. That produced 150 API requests per experiment.

In the first run, 131 responses contained a correct result in the required `FINAL:` format. The other 19 were classified `NO_ANSWER`, meaning the program could not extract the required final number. In the second run, after I increased the output-token allowance and collected more information about response completion, all 150 responses matched the independently calculated answers.

## Research Paper

**[Read the full research paper (PDF)](RESEARCH_PAPER.pdf)** | [Read online (Markdown)](RESEARCH_PAPER.md)

*When a Correct AI Answer Looks Like a Failure*

## Results at a Glance

I tested Claude Haiku 5.5 and Claude Sonnet 5.5 across five financial calculations, five question styles, and three repetitions per model. Each experiment contained 150 API requests.

| Result                                           | Experiment 1 | Experiment 2 |
|--------------------------------------------------|-------------:|-------------:|
| API requests                                     | 150          | 150          |
| Correct answers in required `FINAL:` format      | 131 (87.3%)  | 150 (100%)   |
| `NO_ANSWER` classifications                      | 19           | 0            |
| Recorded numerical `BREAK` or `ANCHORED` results | 0            | 0            |
| Maximum output tokens                            | 1,000        | 3,000        |

## Key Finding

My first experiment produced 19 `NO_ANSWER` classifications. After inspecting the saved responses, I found that six visibly contained the correct number but lacked the required `FINAL:` line. Six had no saved text, and seven remained unresolved from the available text.

In the second experiment, all 150 responses matched the independently calculated answers in the required format.

**The central lesson:** An evaluation can report an unsuccessful response without establishing that the model made a mathematical error. Calculation accuracy, response completion, and machine-readable formatting need to be examined separately.

## Limitations

This was a small exploratory study using five financial problems and two models. The second experiment increased the output-token allowance and recorded additional diagnostics, but the runs occurred at different times. Therefore, the results do not establish that the larger token allowance alone caused the improvement, nor do they demonstrate universal financial accuracy.

## Suggested Citation

Kobichev, Aleksandr. (2026). *When a Correct AI Answer Looks Like a Failure*. Independent research. https://github.com/brizol-hub/llm-financial-consistency-research


## Files and folders

| Location | Contents |
|---|---|
| `RESEARCH_PAPER.pdf` | Full research paper, including formulas, assumptions, both runs and conclusions |
| `RESEARCH_PAPER.docx` | Editable copy of the paper |
| `RESEARCH_PAPER.md` | Plain-text Markdown copy of the paper |
| `experiment_01_initial/` | First experiment's Python program, tests, dry-run option, and real results |
| `experiment_02_diagnostic/` | Second experiment's program, tests, additional diagnostics, and real results |
| `analysis/ANALYSIS_NOTES.md` | Comparison of the two runs and explanation of the exceptions |
| `analysis/paired_runs.csv` | Results from matching test setups shown side by side |
| `analysis/recompute_metrics.py` | Recalculates the main results from both CSV files |
| `analysis/verify_results.py` | Checks formulas, saved classifications, source files and results |
| `analysis/DATA_INTEGRITY.md` | Fingerprints of the original data and source files |
| `MANIFEST_SHA256.txt` | Checksums for the files in this project |

## Check the recorded results

From the project folder, run:

```powershell
python analysis/verify_results.py
python analysis/recompute_metrics.py
```

Neither command calls Anthropic or requires an API key.

To run a new experiment, open the appropriate experiment folder, install its `requirements.txt`, and follow the commands in its README. The `--dry-run` option uses simulated responses to test the program without making API requests. Simulated responses are not included in the research findings.

**Keep the saved `actual_run/` folders unchanged.** Choose a different output folder for new executions.

## How to interpret the results

`MATCH` means the program found a final number within the predefined tolerance. `NO_ANSWER` means it did not find a usable final number in the required format. It does not necessarily mean the financial calculation was wrong. The second run resolved the recorded missing-final-answer cases, but these two runs do not prove that the longer output limit was the only reason for the improvement.

The saved results include model response text, and the original API key is not included in this project.
