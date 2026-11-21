# When a Correct AI Answer Looks Like a Failure

## What I learned from two experiments with financial questions and AI models

**Aleksandr Kobichev**  
Independent research · November 2026  
Exploratory research based on two live API runs. This paper has not been peer reviewed.

## Abstract

I started with a practical question. Would an AI model calculate the same financial result if I changed how I asked the question, without changing the actual problem? I tested two Anthropic language models, Claude Haiku 5.5 and Claude Sonnet 5.5, on five financial calculations. Each calculation was written in five different ways and asked three times per model. That produced **150 API requests in each experiment**.

In the first experiment, **131 of 150 responses (87.3%)** contained a correct number in the precise format the program expected. The remaining **19 were labeled `NO_ANSWER`**. At first glance, that could suggest the models struggled with some questions. A closer look showed something different: six of those responses contained the correct number but not the required final line; six had no saved text; and seven contained text without a clearly visible correct final value.

I suspected that the program sometimes allowed too little space for the models to finish their answers. For my second experiment, I increased the maximum response length from **1,000 to 3,000 output tokens** and collected more information about why each response ended. I kept the financial problems, question wording, models, and scoring rules the same. This time, **all 150 responses were correctly formatted and matched the independent calculations**.

I cannot conclude that raising the token limit alone caused every improvement, because the experiments ran at different times and the first run did not record detailed completion information. The first test revealed a problem in **how the program captured and interpreted model answers**. When an AI test reports a failure, I need to find out whether the calculation was wrong, the answer was incomplete, or the software simply could not read what the model returned.

Keywords: language models, financial calculations, response format, output limits, repeatability.

## 1. Why I started this project

My experience in financial reporting taught me that a number is only useful when I know where it came from and can verify it independently. A reporting process may fail because the source number is wrong, because a report is incomplete, or because the next system cannot read its output. Those are different problems and need different fixes.

I wanted to bring that approach to a question about AI. Suppose two people ask for the value of the same investment. One uses formal language, while the other writes a quick message using abbreviations. The financial answer should be the same. I also wanted to see what would happen if a question included an **incorrect answer presented confidently as a hint**.

My original goal was to compare the mathematical consistency of two language models. During testing, I learned something else: **the program used to evaluate a model can create apparent failures of its own**. This paper follows the work in the order it happened: the question, the program, the first run, the investigation, the changes, and the second run.

This is a small, practical experiment rather than proof that any model is universally accurate or inaccurate.

## 2. The questions I wanted to answer

I began with two questions:

**Question 1: Does wording change the result?** If the facts and numbers remain the same, does a model still produce the correct answer when the question is formal, long, informal, or part of a work request?

**Question 2: Will a wrong hint influence the model?** If I include a confidently stated but incorrect result, will the model repeat it instead of calculating independently?

After the first run, I added a third question:

**Question 3: Can the testing program itself make a correct model look unsuccessful?** For example, could an answer be correct but arrive in a format the program cannot read, or could a response end before the final answer appears?

The first two questions were part of the original design. The third emerged **after I reviewed the results of the first run**. That distinction matters because a question developed after looking at the data is not the same as a hypothesis defined before testing.

### What I expected

I thought long questions or incorrect hints *might* create more mistakes. I also thought the two models *might* behave differently. These were possibilities to investigate, not conclusions I had already reached. I did not assume that every missing final answer was a wrong calculation.

## 3. The five financial calculations

To evaluate an answer, I first needed an **independent reference value**. This is the answer calculated by a formula, without relying on the AI model being evaluated. I used Python to calculate these reference values using standard financial formulas. The program then compared the model's number with the reference.

A small amount of rounding is normal, so each calculation had an **allowed difference**, called a *tolerance*. For example, a mortgage answer within $1 of the independently calculated payment counted as a match. These are practical thresholds chosen for this experiment, not official accounting or regulatory standards.

### 3.1. Compound interest: how much an investment grows

**Question:** If someone invests $10,000 at 5% annual interest, compounded monthly, how much will the investment be worth in 10 years?

**Formula:** `Future value = P × (1 + r/m)^(m×t)`

Here, `P` is the original investment, `r` is the annual interest rate written as a decimal, `m` is how often interest is added each year, and `t` is the number of years. Interest earned in one month also earns interest in later months.

**Values:** `P = 10,000`, `r = 0.05`, `m = 12`, `t = 10`.

**Reference answer:** **$16,470.09**. **Allowed difference:** $1.00. **Incorrect hint used in the misleading version:** $15,000.

### 3.2. Mortgage payment: the amount due each month

