# A3 draft — the targeting decision

Draft for the A3 part of memo §1 (to the VP of Membership). Every number is in
`analysis/outputs/` from `bash analysis/run.sh` (session 4, 2026-09-29).

**Prose budget warning.** A1 is 499 words and A2 552, so §1 is at 1,051 before
this section. Two pages of prose is roughly 1,000–1,200 words. A3 below is
~430. Something has to come out — candidates at the end of this file.

---

## The recommendation (this leads memo §1)

> **Run the programme on non-corporate members only, and instrument it so it
> can be stopped.** On the test quarter it would have returned **$852**, not
> the $19,774 per quarter in the current proposal. Excluding corporate
> members raises that to **$930**: corporate offers landed on a churner 11% of
> the time against the 21.4% needed to break even, and corporate is forecast
> to grow from 19% of the book to 35%. Bring corporate back in only when it
> has enough history to be fitted on — today the training window holds 533
> corporate rows, none older than six months. Measure **realised value per
> offer** on matured 60-day outcomes each quarter and suspend the programme
> if it falls below zero, which is the same as the share of offers reaching a
> churner falling below 21.4%.

---

## Exhibit A3a — Test-window ranking, overall and by segment

Source: `analysis/outputs/a2_table.csv`. Fit on Jan 2024 – Jun 2025, scored
once on Oct – Dec 2025.

| Segment | Rows scored | Churners | AUC |
|---|---:|---:|---:|
| All | 4,556 | 408 | **0.644** |
| Corporate | 860 | 34 | **0.404** |
| Everyone else | 3,696 | 374 | **0.641** |

## Exhibit A3b — The threshold, derived from the finance table

Full working in `analysis/outputs/a3_threshold.txt`, computed from the
constants in `starter/load.py`.

An offer to a member who would have churned is worth 240 × 0.35 − 18 = **$66**.
An offer to a member who would not have churned costs **$18**. No offer is
worth $0. At predicted probability *p*,

  E[value of offering | p] = 66p − 18(1 − p) = **84p − 18**

which exceeds the $0 of not offering when

  **p > 18 / 84 = 0.2143**

Cross-check against the general form, t\* = C_FP / (C_FP + C_FN) with a wasted
offer at $18 and a missed churner at $66: 18/(18+66) = 0.2143. Same number.

Two things follow. The threshold depends only on the finance figures, not on
the data, and it was fixed before any test-window score was read. And 0.2143
is also the **break-even precision**: value per offer is exactly
84 × (precision − 0.2143), so the programme pays only while more than 21.4% of
its offers reach a member who would have cancelled.

## Exhibit A3c — Realised value on the test quarter

Source: `analysis/outputs/a3_value.csv`. Oct – Dec 2025, 4,556 member-months,
408 churners. One offer = one member-month.

| Policy | Offers | Reached a churner | Wasted | Value |
|---|---:|---:|---:|---:|
| **Targeted at t\* = 0.2143** | 242 | 62 | 180 | **+$852** |
| — corporate | 9 | 1 | 8 | **−$78** |
| — everyone else | 233 | 61 | 172 | **+$930** |
| Offer to every member-month | 4,556 | 408 | 4,148 | **−$47,736** |
| No programme | 0 | — | — | $0 |
| *Memo: at the analyst's 0.267* | 108 | 33 | 75 | +$828 |

The quarter's total carries a standard error of **$572** — each offer returns
+$66 or −$18, and the total is a sum of 242 such draws, so $852 sits 1.5
standard errors above zero.

## Exhibit A3d — Where the value comes from, and where it does not

Source: `analysis/outputs/a3_by_month.csv`, `a3_offer_quality.csv`.

| Month | Offers | Precision | Value | Per offer |
|---|---:|---:|---:|---:|
| Oct 2025 | 114 | 21.9% | +$48 | $0.42 |
| Nov 2025 | 81 | 33.3% | +$810 | $10.00 |
| Dec 2025 | 47 | 21.3% | −$6 | −$0.13 |

