# Memo

**From:** Orcun Tasdemir
**Date:** 1 October 2026
**Re:** §1 Northline Fitness retention targeting · §2 Cascade Outdoor forecasting standard

Every figure in this memo is reproduced by `bash analysis/run.sh`; the output
file behind each one is named in the exhibits.

---

# §1 — To the VP of Membership, Northline Fitness

## Recommendation

**Run the retention programme on non-corporate members only, and instrument it
so it can be stopped.** On the most recent quarter it would have returned
**$852**, not the $19,774 per quarter in the proposal before you. Excluding
corporate raises that to **$930**: corporate offers reached a member who was
going to cancel 11% of the time against the 21.4% needed to break even, and
corporate is forecast to grow from 19% of the book to 35%. Bring it back in
when it has enough history to fit on — the model that would score April saw 533
corporate member-months, none older than six months. Then measure **realised
value per offer** on matured 60-day outcomes each quarter and suspend the
programme if it turns negative, which is the same as the share of offers
reaching a churner falling below 21.4%.

## The headline answers the wrong question

The pipeline itself is careful — encoder and scaler are fitted inside each
fold, so there is no preprocessing leak. What is wrong sits above the
modelling, in what the evaluation was asked to estimate. Exhibit A2 makes four
corrections one at a time, so each is attributable to one cause.

**Two of the fourteen columns do not exist when a score must be produced.** The
programme scores the book at the *start* of each month. `winback_offer_sent`
records a contact worked from a list circulated on the third business day
*after* month close; `exit_survey_started` records a member opening the
cancellation survey, which is a step in cancelling. In the historical file both
are filled in — the exit-survey flag is 1 on 1,810 rows and **every one is a
cancellation**, with no exceptions in 31,645 rows. On 1 April both will be 0
for everyone, including the members who go on to leave. Removing them costs
0.22 AUC. Exhibit A2b argues all fourteen columns from the dictionary's timing
notes, kept and dropped alike.

**Keeping a member wholly on one side of the split costs 0.001**, though 2,899
of 3,648 members straddled folds beforehand — no admissible column identifies a
member, and a linear model cannot build identity from shared attributes.
**Fitting on the past and scoring the future costs a further 0.10**; what
changes at that row is not that the data is unseen, which it already was, but
that it is *later*. The two-month gap exists because a June 2025 label is not
settled until 31 August, so training on June while evaluating in July would use
outcomes from the period being evaluated. It also mirrors deployment: on 1
April the two most recent months of labels will not exist either.

**These differences are not a decomposition.** Each is measured on top of those
above it, so they sum to the total but the split depends on the order. Had
past-to-future come first with the two post-hoc columns still in, the test AUC
would have stayed near 0.97, time would have looked free, and dropping the
columns afterwards would have carried the whole fall.

Exhibit A1 sets the scale. Predicting "no churn" for everyone is 90.7% accurate
and identifies nobody; the same rule scores 0.50 on the ranking scale, so 90.7%
and 0.967 are not neighbouring numbers. Accuracy is the wrong yardstick twice
over — the outcome is rare, and a wasted offer costs $18 against $66 forgone on
a missed churner, so counting both as one mistake prices them wrongly.

## From a probability to a decision

An offer to a member who would have cancelled is worth 240 × 0.35 − 18 = **$66**;
to one who would not, it costs **$18**; no offer is worth $0. So at predicted
probability *p* the expected value of offering is

> 66*p* − 18(1 − *p*) = **84*p* − 18**

which beats not offering exactly when **p > 18/84 = 0.2143**. That comes from
your finance figures alone, and was fixed before any test-period score was
read. The analyst's 0.267 was instead found by searching 400 cut-points for the
one that maximised measured value — choosing by looking at the answer. It made
little difference: on honest scores it returns $828 against our $852. The
$19,774 was never a threshold error.

0.2143 is also the **break-even precision**, since value per offer is exactly
84 × (precision − 0.2143). Against a 9% base rate that means finding members at
roughly two and a half times average risk; the model manages 25.6% in the top
5% of the book, clearing the bar by four percentage points.

## What it is worth, and how firmly

$852 on the quarter, against **−$47,736** for offering to every member-month
and $0 for doing nothing: targeting is what makes the programme viable at all.
But the total carries a standard error of about **$572** — a sum of 242 draws
of +$66 or −$18 — so it sits 1.5 standard errors above zero, and month to month
it straddles the line: November +$810, October +$48, December −$6.

