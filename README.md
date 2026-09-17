# Assignment 1 — Evaluation and flexibility

**IDS 575: Machine Learning and Statistical Methods for Business Analytics · Fall 2026**
Released Thursday, September 3 · **Due Thursday, October 1, 6:00 PM Central** · 10% of course grade

Covers Handouts 1–3: supervised learning and loss, training versus test error, cross-validation, choosing a split that matches deployment, logistic regression, model flexibility, bias and variance, and regularization.

**Expected effort: 6–8 focused hours.** Part A is the larger of the two parts.

Two independent cases, one memo.

- **Part A — Northline Fitness.** Build an evaluation for a churn model that reflects how the model would actually be used, and turn its predictions into a targeting decision priced in dollars. Uses Handouts 1–2.
- **Part B — Cascade Outdoor.** Measure how much of the forecast error in two retail divisions is unavoidable, compare four models against that floor, and say what a company-wide modelling standard should specify. Uses Handout 3.

Part A can be started the day the assignment is released. Part B needs Handout 3, covered in Lecture 4; you will have at least two weeks after that. Midterm 1 on September 24 covers Lectures 1–4, so this assignment is direct preparation for it, and the deadline falls a week after the exam.

---

# Part A — Northline Fitness

## The situation

Northline Fitness sells a subscription fitness app. Members pay monthly on one of three plans. About 9% of active members cancel in any 60-day window.

The retention team wants to run a monthly program: score every active member for the probability they cancel within 60 days, and send the highest-scoring members a **retention offer** — one month at 50% off plus a personal check-in.

Finance has priced it:

| Quantity | Value |
|---|---|
| Cost of extending one offer | **$18** |
| Lifetime value of a member who stays | **$240** |
| Fraction of would-be churners retained by the offer | **0.35** |
| Effect on a member who was not going to churn | none; the $18 is still spent |

So an offer to a member who would have churned is worth `240 × 0.35 - 18 = $66`. An offer to a member who would not have churned costs `$18`. No offer is worth `$0`.

A junior analyst has already pulled 24 months of history and fitted a first model: logistic regression on all available columns, 5-fold cross-validation, encoders and scalers fitted inside the folds. It reports **0.967 AUC**. The code is in `part1_northline/starter/analyst_model.py` and runs as-is.

The VP of Membership wants a second opinion before this goes to the operating committee. **Your job is to produce the estimate she can plan against, and a recommendation.**

## How the model would be deployed

If approved, the program runs monthly from **April 2026**, scoring the active book at the start of each month. Two things about that book differ from the history you have:

1. **Corporate members.** Northline signed three employer wellness contracts starting February 2025. The `corporate` channel is 0% of the book in 2024, about 20% by December 2025, and Membership Analytics forecasts **roughly 35% of the April–June 2026 book**.
2. **A competitor** launched a rival app in July 2025 and is still spending heavily.

## What you need to know about the data

All of this is also in `part1_northline/data/DATA_DICTIONARY.md`. None of it is hidden; the work is in handling it correctly, not in finding it.

- **Grain.** One row per member per calendar month. A member appears in many rows. The 4,200 members produce 33,340 rows.
- **Timing.** The dictionary states, for every column, the window over which it is measured. Some columns are recorded **after** the month being scored, and so would not exist at the moment the April 2026 model has to produce a score. Use the timing notes to decide which columns are admissible; keeping a column is a decision you should be able to justify just as much as dropping one.
- **Duplicated rows (ticket NLF-2231).** The March 2025 load was re-run after a partition failure and appended instead of replacing. Every affected row appears twice, identical on every column. Remove the duplicates before modelling.
- **Date formats (ticket NLF-2198).** `snapshot_month` appears in three formats. `load.py` provides `month_key()` to normalise them.

## A1 — Baselines (before any modelling)

Report, in one small table:

1. The base rate of `churn_next_60d`.
2. The accuracy of predicting "no churn" for everyone, and one sentence on whether accuracy is the right metric for this decision.
3. AUC for one single-variable rule — for example, ranking members by `days_since_last_login`.
4. The analyst's headline AUC (0.967) beside them.

Then, in one short paragraph: what would have to be true about this dataset for 0.967 to be a good estimate of performance on the April 2026 book?

## A2 — Build an evaluation that matches deployment

Make the following four changes to the analyst's protocol, **one at a time, in an order you choose**, and record the AUC after each. Report it as a table.

Until you have made change 3 the number is cross-validated on the building data; from change 3 onward it is measured on the test window defined below. Say in the table which kind each row is.