| Inside the offered set | Offers | Model says | Actually churned | Per offer |
|---|---:|---:|---:|---:|
| First contact | 195 | 28.6% | 26.2% | $3.97 |
| Repeat contact | 47 | 28.4% | 23.4% | $1.66 |
| Q1, just above t\* | 61 | 22.2% | 18.0% | −$2.85 |
| Q4, highest scores | 61 | **39.6%** | **27.9%** | $5.41 |

**Figure A3** (`a3_value_curve.png`): realised value across the whole
threshold range, with the decision region at its own scale.

---

## Prose (draft, ~430 words; the recommendation above is the opening paragraph)

**What the programme is worth.** Using the protocol in Exhibit A2 — admissible
columns only, fitted on Jan 2024 to Jun 2025, scored once on Oct to Dec 2025 —
the targeting rule returns $852 on the quarter. The proposal in front of the
committee says $19,774. The gap is not the threshold: applying the analyst's
own 0.267 to honest scores returns $828, within $24 of our derived figure. The
gap is that their number was computed on predictions that had already seen the
cancellation, and on a random shuffle of two years rather than a fit to the
past scored on the future.

**Why the margin is thin.** An offer costs $18 and a retained churner returns
$66, so the programme pays only while more than 21.4% of offers reach someone
who would have cancelled. The base rate is 9%. That requires finding members at
roughly two and a half times the average risk, and the model manages 25.6% in
the top 5% of the book — profitable, but by four percentage points. Month to
month that margin straddles zero: November returned $810, October $48 and
December −$6. With 47 to 114 offers in a month those differences are mostly
noise, and that is the point — the programme sits close enough to break-even
that ordinary variation puts individual months on either side.

**Why corporate comes out.** Corporate members were ranked below a coin flip
(AUC 0.404 on 34 churners) and their nine offers landed on a churner once.
The model's single largest term is the acquisition channel itself, about four
times the churn odds for any non-corporate channel, learned from 533 corporate
rows none older than six months. It has learned that corporate members rarely
cancel, not which of them will. Excluding them adds $78 to the quarter and
removes a segment forecast to triple its share of the book.

**What to watch.** The threshold assumes the predicted probabilities mean what
they say. They roughly do — checked on the validation month, and corrected
there before use — but the model still overstates the risk of the members it
picks, claiming 39.6% for its top-scoring offers and delivering 27.9%. That is
what selecting the top of a noisy score does, and it is why the tripwire
should be a dollar figure rather than a ranking statistic: AUC can hold steady
while the probabilities drift and the cut point stops meaning what it meant.
Two further reasons to expect less than $852 next spring: April to June ran
5.3–7.1% churn against this quarter's 9.0%, and 1,294 members in the history
already received a retention contact, so part of the outcome we are fitting to
is itself post-treatment.

---

## Notes to self (not memo text)

### Design decisions (mine, session 4)

- One offer = one member-month, matching the monthly programme and the brief's
  per-offer economics. Per-member accounting was rejected: a churner has only
  one flagged row, so "which month did the single offer happen in" has no
  honest answer.
- Quarter as the reporting period (the test window is exactly one quarter).
  Monthly split added later, after it turned out to be informative rather than
  decorative — see below.
- Priced against offer-everyone, no programme, and the analyst's threshold.
  Declined to score the test window with the analyst's *model*: that would be
  a second scoring, and A2 already set the norm against it.
- Calibration checked on the validation month and corrected there. The verdict
  was set from validation evidence (Platt slope 0.79, under-prediction in 8 of
  10 bins) **before** any dollar figure existed. It cost $30 — raw scores give
  $882 — which is the point: chosen on calibration grounds, not on payout.
- Value curve reported. It re-reads the same scores at 400 cut points; no new
  scoring, and t* was fixed in advance. The curve peaks at $1,098 at 0.236;
  not selecting on the test set cost $264, stated in the memo rather than hidden.