Corporate is the clearest part of the picture: ranked at 0.404, below a coin
flip, with nine offers reaching a churner once. The model's largest single term
is the channel itself, roughly four times the churn odds for any non-corporate
channel — it has learned that corporate members rarely cancel, not which of
them will. That is reasonable to learn from 533 rows none older than six
months, and a poor basis for spending on a third of next spring's book.

Two things make $852 optimistic for April: the test quarter ran 8.4–9.5% churn
where April–June 2025 ran 5.3–7.1%, and 1,294 members already received a
retention contact, so part of what we fitted to is post-treatment. The
threshold also assumes the probabilities mean what they say. They roughly do —
checked on September 2025 and corrected there before use — but the model still
overstates the members it picks, claiming 39.6% for its top-scoring offers and
delivering 27.9%. Hence a dollar tripwire rather than a ranking statistic,
which can hold steady while the probabilities drift.

---

## Exhibit A1 — Baselines, before any modelling

Source: `analysis/outputs/a1_baselines.csv`, `a1_cleaning.txt`. All rows
deduplicated: the extract contains 1,695 exact duplicate rows, all in March
2025 (ticket NLF-2231), removed before every figure below except the
analyst's, which is reported as his script prints it on the raw file.

| Quantity | Value | Basis |
|---|---:|---|
| Base rate of `churn_next_60d` | **9.29%** | 2,939 of 31,645 member-months |
| *Context:* members cancelling at some point in the window | 70.0% | 2,939 of 4,200 members; a different unit |
| Accuracy of predicting "no churn" for everyone | **90.71%** | = 1 − base rate; uses no information |
| AUC of that same rule | **0.50** | every member scored alike, so no ranking |
| AUC, rank by `avg_session_minutes` (shorter → churn) | **0.681** | one column, no fitting |
| AUC, rank by `app_opens_last_30d` (fewer → churn) | 0.648 | " |
| AUC, rank by `days_since_last_login` (longer → churn) | 0.646 | " |
| AUC, rank by `tenure_months` (shorter → churn) | 0.502 | " |
| **Analyst's 5-fold cross-validated AUC, 14 columns** | **0.967** | raw 33,340 rows, randomly shuffled folds |

Tenure's 0.50 is not an artefact of a non-monotone relationship: churn sits
between 6.7% and 10.1% in every tenure bucket from month 0 to 24+
(`a1_churn_by_tenure.csv`).

## Exhibit A2 — Four changes to the evaluation, one at a time

Source: `analysis/outputs/a2_table.csv`. Changes are cumulative. Rows 0–2 are
5-fold cross-validated on the building window (Jan 2024 – Jun 2025: 21,031
rows, 1,767 cancellations, 3,648 members). Rows 3–4 are the test window
(Oct – Dec 2025), scored once. The validation month (Sep 2025) is not used
here: no choice in this section was made by looking at data.

| Row | Change | Scored | Churners | AUC | Kind | What it means |
|---|---|---:|---:|---:|---|---|
| — | Analyst's script as printed: raw file, 24 months, 14 columns, random folds | 33,340 | | 0.967 | cross-validated | The figure in the proposal |
| 0 | Same protocol, deduplicated, building window only | 21,031 | 1,767 | **0.968** | cross-validated | Deduplication and the shorter window change nothing; the leak dominates |
| 1 | + admissible columns only (12 of 14, Exhibit A2b) | 21,031 | 1,767 | **0.748** | cross-validated | 0.22 of the headline was information recorded by the cancellation itself |
| 2 | + a member never in both the fitting and held-out folds | 21,031 | 1,767 | **0.747** | cross-validated | Worth 0.001 here: no admissible column identifies a member |
| 3 | + past to future: fit Jan 2024 – Jun 2025, score Oct – Dec 2025 | 4,556 | 408 | **0.644** | test window | 0.10 is the cost of time; rows 0–2 were already on unseen rows |
| 4 | corporate members | 860 | 34 | **0.404** | test window | Below a coin flip on the segment about to triple its share |
| 4 | everyone else | 3,696 | 374 | **0.641** | test window | Which is also the pooled figure: corporate is 19% of rows, 8% of churners |