| Change | What it means |
|---|---|
| **1. Admissible columns only** | Keep only columns that exist at the moment of scoring, per the timing notes in the dictionary. |
| **2. One member, not many rows** | A member contributes many rows. Make sure a member never appears in both the fitting data and the held-out data. |
| **3. Past to future** | Fit on earlier months and evaluate on later ones, rather than on a random shuffle of all months. |
| **4. Report by segment** | Report the final number separately for `corporate` members and for everyone else. |

**One of these four changes will move the number a great deal, and at least one will move it barely at all.** That is expected. A change can be the right thing to do and still be worth almost nothing on a particular dataset, and reporting a near-zero effect correctly earns the same marks as reporting a large one. Do not go looking for a bug because a number did not move.

For each row of the table, write one sentence on what the number means. Then, in two or three sentences:

- Why you chose that order.
- Whether the changes between rows can be read as "problem X cost this much AUC." (They cannot be read that way independently of the order; say why, in your own words.)

**Use these evaluation windows** for the final protocol, so that everyone's numbers are comparable:

| Window | Months | Purpose |
|---|---|---|
| Training | 2024-01 → 2025-06 | Fit the model |
| Not used | 2025-07, 2025-08 | Labels for June 2025 do not mature until end of August 2025 |
| Validation | 2025-09 | Any choice made by looking at data |
| Test | 2025-10 → 2025-12 | Final estimate; score once |

Explain in one sentence why the two-month gap is there.

## A3 — The targeting decision

Using the final protocol from A2:

1. Report test-period AUC overall, for corporate members, and for everyone else, each with row counts and churner counts.
2. **Derive the cost-based threshold** from the finance figures in the table above. Write down what an offer is worth to a member who would have churned and to one who would not, take the expectation at predicted probability `p`, and find the value of `p` above which making the offer is worth more than not making it. Show the working and state the threshold. Handout R1 §3 covers the general form; derive it here rather than quoting it, since you will be asked to on the midterm.
3. Report the realised dollar value of the program on the test period at that threshold, and compare it with offering to every member.
4. **State your recommendation** to the VP. If it is conditional, state the condition so that someone at Northline could check whether it holds — for example, in terms of a share of the book or a measured AUC.

---

# Part B — Cascade Outdoor

## The situation

Cascade Outdoor is a specialty retailer with two merchandising divisions: **Hardgoods** (tents, packs, stoves) and **Apparel** (jackets, base layers). Both forecast weekly units per store to drive buying and markdown decisions. Both run on the same planning system and record the same twelve fields.

They differ in size. Apparel migrated to the new platform in March and its pre-migration history is not comparable, so it was dropped. **Hardgoods has about 3,000 usable store-weeks; Apparel has 197.**

A contractor fitted ordinary least squares to each division twice — once on the twelve fields (degree 1, twelve terms) and once on a degree-2 polynomial basis (every square and pairwise product, ninety terms) — and scored both by 5-fold cross-validated MSE:

| | degree 1 | degree 2 |
|---|---:|---:|
| Hardgoods | 336 | **231** |
| Apparel | **414** | 618 |

He drew two conclusions: that the divisions need **different models**, since a different specification wins in each; and that **Apparel demand is inherently harder to forecast**, since its best error of 414 is nearly double Hardgoods' 231.

The VP of Merchandising Planning wants **one modelling standard** company-wide, and has asked you whether that is possible and what it should say.

## What Part B asks

1. How much of the error in each division is unavoidable?
2. What does a penalty buy, and why is the answer different in a division with 3,000 rows than in one with 197?
3. Should Cascade standardise a model, or a process?

There are no marks for a better model than the four specified below.

## What you need to know about the data

Also in `part2_cascade/data/DATA_DICTIONARY.md`.

- **`replicates.csv`** is a controlled exercise: 45 store-week configurations per division, each observed **ten times** with identical values on all twelve recorded fields. None of these rows appear in the training extracts. You use it for two things: estimating the noise floor, and scoring your final models once.
- **Duplicated rows (ticket CO-4471).** The Hardgoods load was re-run and appended rather than replaced, so affected store-weeks appear twice. `dedup_h()` in `load.py` removes them. Use it for everything in Part B.
- **Apparel cleaning.** Three Apparel weeks were removed before delivery (a store closure, a keying error, and Black Friday). The dictionary records the reasoning; you do not need to revisit it.

## The protocol — use exactly this

`part2_cascade/starter/load.py` provides all of it.

