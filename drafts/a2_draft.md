# A2 draft — an evaluation that matches deployment

Working draft for the A2 part of memo §1 (to the VP of Membership). Every
number is in `analysis/outputs/` from `bash analysis/run.sh` (session 3,
2026-09-20). Prose budget for §1 is two pages for A1–A3 together; this
section is about 500 words and will need trimming against A1 and A3.

---

## Exhibit A2 — Four changes to the analyst's protocol, one at a time

Source: `analysis/outputs/a2_table.csv`. Changes are cumulative; each row
adds one change to the row above. Rows 0–2 are 5-fold cross-validated on the
building window (Jan 2024 – Jun 2025: 21,031 deduplicated rows, 3,648
members). Rows 3–4 are the test window (Oct – Dec 2025), scored once.

| Row | Change | Rows scored | Churners | AUC | Kind |
|---|---|---:|---:|---:|---|
| as printed | Analyst's script: raw file, all 24 months, 14 columns, random folds | 33,340 | | 0.967 | cross-validated |
| 0 | Same protocol, deduplicated, building window only | 21,031 | 1,767 | **0.968** | cross-validated |
| 1 | + admissible columns only (12 of 14, Exhibit A2b) | 21,031 | 1,767 | **0.748** | cross-validated |
| 2 | + a member never in both the fitting and the held-out fold | 21,031 | 1,767 | **0.747** | cross-validated |
| 3 | + past to future: fit Jan 2024 – Jun 2025, score Oct – Dec 2025 | 4,556 | 408 | **0.644** | test window |
| 4 | corporate members | 860 | 34 | **0.404** | test window |
| 4 | everyone else | 3,696 | 374 | **0.641** | test window |

Footnote: all rows from 0 down use the 31,645 deduplicated member-months;
the analyst's 0.967 is on the raw file. Re-running the analyst's exact
protocol on the raw file in our harness reproduces 0.967 (`run.log`). The
validation month (Sep 2025) is unused: no choice in this section was made by
looking at data.

## Exhibit A2b — Which columns exist at the moment of scoring

Source: `analysis/outputs/a2_columns.csv`. The scoring moment is the start of
`snapshot_month`. Decided from the data dictionary's timing note for each
column.

| Decision | Columns | Timing note |
|---|---|---|
| Kept (12) | `tenure_months` | "as of the start of `snapshot_month`" |
| | `sessions_last_30d`, `app_opens_last_30d`, `avg_session_minutes`, `days_since_last_login`, `support_tickets_last_30d`, `referrals_made` | 30 days ending on the last day of the previous month |
| | `payment_failures_last_90d` | 90 days ending on the last day of the previous month |
| | `acquisition_channel`, `city_tier` | fixed at signup |
| | `plan_tier`, `monthly_price` | billing; no timing note. Read as the plan on the billing snapshot at the start of the month. A mid-month change would not be visible, which the dictionary does not rule out. |
| Dropped (2) | `winback_offer_sent` | contact "about this month", from a list circulated on the third business day **after** month close |
| | `exit_survey_started` | the cancellation flow itself; 1 on 1,810 rows, every one a cancellation month, none a non-churner (Exhibit A1 notes) |
| Not features (3) | `member_id`, `snapshot_month`, `signup_month` | identifier; the month (April 2026 is a value never seen in training); redundant with tenure |

## Exhibit A2c — What the row-3 model learned (odds ratios, largest first)

Source: `analysis/outputs/a2_odds_ratios.csv`. Fitted on the building window
only. Numeric columns are standardised inside the pipeline, so "per SD" is
one standard deviation of the building data.

| Feature | Odds ratio | Reading |
|---|---:|---|
| channel = partner_gym / paid_search / organic, vs corporate | 4.3 / 4.1 / 4.1 | a non-corporate member has about 4× the churn odds of a corporate one, all else equal |
| plan_tier = elite vs basic | 0.38 | (collinear with price; read the pair together) |
| sessions_last_30d | 0.57 per SD; 0.88 per session | each extra session cuts churn odds 12% |
| avg_session_minutes | 0.61 per SD | |
| monthly_price | 1.38 per SD | |
| days_since_last_login | 1.33 per SD | |
| tenure_months | 0.85 per SD | weak, as in Exhibit A1 |
| everything else | 0.9 – 1.1 | near nothing |

---

## Prose (draft, ~500 words)

**Order.** Columns first, folds second, time third, segment last. Two facts
fix most of it. Once the evaluation is past-to-future there are no folds left
to group, so change 2 has to precede change 3 or it measures nothing by
construction. And change 3 is the row that touches the test window, so it
comes as late as possible, and row 4 splits the same scores rather than
scoring again. Change 1 goes first because it is the one change to the data
rather than to the protocol: every row after it is measured on a model that
could actually be deployed.

