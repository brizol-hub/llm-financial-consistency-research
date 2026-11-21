# Original data and source file checks

I kept the source code and results for each completed run unchanged. The following SHA256 fingerprints identify the files used in this study.

| File | SHA256 |
|---|---|
| `experiment_01_initial/actual_run/results.csv` | `0bcbbc2ace840f03bc405a72dd58b86064caccd6c17090e11fcefe207b532743` |
| `experiment_02_diagnostic/actual_run/results.csv` | `295c7bf039a4f99ea3e1bcdb5cde2dba61cde2a5ed06daad9039f5f1d0e5cc96` |
| `experiment_01_initial/experiment.py` | `10ccf01f71ac3d4fb5876631f3af79d743a2b729c9320d6549e62f52165374e8` |
| `experiment_02_diagnostic/experiment.py` | `ac8282d10b7588b2f091a256db9b3d5c9b0d03e023883dd337a6c6f7f8413112` |

The original CSV classifications are unchanged. `paired_runs.csv` combines the results for comparison but does not replace the original records. The verification program checks the saved values against the formulas and classification rules in each experiment.

The first program used `max_tokens=1000`. The second defaults to `max_tokens=3000`. The saved CSV files do not record the exact command used to start each run or the SDK version, and the first run did not save stop reasons or token counts. These limits are important when interpreting why the results differed.

The saved source code and results for each experiment are preserved in the two experiment folders. The completed investigation notes are in those folders as well.