| Step | What to do |
|---|---|
| **Tune** | 5-fold CV on the division's own training extract, using `make_folds()`. Fit preprocessing inside each fold — `poly_pipeline(estimator, degree=d)` does this. |
| **Refit** | Refit each tuned configuration on all rows of that division's training extract. |
| **Test** | Score once on `test_extract("H")` or `test_extract("A")`. Nothing is selected by looking at these rows. |
| **Report** | Test MSE, and **test MSE − σ̂²** — the part of the error a better model could in principle remove. |

Standardising before penalising is not optional; `poly_pipeline()` handles it. Handout 3 §5.2 explains why.

## B1 — The noise floor

Each group of ten rows in `replicates.csv` is identical on every recorded field, so the variation within a group is what no model could have predicted. Estimate σ² for each division as the pooled within-configuration variance:

$$\hat{\sigma}^2 = \frac{\sum_g \sum_r (y_{gr} - \bar{y}_g)^2}{\sum_g (m_g - 1)}$$

Report both estimates with their approximate standard error, $\hat{\sigma}^2\sqrt{2/\text{dof}}$, where the degrees of freedom are the denominator of $\hat{\sigma}^2$ above:

$$\text{dof} \;=\; \sum_g (m_g - 1),$$

that is, one fewer than the group size, summed over groups. With 45 configurations of 10 replicates in a division, $\text{dof} = 45 \times 9 = 405$.

Then, in one or two sentences: what do the two floors say about the contractor's claim that Apparel demand is inherently harder to forecast?

## B2 — Four models, compared against the floor

Two degrees crossed with two treatments, in both divisions:

| Model | How to fit it | Tuning |
|---|---|---|
| Degree-1 OLS | `poly_pipeline(LinearRegression(), degree=1)` | none |
| Degree-1 ridge | `poly_pipeline(Ridge(), degree=1)` | `ALPHA_GRID`, 5-fold CV |
| Degree-2 OLS | `poly_pipeline(LinearRegression(), degree=2)` | none |
| Degree-2 ridge | `poly_pipeline(Ridge(), degree=2)` | `ALPHA_GRID`, 5-fold CV |

For each of the eight cells report: the tuned penalty where there is one, CV MSE with its standard error across folds, test MSE, and test MSE − σ̂².

Then answer, in two or three sentences each, citing numbers from your own table:

1. **Where does the penalty change the answer, and where does it not?** Compare the CV MSE with and without a penalty in all four cells. Say what distinguishes the cell where it matters most. (Note that degree-1 Apparel is also a small sample, so "Apparel is small" is not the full explanation — the useful quantity is the number of terms relative to the number of rows.)
2. **Is a single company-wide specification possible?** The contractor compared unpenalised fits only. Once each specification is allowed a tuned penalty, is there one choice that is at least as good as the best hand-picked choice in *both* divisions? Note where the one-standard-error rule (Handout 1 §6.5) bears on your answer.
3. **How firm is the Apparel ordering?** Put the Apparel CV standard errors next to the Hardgoods ones and say which differences in Apparel are large relative to their uncertainty and which are not.

## B3 — One stability experiment

`part2_cascade/starter/stability.py` contains the loop; fill in the four models and interpret the output. Everything else is fixed: **20 bootstrap resamples** from `bootstrap_indices()`, **three query configurations** per division from `QUERY_CONFIGS`, and penalties **held at the B2 values** (do not re-tune inside the resamples).

Each query configuration also appears in `replicates.csv`, so the mean of its ten replicates estimates the true mean demand there to within about σ/√10 ≈ 4 units. That is what lets you see bias and variance separately rather than only their sum.

For each division and model, report at each query point:

- the **standard deviation** of the 20 predictions (variance), and
- the **difference between their mean and the replicate-based estimate of the truth** (bias).

Report the average of each across the three points, plus one figure.

Then, in one sentence each, backed by a number from your table:

1. What raising the degree from 1 to 2 did to bias and to variance, in each division.
2. What the penalty did to each, at each degree.
3. Why the same four procedures give different answers in the two divisions. Name the quantity that differs and connect it to B2.

If one of these effects is nearly zero, say so and give the number.

**Optional, no marks, about two minutes.** `part2_cascade/starter/sweep.py` plots training and cross-validated error against the number of terms in the basis, and cross-validated error against the ridge penalty, for both divisions. Running it is the fastest way to see the curves in Handout 3 §1.4, and Midterm 1 will ask you to read a plot like them.

---

## Deliverables

Full format in `../00_start_here/04_submission_checklist.md`. One submission, one grade.