Re-running the analyst's exact protocol on the raw file in our harness
reproduces 0.967, confirming the comparison is like-for-like (`run.log`).

### Exhibit A2b — Which columns exist at the moment of scoring

Source: `analysis/outputs/a2_columns.csv`. The scoring moment is the **start**
of `snapshot_month`. Decided from the data dictionary's timing note for each
column, for columns kept as well as dropped.

| Decision | Columns | Timing note that decides it |
|---|---|---|
| **Kept (12)** | `tenure_months` | "as of the start of `snapshot_month`" — explicitly at the scoring moment |
| | `sessions_last_30d`, `app_opens_last_30d`, `avg_session_minutes`, `days_since_last_login`, `support_tickets_last_30d`, `referrals_made` | 30 days ending on the last day of the **previous** month: the window closes before the month starts |
| | `payment_failures_last_90d` | 90 days ending on the last day of the previous month |
| | `acquisition_channel`, `city_tier` | fixed at signup |
| | `plan_tier`, `monthly_price` | billing, no timing note stated. Read as the plan on the billing snapshot at the start of the month. A mid-month change would not be visible, which the dictionary does not rule out. This is the one reading rather than a fact. |
| **Dropped (2)** | `winback_offer_sent` | contact "about this month", worked from a list circulated on the third business day **after** month close. 1 on 3,533 rows, 2,239 of them cancellations |
| | `exit_survey_started` | the cancellation flow itself; no window stated. 1 on 1,810 rows, **every one a cancellation**, none a non-churner |
| **Not features (3)** | `member_id`, `snapshot_month`, `signup_month` | identifier; the month itself (April 2026 is a value never seen in training); redundant with tenure |

## Exhibit A3 — The targeting decision

Source: `analysis/outputs/a3_value.csv`, `a3_threshold.txt`, `a3_by_month.csv`,
`a3_offer_quality.csv`. Test window Oct – Dec 2025. One offer = one
member-month, matching a programme that scores the book monthly.

**(a) Realised value at the cost-derived threshold t\* = 0.2143**

| Policy | Offers | Reached a churner | Wasted | Value |
|---|---:|---:|---:|---:|
| **Targeted at t\* = 0.2143** | 242 | 62 | 180 | **+$852** |
| — corporate | 9 | 1 | 8 | **−$78** |
| — everyone else | 233 | 61 | 172 | **+$930** |
| Offer to every member-month | 4,556 | 408 | 4,148 | **−$47,736** |
| No programme | 0 | — | — | $0 |
| *Memo: at the analyst's grid-searched 0.267* | 108 | 33 | 75 | +$828 |

Standard error of the quarter's total: **$572** (242 draws of +$66 or −$18).
Contacting each member at most once in the quarter gives 195 offers worth $774;
47 of the 242 are repeat contacts, and they earn $1.66 each against $3.97 for
first contacts.

**(b) Month by month at the same fixed threshold**

| Month | Offers | Precision | Break-even | Value | Per offer |
|---|---:|---:|---:|---:|---:|
| Oct 2025 | 114 | 21.9% | 21.4% | +$48 | $0.42 |
| Nov 2025 | 81 | 33.3% | 21.4% | +$810 | $10.00 |
| Dec 2025 | 47 | 21.3% | 21.4% | −$6 | −$0.13 |

**(c) Figure — realised value across all thresholds:** `a3_value_curve.png`.
The threshold was fixed from the finance table before any score was read; the
curve is shown for sensitivity, not for selection. It peaks at $1,098 at a
threshold of 0.236, so not selecting on the test period cost $264.

---

# §2 — To the VP of Merchandising Planning, Cascade Outdoor

## Recommendation

**Standardise the process, not the model.** Every division should estimate its
own noise floor from repeat observations, tune flexibility and penalty by
cross-validation on its own rows, report standard errors and break ties with
the one-standard-error rule, then score once on held-out data that selects
nothing. Applied this year that process yields the *same* specification in both
divisions — degree-2 ridge — no worse than the best hand-picked choice in
Hardgoods (0.15 ± 0.22) and better by 84 ± 20 in Apparel. So one specification
does serve both; the contractor's contrary conclusion came from comparing
unpenalised fits only.

**How much of the error is unavoidable.** The same amount in both — 148 units²
in Hardgoods, 142 in Apparel, 0.4 standard errors apart — so Apparel demand is
**not** inherently harder to forecast. What differs is how much is recoverable:
83 units² above the floor against 272. His arithmetic was sound (Exhibit B2);
his conclusions were not.