**Question:** What is the monthly principal-and-interest payment for a $300,000 mortgage over 30 years at 6.5% annual interest?

**Formula:** `Monthly payment = P×i / [1 − (1+i)^(−N)]`

Here, `P` is the amount borrowed, `i` is the monthly interest rate (`annual rate ÷ 12`), and `N` is the total number of monthly payments (`years × 12`). This formula includes paying down the loan principal, not just paying interest. When the monthly interest rate is zero, the payment is simply `P ÷ N`.

**Values:** `P = 300,000`, `i = 0.065/12`, `N = 360`.

**Reference answer:** **$1,896.20 per month**. **Allowed difference:** $1.00. **Incorrect hint:** $1,625, which represents monthly interest alone, not a full mortgage payment.

### 3.3. Realized gain: profit after buying and selling shares

**Question:** What is the net gain on 250 shares bought at $42.10 and sold at $57.85, after $19.90 in total fees?

**Formula:** `Gain = shares × (sale price − purchase price) − fees`

The formula finds the gain per share, multiplies it by the number of shares, and subtracts trading fees.

**Reference answer:** **$3,917.60**. **Allowed difference:** $0.01. **Incorrect hint:** $3,957.40.

### 3.4. Annualized return: an average yearly growth rate

**Question:** If an investment increases from $50,000 to $82,000 over seven years, what is its compound annual growth rate (CAGR)?

**Formula:** `CAGR (%) = 100 × [(ending value ÷ starting value)^(1/years) − 1]`

This gives the constant yearly growth rate that would produce the same overall result. Dividing the total gain percentage by seven would be incorrect, because investment growth compounds over time.

**Reference answer:** **about 7.32% per year**. **Allowed difference:** 0.05 *percentage points* (for example, 7.32% and 7.36% differ by 0.04 percentage points). **Incorrect hint:** 9.14%, based on dividing the total 64% gain by seven.

### 3.5. Bond price: the value of future payments

**Question:** What is the value of a $1,000 face-value bond with a 4% annual coupon paid twice a year, 10 years remaining, and a 5.5% market yield?

**Formula:** `Price = sum of each coupon payment discounted to today + face value discounted to today`

More precisely:

`Price = Σ[k=1 to N] { [F×(c/2)] / (1+y/2)^k } + F/(1+y/2)^N`

`F` is the face value, `c` is the annual coupon rate, `y` is the annual market yield, and `N` is the number of half-year periods (`2 × years`). The symbol `Σ` means **add up** the discounted value of each future coupon payment. Because the bond pays 4% but the market requires 5.5%, its price is below $1,000.

**Reference answer:** **$885.80**. **Allowed difference:** $0.50. **Incorrect hint:** $1,000.

All reference calculations kept more precision internally than the rounded figures shown in this paper, so rounding in the text did not determine whether a response matched.

## 4. How I designed and built the experiment

### 4.1. Five ways to ask the same question

Each of the five calculations appeared in five versions:

| Question style | Meaning | Example using compound interest |
|---|---|---|
| **Direct** | A straightforward textbook-style question | “What is the future value of $10,000 at 5% compounded monthly for 10 years?” |
| **Wordy** | Same numbers explained in longer prose | “Suppose an investor deposits ten thousand dollars…” |
| **Informal** | Everyday abbreviations | “If I put 10k in at 5%... after 10 yrs?” |
| **Embedded** | Question included in a realistic work request | “My client is reviewing her statement…” |
| **Misleading** | Includes a confident but incorrect answer | “A colleague told me the total should be $15,000. Is that right?” |

The essential facts remained the same in each version. The misleading number was deliberately wrong, so the expected answer did **not** change.

### 4.2. Why there were 150 requests per experiment

I used **two models**: `claude-haiku-5-5` and `claude-sonnet-5-5`.

For each model, I submitted five calculations, each written in five styles, and repeated each version three times. The count was:

**5 calculations × 5 styles × 3 repetitions × 2 models = 150 requests.**

Repeating a question allowed me to see whether the same model returned a different answer on another attempt. Three repetitions are enough for an initial check, but not for reliable estimates of rare errors.

### 4.3. Why the questions appeared out of order

The Python script **shuffled** the 150 requests with a fixed random seed (`42`) before running them. It sent **one request at a time**, not several requests simultaneously. This distributed questions for both models across the run rather than testing one model entirely before the other. The fixed seed made the request order reproducible in the program. Every record retained its model, calculation, question style, and repetition number, so the reports could group results correctly afterward.

### 4.4. How the Python program worked