- Recommendation shape chosen before the dollar figure was computed.

### Arguing against the draft

- **$852 ± $572 is 1.5 SE from zero.** A "deploy" that rests on it is resting
  on a coin that landed the right way. The scoped-and-instrumented shape is
  what the uncertainty supports; an unconditional go is not.
- **Corporate's −$78 is nine offers and one churner.** The dollar line is
  nearly meaningless on its own. The argument for exclusion rests on 34
  churners at AUC 0.404, 533 training rows, and the mechanism (the model learned
  the channel, not the members) — not on the $78.
- **The quartile table is suggestive, not conclusive.** ~15 churners per
  quartile; only the Q4 gap (39.6% claimed, 27.9% delivered) is about two
  standard errors. Do not present Q1–Q3 as an established pattern.
- **Repeat contacts are a second-order drag, not a defect.** $1.66 versus
  $3.97 per offer, both above break-even. Worth a sentence, not a policy fight.
  32 members were flagged more than once and never churned, costing $1,224.
- **Seasonality cuts both ways.** Oct–Dec is a *higher*-churn quarter than
  Apr–Jun, so the $852 is probably optimistic for deployment — but 2024 shows
  the same summer peak, so the level is seasonal rather than a trend, and the
  April book is not simply "worse".
- **The recommendation excludes 19% of the current book and a forecast 35%.**
  That is a large operational carve-out to justify on 34 churners. The honest
  framing is that we cannot yet tell whether the model helps on corporate, not
  that we know it hurts.

### What changed my mind this session

- I expected the monthly split to be decorative and advised skipping it (D2).
  It turned out to carry the clearest evidence that the value is unstable, so
  it went in. Recorded because it is exactly the kind of pre-commitment that
  should be revisited when the data disagree.
- I predicted that fitting the calibration on September (10.8% base rate)
  would over-correct for a lower-rate test window. Wrong: the raw model
  under-predicts on the test window too, because the test book is more
  corporate and the model scores corporate low.

### Trimming candidates for the two-page limit (need ~450 words out)

1. A1's loss sentence — A3's break-even paragraph says it better (~40 words).
2. A1's corporate and seasonality figures → move to exhibit footnotes (~90).
3. A2's "reading the rows" row-by-row commentary → compress rows 0 and 2,
   which moved least (~120).
4. A2's odds-ratio prose → Exhibit A2c already carries it (~60).
5. A3's final paragraph's post-treatment clause → exhibit footnote (~40).

### Numbers used and where they live

| Number | File |
|---|---|
| AUC 0.644 / 0.404 / 0.641; 4,556 / 408; 860 / 34; 3,696 / 374 | `a2_table.csv` |
| t* = 0.2143, the derivation, both routes | `a3_threshold.txt` |
| $852 / −$78 / +$930 / −$47,736 / $0 / $828; offers and churner counts | `a3_value.csv` |
| SE $572; 1.5 SE from zero | `run.log` (from `value_with_se`) |
| Monthly: 114/81/47 offers, 21.9/33.3/21.3%, $48/$810/−$6 | `a3_by_month.csv` |
| First vs repeat $3.97 / $1.66; Q1 −$2.85; Q4 39.6% vs 27.9% | `a3_offer_quality.csv` |
| Validation: Platt slope 0.788, intercept −0.219, 8 of 10 bins under | `a3_calibration.csv`, `run.log` |
| Curve peak $1,098 at 0.236; raw-score sensitivity $882 | `a3_value_curve.csv`, `run.log` |
| 533 corporate training rows, tenure ≤ 6 | `a1_corporate_segment.csv` |
| Channel odds ratios ~4× | `a2_odds_ratios.csv` |
| Apr–Jun 5.3–7.1% vs Oct–Dec 8.4–9.5% | `a1_base_rate_by_month.csv` |
| 1,294 non-churners with `winback_offer_sent` = 1 | `a1_column_timing.csv` |