**What a penalty buys, and why that differs.** In one cell of four, and
overwhelmingly: Apparel at degree 2, where it takes cross-validated error from
618 to 330, a drop of 288 against a standard error of 55. Elsewhere it does
nothing measurable — 0.01, 0.15 and 1.47, each smaller than its own standard
error. The separator is not division size but **terms estimated per row: 0.46
where it matters, against 0.004, 0.030 and 0.061 where it does not.** Apparel at
degree 1 proves it: the same 197 rows, twelve terms, no gain.

**How firm the Apparel ordering is.** Not uniformly: its standard errors run 14
to 68 against Hardgoods' 4.6 to 6.4. Firm — degree-2 ridge beats both degree-1
cells by 82 to 84 (SEs 20 to 26), and unpenalised degree 2 is worst by 204 ± 53.
Not firm — whether to penalise at degree 1, at 1.47 ± 7.26.

## Stability, and a third division

Raising the degree is a good trade in Hardgoods — prediction spread rises from
1.14 units to 2.83 while distance from the truth falls from 12.65 to 3.84 — and
a pure loss in Apparel, where spread rises nearly six-fold to 25.24 with no
improvement in distance from the truth. The penalty does nothing at degree 1 in
either division or at degree 2 in Hardgoods (2.83 → 2.80), and cuts Apparel's
degree-2 spread by 71%, to 7.22. Both track the same terms-to-rows ratio, 0.03
against 0.46 — which is why the standard fixes a method, not a specification. A
division acquired next year with 400 rows would sit at 0.225 on the same basis,
between these two, and could legitimately land on a different answer.

What no standard can supply is history. Apparel's best model is **85% bias** —
293 units² against 53 of variance — while Hardgoods on the same specification
selects a penalty ten times smaller. The shrinkage Apparel's sample forces on it
creates that bias, so we expect it to fall as history accumulates and
cross-validation relaxes the penalty — an expectation rather than a
measurement, since the Apparel demand surface may simply be shaped differently.
Either way the remedy is more Apparel weeks, not a bigger basis or a heavier
penalty. Parity is forecast for late 2027.

---

## Exhibit B1 — How much of the error is unavoidable

Source: `analysis/outputs/b1_noise_floor.csv`, `b1_config_check.csv`. Pooled
within-configuration variance over 45 configurations of ten repeat
observations per division; 405 degrees of freedom each.

| Division | σ̂² | Approx. SE | σ̂ (units) | Mean units |
|---|---:|---:|---:|---:|
| Hardgoods | **148.1** | ± 10.4 | 12.2 | 111.9 |
| Apparel | **142.0** | ± 10.0 | 11.9 | 111.0 |

Difference (Apparel − Hardgoods) = −6.1 with a standard error of 14.4: **0.42
standard errors, indistinguishable at this precision.**

| Division | Contractor's best CV MSE | Floor | Avoidable | Share that is floor |
|---|---:|---:|---:|---:|
| Hardgoods | 231 (degree 2) | 148.1 | **82.9** | 64% |
| Apparel | 414 (degree 1) | 142.0 | **272.0** | 34% |

The estimator assumes the twelve recorded fields are constant within a
configuration; verified, 0 of 12 vary in any of the 90 configurations. This is
the **average** unavoidable error: it may vary across the demand range, and the
experiment cannot resolve whether it does (`b1_variance_shape.csv`).

## Exhibit B2 — Four models per division, against the floor

Source: `analysis/outputs/b2_table.csv`, `b2_differences.csv`. Protocol as
prescribed: 5-fold CV on the division's own training extract, basis and scaler
fitted inside each fold, ridge tuned over the 25-value grid by lowest CV MSE,
each tuned configuration refit on all training rows, then scored **once** on
the held-out repeat-observation extract. CV MSE is the average of the five fold
MSEs; the SE is their standard deviation over √5.