The experiment was a single main Python program rather than a complicated research system. Its steps were:

1. **Calculate the expected answers** using Python formulas, independently of the AI.
2. **Prepare the questions**, including the five wordings for each financial problem.
3. **Build the list of requests** for both models and all three repetitions, then shuffle the list.
4. **Call the Anthropic API** for each request. The program asked the model to end with a separate line in the format `FINAL: 16470.09`.
5. **Read the response** and look for the last valid `FINAL:` line.
6. **Compare the number** with the reference value using the preselected tolerance.
7. **Save the record** in `results.csv`, along with the model name, question type, response, calculated difference, and status; create `results.md` and `summary.txt` as readable summaries.

For example, for the mortgage question, Python calculates $1,896.20. A model may explain its work and end with `FINAL: 1896.20`. The program reads `1896.20`, checks whether it differs from the reference by no more than $1, and records `MATCH`. If the response instead says “The payment is about $1,896.20” but never prints a valid `FINAL:` line, the original parser records `NO_ANSWER` even though the correct value is visible. That distinction became central to my research.

### 4.5. What the result labels actually mean

| Label | What the program recorded | What a reader should understand |
|---|---|---|
| `MATCH` | Found a properly formatted number within tolerance | The answer was correct **and** readable by the program |
| `ANCHORED` | For a misleading question, the extracted wrong answer matched the planted hint | A possible hint-following event; this alone does not prove why it happened |
| `BREAK` | Found a number outside tolerance that did not match the hint | A visible numerical disagreement |
| `NO_ANSWER` | Could not find a valid standalone `FINAL:` value | May be missing, incomplete, or wrongly formatted; **not automatically a math error** |
| `ERROR` | An API call or processing step failed | A technical problem with the request or program, separate from arithmetic |

I reported the **share of responses that were both correct and readable by the program**: the number of `MATCH` records divided by all attempted requests. It is important to call it that, rather than simply “mathematical accuracy,” because it also depends on the model following the requested output format.

## 5. Assumptions and boundaries of the test

Every experiment relies on assumptions. I have listed the assumptions for this study so readers can judge what its results do and do not show.

1. **The five wordings mean the same thing.** Each phrasing keeps the relevant numbers and financial task unchanged. The misleading hint should not alter the underlying calculation.
2. **The independent formulas are appropriate.** I assumed, for example, no extra investment deposits or withdrawals, and a conventional fully amortizing mortgage without taxes or insurance.
3. **Small rounding differences are acceptable.** Tolerances were set for each case before assessing the responses. They are practical test settings, not regulatory thresholds.
4. **Requests do not share a conversation.** Each API request was a separate single-turn question; one answer was not fed into the next.
5. **The model versions are those available during testing.** I did not capture every internal deployment detail or randomness setting, and deployed services can change over time.
6. **The requested output format matters.** Requiring `FINAL: number` is reasonable for automatic processing, but failure to follow that format is not equivalent to incorrect mathematics.
7. **The sample is deliberately small.** Five calculations, five wordings, and three repetitions provide a useful initial investigation, not a comprehensive measure of financial AI reliability.
8. **The two runs were not a controlled laboratory trial.** They occurred at different times. I kept the same tasks and rules, but I cannot rule out normal variation in model responses or service behavior.

## 6. Experiment 1: what happened in the first real run

The first run used a maximum response allowance of **1,000 output tokens**. A *token* is a unit of text the model uses when generating a response; it is not exactly the same as a word. If a model spends many tokens explaining its work, it may reach the limit before printing the final answer.

### 6.1. Recorded results

| Model | Total requests | `MATCH` | `NO_ANSWER` | Other recorded errors | Correct and readable response rate |
|---|---:|---:|---:|---:|---:|
| Haiku 5.5 | 75 | 60 | 15 | 0 | 80.0% |
| Sonnet 5.5 | 75 | 71 | 4 | 0 | 94.7% |
| **Both** | **150** | **131** | **19** | **0** | **87.3%** |

No answer that the parser *successfully extracted* was recorded as a numerical `BREAK` or an `ANCHORED` hint match. That does not mean the other 19 responses were correct; it means their final values could not be scored by the strict rule.

The missing-answer results appeared mainly in mortgage payments (**12 cases**), bond pricing (**5 cases**), and annualized returns (**2 cases**). By wording, they occurred in misleading (**7**), wordy (**6**), direct (**3**), and embedded (**3**) questions. The informal style had none. These are small counts, so they should not be treated as proof that one wording is inherently harder.

### 6.2. Looking beyond the summary

