# A1 draft — baselines

Working draft for the A1 part of memo §1 (to the VP of Membership). Not the
memo. Every number here is in `analysis/outputs/` from `bash analysis/run.sh`
(session 2, 2026-09-17) unless marked otherwise. Prose budget: §1 is two pages
for A1–A3 together, so A1 should be about a third of a page plus the exhibit.

---

## Exhibit A1 — Baselines before any modelling

Source: `analysis/outputs/a1_baselines.csv`, `a1_cleaning.txt`.

| Quantity | Value | Basis |
|---|---:|---|
| Base rate of `churn_next_60d` | **9.29%** (2,939 of 31,645 member-months) | deduplicated rows, Jan 2024 – Dec 2025 |
| *Context:* members who churn at some point in the window | 70.0% (2,939 of 4,200) | member level; a different unit, shown for scale |
| Accuracy of predicting "no churn" for everyone | **90.71%** | = 1 − base rate; uses no information |
| AUC of the same rule | **0.50** | every member scored the same, so no ranking; a coin flip |
| AUC, rank members by `avg_session_minutes` (shorter → churn) | **0.681** | one column, no fitting, all deduplicated rows |
| AUC, rank by `app_opens_last_30d` (fewer → churn) | 0.648 | " |
| AUC, rank by `days_since_last_login` (longer → churn) | 0.646 | " |
| AUC, rank by `tenure_months` (shorter → churn) | 0.502 | " |
| **Analyst's 5-fold cross-validated AUC, all 14 columns** | **0.967** | raw 33,340 rows, random shuffled folds, as printed by `analyst_model.py` |

Footnote for the exhibit: the extract contains 1,695 exact duplicate rows, all
in March 2025 (ticket NLF-2231), removed before every number above except the
analyst's, which is reported as their script prints it on the raw file.

---

## Prose (final draft for §1 A1, session 3)

**Where the model would have to start from.** About one member-month in
eleven ends in a cancellation: the base rate is 9.29%, 2,939 flagged rows out
of 31,645 after removing the duplicated March 2025 load. A rule that predicts
"no churn" for everyone is therefore 90.7% accurate while identifying nobody.
On the ranking scale the same rule scores an AUC of 0.50, a coin flip: the
90.7% and the analyst's 0.967 are on different scales and are not neighbours.
Accuracy is the wrong yardstick for two reasons: the outcome is rare, so the
number is dominated by the 91% of rows where nothing happens; and the two
mistakes cost different amounts, $18 for a wasted offer against $66 forgone
on a churner not offered, so counting them equally is the wrong loss. The
number that fits the decision is the dollar value of the programme at the
cost-derived threshold (Exhibit A3). AUC is used until then only to compare
evaluation protocols, because it needs no threshold.

Against that 0.50, ranking members by a single behavioural column, with no
model at all, gives an AUC between 0.65 and 0.68 (shorter sessions, fewer app
opens, longer since last login). Tenure alone carries no ranking signal
(0.50), and that is not a monotonicity artefact: churn sits between 6.7% and
10.1% in every tenure bucket from month 0 to 24+. The analyst's model reports
0.967.

**What would have to be true for 0.967 to describe April 2026.** Two kinds
of thing. First, the number would have to be an honest estimate of 2024–25
itself. That requires the dictionary's timing notes to be wrong, with every
column known at the start of the month rather than filled in afterwards; but
`winback_offer_sent` is written from an at-risk list circulated after month
close, and `exit_survey_started` is the cancellation flow itself, set on 1,810
rows, every one a cancellation month and none a non-churner. It also requires
that scoring a member's month from that same member's other months, or from
later months, counts as prediction. Random folds permit both, and for the
1,695 duplicated March 2025 rows they permit scoring a row against its own
copy. Second, even an honest 2024–25 number would have to transfer. The April
book would have to resemble the pooled file, but corporate members were 0% of
2024 rows, 20% of December 2025, and are forecast at 35%; in the history they
churn at 3.1% against 9.7% for everyone else, and the training window holds
533 corporate rows with at most six months of tenure. And the churn process
would have to be stable, when the monthly rate ranged from 5.3% to 14.2%,
peaking each summer, with the July 2025 competitor launch coinciding with the
second peak. Set against a best single-column AUC of 0.68, a jump to 0.97
from a linear combination of fourteen columns is, until shown otherwise, the
signature of a leak. Section A2 tests the first kind one change at a time and
measures the second by segment.

---

## Notes to self (not memo text)

### What the label actually is

From `a1_cleaning.txt`: 2,939 churners, none with more than one flagged row,
and every flagged row is the member's last row. The dictionary defines the
target as a 60-day forward window, which would normally flag two rows per
churner. The extract flags one: the cancellation month itself. So in practice
`churn_next_60d = 1` means "this is the member's final month on the book."
Worth one line in the memo (shows the dictionary was checked, not trusted).
It also means the brief's two-month gap between training and validation is
conservative; keep it anyway — the brief fixes the windows for comparability,
and a protocol should be safe under the documented definition.

### Evidence for the leakage claim

Source: `analysis/outputs/a1_column_timing.csv`. Usable in the memo.