| Division | Degree | Penalty | Terms | Terms/row | Tuned α | CV MSE | ± SE | Test MSE | Test − σ̂² |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| Hardgoods | 1 | none | 12 | 0.004 | | 336.62 | 6.42 | 398.55 | 250.44 |
| Hardgoods | 1 | ridge | 12 | 0.004 | 10.0 | 336.61 | 6.39 | 398.38 | 250.27 |
| Hardgoods | 2 | none | 90 | 0.030 | | 233.12 | 4.64 | 246.16 | 98.05 |
| Hardgoods | 2 | ridge | 90 | 0.030 | 0.316 | **232.98** | 4.79 | 247.47 | 99.36 |
| Apparel | 1 | none | 12 | 0.061 | | 413.53 | 29.84 | 363.58 | 221.54 |
| Apparel | 1 | ridge | 12 | 0.061 | 10.0 | 412.06 | 36.19 | 354.12 | 212.08 |
| Apparel | 2 | none | 90 | 0.457 | | 617.97 | 67.54 | 366.86 | 224.82 |
| Apparel | 2 | ridge | 90 | 0.457 | 3.162 | **329.80** | 14.31 | **296.19** | **154.15** |

No tuned penalty falls on an endpoint of the grid. The contractor's four
figures reproduce under this protocol — 336.62, 233.12, 413.53, 617.97 against
his 336, 231, 414, 618, all within half a standard error
(`b2_contractor_check.csv`).

*Footnote.* The CV column is not quite like-for-like: an unpenalised cell
reports a single estimate while a ridge cell reports the lowest of 25, which
flatters it. The test column, scored once, is not subject to this.

**Paired differences, taken fold by fold so fold-to-fold variation cancels:**

| Division | Comparison | Difference | ± SE | SEs from zero |
|---|---|---:|---:|---:|
| Hardgoods | degree-1 OLS − degree-1 ridge | 0.01 | 0.05 | 0.1 |
| Hardgoods | degree-2 OLS − degree-2 ridge | 0.15 | 0.22 | 0.7 |
| Apparel | degree-1 OLS − degree-1 ridge | 1.47 | 7.26 | 0.2 |
| Apparel | degree-2 OLS − degree-2 ridge | **288.16** | 55.02 | **5.2** |
| Apparel | degree-1 OLS − degree-2 ridge | 83.72 | 19.98 | 4.2 |

Twelve of the twenty-five penalties tested in Hardgoods degree 2 sit within one
standard error of the best, so the exact value is not load-bearing; the
one-standard-error rule is what licenses standardising on degree-2 ridge there.

## Exhibit B3 — What flexibility and a penalty do to bias and variance

Source: `analysis/outputs/b3_stability.csv`, figure `b3_stability.png`. Twenty
bootstrap resamples per division, the supplied stability loop run as issued,
penalties held at the B2 values and not re-tuned. Each model refit on every
resample and asked for the same three configurations spanning low, middle and
high demand. "sd" is the spread of the twenty predictions; "bias" is their mean
minus the repeat-observation estimate of the truth. All figures in units.

| Division | Model | Mean sd | Mean \|bias\| | Bias² | Variance | Bias share |
|---|---|---:|---:|---:|---:|---:|
| Hardgoods | degree-1 OLS | 1.14 | 12.65 | 224.0 | 1.3 | 99% |
| Hardgoods | degree-1 ridge | 1.14 | 12.66 | — | — | |
| Hardgoods | degree-2 OLS | 2.83 | 3.84 | — | — | |
| Hardgoods | degree-2 ridge | **2.80** | **3.64** | 15.1 | 8.9 | 63% |
| Apparel | degree-1 OLS | 4.33 | 16.66 | 293.6 | 19.2 | 94% |
| Apparel | degree-1 ridge | 4.13 | 16.46 | — | — | |
| Apparel | degree-2 OLS | **25.24** | 18.78 | 474.9 | 664.2 | 42% |
| Apparel | degree-2 ridge | **7.22** | **15.05** | **292.8** | **52.9** | **85%** |

The truth at each configuration is itself an average of ten weeks, so it
carries a standard error of σ̂/√10 — 3.85 units in Hardgoods, 3.77 in Apparel.
A bias smaller than that is indistinguishable from zero; Apparel's 15.05 is
not. Twenty resamples give a standard deviation roughly 16% uncertain in its
own right, so 2.83 against 2.80 is not a difference.

Levels here are not comparable with Exhibit B2's: these are three
configurations rather than 45, and each fit uses a bootstrap resample holding
about 63% distinct rows rather than the full extract. Comparisons **within**
this table are sound, because they hold both fixed and vary only the model.