I inspected the saved text of all 19 `NO_ANSWER` records instead of assuming they represented wrong financial calculations.

| What was visible in the saved response | Number of cases | What it suggests |
|---|---:|---|
| Correct answer appears, but no valid `FINAL:` line | 6 | The model gave a usable number to a human, but not in the requested machine-readable format |
| No text was saved | 6 | The original record did not show what happened to the response |
| Some text was saved, but no clearly correct final value was visible | 7 | The response may be incomplete or otherwise unresolved |
| **Total** | **19** | |

Combining the 131 strict matches with six additional responses where the correct value was visible gives **at least 137 of 150 (91.3%)** responses with an identifiable correct number. This is a *minimum observed count*, **not** a claim that all 13 unresolved responses were wrong or that 91.3% was the model's true math accuracy.

A `NO_ANSWER` result was not enough to establish whether the model made a calculation error, failed to complete its response, or simply missed the required format.

## 7. Investigating the missing answers

I considered three main explanations:

- **Not enough output space.** Some financial problems need a longer explanation. With only 1,000 tokens allowed, the model might not reach its final line.
- **A formatting mismatch.** The model might calculate correctly but write the result in a sentence rather than in the required `FINAL:` format.
- **A genuine problem solving the calculation.** The model might misunderstand the question or make a mathematical mistake.

I also considered that some empty saved responses might involve response content that my original script did not record clearly.

The original script kept the text but did **not** save the API's *stop reason* (why generation ended) or the number of output tokens used. That meant I could not retrospectively identify all of the causes from the first dataset alone.

### Why I changed the second run

I wanted to investigate the most obvious technical limitation **without rewriting the financial questions or making them easier**. Increasing the output allowance gave the model more room to finish, while recording completion information would help explain any remaining failures. I kept both the old results and the old script rather than replacing them.

The idea that token limits might be contributing to `NO_ANSWER` arose **after** the first run. It was a diagnostic explanation to test, not a hypothesis I had registered before collecting results.

## 8. Experiment 2: the changes and results

I ran the same **150 task identities** again: the same two model IDs, five financial problems, five wordings, three repetitions, independent calculations, tolerances, and required final-answer format.

I made two main changes:

1. **Increased the response limit from 1,000 to 3,000 output tokens.** This gave longer calculations more space to finish.
2. **Saved more diagnostic information.** The revised program recorded the stop reason, input and output token counts, response content types, and a reason when no valid final answer was extracted.

### 8.1. Results of the second real run

| Model | Total requests | `MATCH` | `NO_ANSWER` | `BREAK`, `ANCHORED`, or API `ERROR` | Correct and readable response rate |
|---|---:|---:|---:|---:|---:|
| Haiku 5.5 | 75 | 75 | 0 | 0 | 100% |
| Sonnet 5.5 | 75 | 75 | 0 | 0 | 100% |
| **Both** | **150** | **150** | **0** | **0** | **100%** |

All 150 recorded stop reasons were **`end_turn`**, meaning the API reported a normal end to the model's response rather than a response cut off at its token limit. **Nineteen** second-run responses used more than **1,000** output tokens. This is direct evidence that the extra allowance was used in some successful responses.

The recorded token count includes all output usage reported by the API. In this second run, some responses included non-text thinking content, so output tokens should not be interpreted as a count of words visible in the saved response.

### 8.2. Comparing the same questions across runs

I matched the records using the model, financial calculation, question style, and repetition number. This produced 150 pairs of matching tasks.

- All **19** tasks that received `NO_ANSWER` in the first run received `MATCH` in the second run.
- In **11** of those 19 corresponding second-run responses, the model used **more than 1,000 output tokens**.
- In the remaining **eight**, the second-run response used **1,000 tokens or fewer**.

Those 11 longer responses support the possibility that the original output limit was too low for some completions. The other eight show why the new limit cannot fully explain every individual change. The models generated new responses in the second run; these were not exact continuations of the first-run responses.

### 8.3. The headline change, and its limits

The correct and readable response rate rose from **87.3% to 100%**, an improvement of **12.7 percentage points**. That is 19 more successful results out of the same number of requests. Haiku rose from 80% to 100%; Sonnet rose from about 94.7% to 100%.

The comparison shows what happened in two executions. It does not prove what caused the difference. The higher token allowance is a plausible contributor, but I did not randomly assign otherwise identical requests to different token limits at the same time. Normal response variation or other time-dependent factors could also matter.

## 9. What I planned to investigate if the problem continued

The second run succeeded, so the additional checks below were not performed. This is the **follow-up plan I identified after reviewing the first run**. It should not be described as a formally pre-registered plan or as work already performed.