1. **`memo.pdf`** (or `.md`) — two sections in one document, each leading with its recommendation:
   - **§1 to the VP of Membership, Northline Fitness** — max 2 pages of prose, plus Exhibits A1–A3.
   - **§2 to the VP of Merchandising Planning, Cascade Outdoor** — max 1 page of prose, plus Exhibits B1–B3. Answer the three Part B questions, and say what a company-wide standard should fix and what it should leave to the data, in terms someone could apply to a third division acquired next year.

   Exhibits do not count against the prose limits.
2. **`analysis/`** — your code, runnable end to end with one command, plus a `README` saying what to run. `analysis/part1/` and `analysis/part2/` is fine; one command must still produce everything.
3. **`ai_process_note.md`** — max 1 page, covering both parts: what you delegated, what you changed or rejected and why, and how you checked the numbers.
4. **`sessions/`** — complete exported history of every AI session used.

---

## What is in this folder

```
part1_northline/data/member_months.csv      the extract
part1_northline/data/DATA_DICTIONARY.md     read this first
part1_northline/starter/analyst_model.py    the analyst's pipeline, runnable
part1_northline/starter/load.py             loader, month_key(), economics constants

part2_cascade/data/division_h.csv           Hardgoods store-weeks
part2_cascade/data/division_a.csv           Apparel store-weeks
part2_cascade/data/replicates.csv           repeat-observation extract; also the test set
part2_cascade/data/DATA_DICTIONARY.md       read this first
part2_cascade/starter/load.py               loaders, dedup_h(), folds, pipelines, grids, queries
part2_cascade/starter/stability.py          the B3 bootstrap loop, models left to you
part2_cascade/starter/sweep.py              optional degree and penalty sweeps, complete

rubric.md                                   how this is graded
assignment1.pdf                             this brief, the dictionaries and the rubric
```

### Elsewhere in the course repository

| Path | What it is |
|---|---|
| `assignments/00_start_here/01_how_to_approach_assignments.md` | Read before you begin. Short. |
| `assignments/00_start_here/02_ai_coding_agent_policy.md` | What you may delegate, and which agents are approved |
| `assignments/00_start_here/03_exporting_your_session_history.md` | How to produce `sessions/` |
| `assignments/00_start_here/04_submission_checklist.md` | Submission format |
| `handouts/lecture01_learning_from_data.pdf` … `lecture03_bias_variance.pdf` | Handouts 1–3 |
| `handouts/handoutR1_reading_a_metric.pdf` | Handout R1 — every metric used here, with worked examples |

## Where the concepts are

| For | Read |
|---|---|
| Loss as a business statement | Handout 1, §4.4 |
| Risk, empirical risk, why training error is not evidence | Handout 1, §5 |
| Cross-validation, what it estimates, its standard error | Handout 1, §6 |
| The one-standard-error rule | Handout 1, §6.5 |
| Leakage and the test that catches it | Handout 1, §7.2 |
| Splits that match deployment; grouped and temporal folds; reporting by segment | Handout 1, §7.3–7.4 |
| Logistic regression; reading a coefficient as an odds ratio | Handout 2, §7.2 |
| The flexibility dial; why the cross-validated minimum is interior | Handout 3, §1 and §4 |
| Irreducible error as a floor | Handout 3, §3.3 |
| The bias–variance decomposition | Handout 3, §3 |
| Ridge; what a penalty buys and costs; why you standardise first | Handout 3, §5.2 |

**Metrics — accuracy, precision, recall, ROC, AUC, R², RMSE, calibration — are in Handout R1, *Reading a Metric*.** Look a metric up when you need it rather than reading it front to back. The parts this assignment uses:

| For | Read |
|---|---|
| Accuracy, and why a 9% base rate makes it a poor headline | Handout R1, §4.2 |
| Confusion matrix; precision and recall | Handout R1, §4.1, §4.3 |
| ROC and AUC | Handout R1, §4.5 |
| Turning a probability into a send / don't-send decision from costs | Handout R1, §3 — the general form; A3 asks you to derive it |
| R², RMSE, MAE; error measured against a floor | Handout R1, §2 |

## Ground rules

- **Score each test set once.** Northline's test period and Cascade's replicate extract are used at the end and select nothing.
- **State every Part B error against the floor.** A raw MSE has no interpretation on its own.
- **Every number in the memo must be reproducible** from your submitted code, with one command.

## Two practical habits

**Do not let your agent read a CSV into the conversation.** `member_months.csv` is 33,000 rows; pasting it can cost more in one message than a whole working session should. Have the agent write code that reads the file and reports numbers back. The data dictionaries are short and are meant to be read.

**Start a fresh session for each work block** — the audit table, then the threshold, then Part B — rather than one session running all month. It keeps costs down and makes your transcripts easier to export and read. `../00_start_here/05_setting_up_your_agent.md` has the rest.
