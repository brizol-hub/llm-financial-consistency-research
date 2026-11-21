# LLM Financial Consistency Research

**Aleksandr Kobichev | November 2026**

I tested whether two language models could solve the same financial calculations when the questions were worded differently or included a misleading answer. I used five financial calculations and five question variations, then repeated each variation three times with each model. That produced 150 API requests per experiment.

In the first run, 131 responses contained a correct result in the required `FINAL:` format. The other 19 were classified `NO_ANSWER`, meaning the program could not extract the required final number. In the second run, after I increased the output-token allowance and collected more information about response completion, all 150 responses matched the independently calculated answers.

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