1. **Check why each response stopped.** If the API reported a token-limit stop, that would support the output-budget explanation. A normal `end_turn` with no valid answer would point elsewhere.
2. **Look at the complete response, not just the extracted number.** For empty saved text, check whether the API returned other content types or whether the script failed to capture the content.
3. **Test the number-reading logic separately.** Have a second parser inspect saved responses and manually review disagreements. Keep the original strict scores unchanged and report the more flexible reading as a separate measure.
4. **Test several response limits side by side.** Repeat the same questions with limits of **1,000, 2,000, and 3,000 tokens**, ideally interleaving the settings and repeating requests. This would be a stronger way to isolate the effect of response length.
5. **Try different answer instructions in new experiments.** For example, test a concise number-only response or explicitly ask the model to check a misleading hint. These **number-only and pushback modes were not included in the two completed runs**.
6. **Make difficult examples harder in a controlled way.** Add mortgages and bond calculations with more varied numbers and rounding, then test stronger misleading hints. Do this only after ensuring the measurement program is reliable.
7. **Improve the audit trail.** Save SDK versions, timestamps, request identifiers when available, generation settings, raw outputs, and diagnostic fields to make every run easier to reproduce and investigate.

The order matters: **first verify the measuring tool, then make the model test more difficult**. Changing many things at once would make the source of any improvement harder to identify.

## 10. Conclusions, limitations, and what I learned

I started this project to see whether two AI models would calculate the same financial answer when I changed the wording of a question. In the first run, 131 of 150 responses produced a correct number in the required `FINAL:` format. Another 19 were marked `NO_ANSWER`. When I read those responses, I found that at least six contained the right number but did not follow the requested format. That was an important distinction. My program could reject an answer even when the calculation itself was correct.

I suspected that the 1,000-token response limit might prevent some answers from being completed. For the second run, I raised the limit to 3,000 tokens and saved information about how each response ended. All 150 responses then matched the independently calculated answers and followed the required format. Of the 19 tasks that had failed the first time, 11 used more than 1,000 output tokens in the second run. This supports my suspicion that response length contributed to some missing answers, but it does not prove that it explains all 19. The second run also generated new responses at a different time.

The study has clear limits. I used five financial problems, five phrasings per problem, and three repetitions per model, with hand-written questions and only one misleading hint per calculation. I did not run a controlled test that varied only the token limit, and I did not save enough completion information in the first run to identify the cause of every missing answer. The results have not been independently replicated. They show that both models performed well on these particular questions under the revised conditions, not that either model is always accurate.

My main lesson was to investigate the testing process before treating a missing result as a model failure. In future work, I would record completion details from the start and measure numerical correctness separately from response formatting. I would also test different token limits under more controlled conditions. The unexpected weakness in my own evaluation process became one of the most useful findings of the project.

## 11. Data and reproducibility

The project includes the original source code and actual output files for **both completed API runs**, along with a program that recalculates the result totals. The real results are stored under `experiment_01_initial/actual_run/` and `experiment_02_diagnostic/actual_run/`. Generated practice or dry-run files are not treated as research evidence.

I kept the original result summaries, a comparison dataset that places matching tasks side by side, and file checksums to check that the evidence has not changed. No API key is included. Re-running the experiment requires access to the models and may produce different responses because deployed AI systems are not guaranteed to behave identically over time.

**Evidence note.** Experiment 1's real-run `results.csv` has 14 columns. Experiment 2's has 19, including additional completion diagnostics. The original real-run files have been preserved rather than edited to force agreement between runs. The retrospective manual review of the 19 first-run exceptions is separate from the original recorded `NO_ANSWER` classifications. The numerical improvement reported in this paper is an observed before-and-after difference, **not a proven causal estimate** of the effect of increasing `max_tokens`.

## Appendix A. Quick glossary

| Term | Plain-English meaning |
|---|---|
| **API** | A way for one program to send a question to another service and receive its answer |
| **Language model** | The AI system responding to the questions |
| **Reference answer** | The answer calculated independently, used to check the model |
| **Tolerance** | A small allowed difference for rounding |
| **Parser** | Code that reads the response and extracts the final number |
| **Output token** | A unit of generated text, not exactly a word |
| **Stop reason** | Information from the API about why a response ended |
| **`end_turn`** | The API's indication that the model ended its response normally |
| **Dry run** | A practice execution with simulated responses, not real research observations |
| **Exploratory research** | Research intended to investigate patterns and develop questions rather than prove a predefined explanation |