| | `exit_survey_started` | `winback_offer_sent` |
|---|---:|---:|
| Rows with a 1 | 1,810 (5.7%) | 3,533 (11.2%) |
| Churners among them | 1,810 — all | 2,239 (63.4%) |
| Non-churners among them | 0 | 1,294 |
| P(churn \| 0) | 3.8% | 2.5% |
| Share of churners with a 1 | 61.6% | 76.2% |
| 1s on the member's last row | 1,810 of 1,810 | 2,288 of 3,533 |
| AUC of the column alone | 0.808 | 0.858 |

Mechanism, in one sentence: the row is scored at the start of the month, but
these two columns record events during or after it, so on 1 April 2026 they
will be 0 for everyone — including the members who go on to cancel — and what
the model learned from them is worthless at deployment.

The framing for the memo paragraph (yours): for 0.967 to hold, the
dictionary's timing notes would have to be wrong — the columns would have to
be known at the start of the month rather than filled in afterwards. The
extract says they were filled in afterwards: a column that is 1 only on
cancellation months and never on a non-churner is recording the cancellation,
not predicting it.

### Arguing against the draft

- The 0.68 → 0.97 gap is a suspicion, not proof; fourteen columns can beat any
  one. Keep "until shown otherwise"; A2 change 1 is the test.
- Seasonality vs competitor: 2024 also peaked in Jul–Sep (12.4–13.3%), swing
  6.4→13.3 (6.9 pts) against 2025's 5.3→14.2 (8.9 pts). Seasonality is the
  dominant pattern. The bigger July 2025 step is mostly an unusually low
  spring 2025, which is also when corporate members arrived. Two years cannot
  separate competitor from season; the draft says "coinciding with," not
  "caused by." Keep it that way. Carry to A3: test window is Oct–Dec (8.4–9.5%),
  deployment is Apr–Jun (5.3–7.1% in 2025). Different seasons.
- Corporate (session 3, `a1_corporate_segment.csv`): 328 members, 2,130 rows,
  churn 3.1% vs 9.7%; tenure 0–12 over the extract, at most 6 in the training
  window, 533 rows there. Shift does not automatically lower AUC; ranking
  within corporate could be easier or harder. A priori the estimate is
  uncertain, not "too high." Change 4 measures it.
- Two kinds of failure, kept apart in the memo: (i) leaks and fold
  contamination make 0.967 wrong about 2024–25 itself, fixed by A2 changes
  1–3; (ii) the book moving means an honest number still may not transfer,
  measured by change 4, not fixable by protocol.
- `tenure_months` at 0.50 is not a bug, and (checked session 3) not a
  monotonicity artefact either: `a1_churn_by_tenure.csv` shows 6.7% to 10.1%
  in every bucket, no month-12 spike, no early cliff. Tenure is simply
  near-uninformative here. The general point still holds for the midterm: AUC
  and a linear logit both see only monotone signal, and a U-shaped column
  would score 0.50 while carrying information; binning is the fix in that
  case. Not this case.
- 70% of members churning over 24 months is consistent with a 9% 60-day rate
  (a hazard of roughly 4.5%/month compounds to ~67% over 24 months).
- Row counts differ from the analyst's (31,645 vs 33,340) because of dedup;
  the duplicated March 2025 rows have a below-average rate (6.0%), so dedup
  raises the base rate slightly. Footnoted in the exhibit.
- Everything came out as expected. Course doc §4: that is the moment to slow
  down, not speed up. The one thing not expected — the label structure — was
  found by checking rather than trusting.

### Numbers used and where they live

| Number | File |
|---|---|
| 9.29%, 2,939 / 31,645; 70.0%, 2,939 / 4,200; 90.71%; AUC 0.50; AUCs 0.681 / 0.648 / 0.646 / 0.502; 0.967 | `a1_baselines.csv` |
| 1,695 duplicates, all 2025-03; 31,645 rows; one flag per churner, 2,939 of 2,939 on last row | `a1_cleaning.txt` |
| 2024: 10.61%, corporate 0%; 2025: 8.62%, corporate 10.1% | `a1_base_rate_by_year.csv` |
| 5.3% (2025-04), 14.2% (2025-08), 2024 Jul–Sep 12.4–13.3%, corporate 20.2% in 2025-12 | `a1_base_rate_by_month.csv` |
| 1,810 / 0 / 61.6% / 0.808; 3,533 / 2,239 / 76.2% / 0.858 | `a1_column_timing.csv` |
| 6.7% (month 2) to 10.1% (months 6–8), all buckets | `a1_churn_by_tenure.csv` |
| corporate 3.1% vs 9.7%; 328 members; 533 rows to 2025-06, tenure max 6 there | `a1_corporate_segment.csv` |

### How to use the leakage evidence in the memo (settled end of session 2)

The *reason* to drop `exit_survey_started` and `winback_offer_sent` is the
dictionary's timing notes: not available at the moment of scoring. That is
what the rubric grades ("argued from availability at the moment of scoring").
The cross-tab and single-column AUCs are *corroboration* that the timing note
holds in this extract, and they size what A2 change 1 should do to the
number. Order in the memo: timing argument first, evidence second. Never
"dropped because they predict too well" — a genuinely available column with
a high AUC should be kept.