**Reading the rows.** Row 0: deduplication and restricting to the building
window leave the number where it was; the leak dominates everything else.
Row 1: removing the two columns recorded after the scoring moment costs 0.22,
which is the size of what the analyst's model was reading off the
cancellation itself. Row 2: under the analyst's random split, 2,899 of 3,648
members (79.5%) have rows in two or more folds; grouping removes all of that
overlap and the number moves by 0.001, because the twelve admissible columns
contain nothing that identifies a member and a linear model cannot
manufacture identity out of shared attributes. The change was still right;
a more flexible model would have paid for it. Row 3: rows 0 to 2 were
already scored on data the fitting model had not seen. What changes here is
that the unseen data is *later*, and a model fit through June 2025 ranks
October to December at 0.644. The 0.10 is the cost of time, not of novelty.
Row 4: the same scores, split by channel. Corporate members, 860 rows and 34
churners, are ranked at 0.404, below a coin flip; everyone else at 0.641,
which is also the pooled number, since corporate is 19% of test rows but 8%
of test churners. The model's largest single term is the channel itself,
about four times the churn odds for any non-corporate channel (Exhibit A2c),
learned from 533 corporate rows with at most six months of tenure. Within the
segment its behavioural columns rank the wrong way.

**Why the rows do not decompose.** Each row measures its change on top of
the rows above it, so the differences sum to the total but the split depends
on the path. `exit_survey_started` is 1 on every churner's last row in every
period. Had past-to-future been done first with that column still in, the
test AUC would have stayed near 0.97 and time would have looked free;
dropping the columns afterwards would then have taken the whole fall,
including the 0.10 attributed here to time. Same total, different split.

**The two-month gap.** A June 2025 row's label is fixed by whether the member
cancels by 31 August 2025, so training labels encode July and August
outcomes; the gap ends training at the last month whose labels have matured
before validation starts. It also mirrors deployment: on 1 April 2026 the
two most recent months of labels will not exist either.

**Columns.** Exhibit A2b argues each of the fourteen from the dictionary's
timing note, kept and dropped alike. The one reading rather than a fact:
`plan_tier` and `monthly_price` carry no timing note and are taken as the
billing snapshot at the start of the month.

---

## Notes to self (not memo text)

### Design decisions (mine, session 3)

- Dedup before row 0, per the brief's "remove the duplicates before
  modelling". The "as printed" line is the analyst's own output, not
  re-computed; the harness check on the raw file confirms the wiring.
- "Building data" for rows 0–2 = the training window only (≤ 2025-06), so
  the test window is scored exactly once, at row 3. Row 0 therefore differs
  from "as printed" in two ways at once (dedup, window); footnoted.
- Order 1→2→3→4 for the structural reasons in the prose.
- `StratifiedGroupKFold(5, shuffle=True, random_state=0)` for change 2:
  same stratification and seed as the analyst, grouping added, so the row
  differs from row 1 in the grouping alone.
- Validation month unused in A2 (nothing chosen from data). No bootstrap CI
  on the segment AUCs: not asked for, page budget.
- No single-column reference on the test window: "score once" honoured.
- Model never touched: `analyst_pipeline()` imported unmodified.

### Arguing against the draft

- Row 4 corporate at 0.404: 34 churners. Rough SE of an AUC near 0.5 with
  34 positives and 826 negatives is about 0.05, so 0.40 is ~2 SE off, not
  pure noise. But 34 is 34. A3's corporate dollar line will be fragile
  whatever the AUC says.
- The pooled 0.644 hides the corporate number. A book at 35% corporate is
  not described by it. This is the A3 problem.
- Row 3 (0.644) is below A1's best single-column AUC (0.681), but those are
  different rows (all months vs test window). Not comparable as they stand;
  a test-window single-column reference would settle it but would score the
  test set a second time. Not done.
- `app_opens_last_30d` flips sign in the multivariable model (OR 1.12 per SD)
  versus its single-column direction in A1. Given sessions and minutes,
  opens without workouts may be a bad sign. Do not quote the single-column
  direction and the coefficient in the same breath.
- The order-independence example (3 before 1 leaves AUC near 0.97) is
  reasoned, not computed. Computing it would score the test set with the
  leaking columns in. Not done; the reasoning is the rubric item.
- Change 2 ≈ 0 in any order on this data is a coincidence of a linear model
  with no member-identifying columns, not a general rule.

### Numbers used and where they live

| Number | File |
|---|---|
| 0.967 as printed | `analyst_model_output.txt` |
| harness check 0.967 on raw | `run.log` |
| 0.968 / 0.748 / 0.747 / 0.644 / 0.404 / 0.641; rows and churners per row; 21,031 / 1,767; 4,556 / 408; 860 / 34; 3,696 / 374 | `a2_table.csv` |
| 3,648 members; 2,899 (79.5%) in 2+ folds; 613 single-row members | `a2_fold_overlap.csv` |
| channel ORs 4.3 / 4.1 / 4.1; elite 0.38; sessions 0.57 per SD, 0.88 per unit; minutes 0.61; price 1.38; login 1.33; tenure 0.85 | `a2_odds_ratios.csv` |
| 12 kept / 2 dropped / 3 ids | `a2_columns.csv` |
| corporate 19% of test rows (860/4,556), 8% of test churners (34/408) | `a2_table.csv`, arithmetic |
| 533 corporate rows in training window, tenure ≤ 6 | `a1_corporate_segment.csv` |
| 1,810 exit-survey rows, all churners | `a1_column_timing.csv` |
| test-window predictions for A3 | `a2_test_scores.csv` |
