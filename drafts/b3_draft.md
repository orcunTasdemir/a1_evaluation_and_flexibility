# B3 draft — the stability experiment

Draft for the B3 part of memo §2 (to the VP of Merchandising Planning). Every
number is in `analysis/outputs/` from `bash analysis/run.sh` (session 6,
2026-10-01).

**Prose budget.** §2 is one page for B1–B3 together, roughly 450–500 words.
The brief asks B3 for "one sentence each" on three questions, so B3's share
is about 110 words. Everything below the prose is notes.

---

## Exhibit B3 — What flexibility and a penalty do to bias and variance

Source: `analysis/outputs/b3_stability.csv`, figure `b3_stability.png`.
Twenty bootstrap resamples of each division's training extract, the supplied
`stability.py` loop run as issued, penalties held at the B2 values and not
re-tuned. Each model refit on every resample and asked for the same three
query configurations (low, middle and high demand). "sd" is the spread of the
twenty predictions; "bias" is their mean minus the replicate-based truth.
Averaged over the three points.

| Division | Model | Terms | Rows/term | Mean sd | Mean \|bias\| | Signed bias | Bias² | Variance | Bias share |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Hardgoods | degree-1 OLS | 12 | 250.0 | 1.14 | 12.65 | +1.35 | 224.0 | 1.3 | 99% |
| Hardgoods | degree-1 ridge | 12 | 250.0 | 1.14 | 12.66 | +1.34 | 223.6 | 1.3 | 99% |
| Hardgoods | degree-2 OLS | 90 | 33.3 | 2.83 | 3.84 | +0.86 | 16.4 | 9.1 | 64% |
| Hardgoods | degree-2 ridge | 90 | 33.3 | 2.80 | 3.64 | +1.05 | 15.1 | 8.9 | 63% |
| Apparel | degree-1 OLS | 12 | 16.4 | 4.33 | 16.66 | +9.35 | 293.6 | 19.2 | 94% |
| Apparel | degree-1 ridge | 12 | 16.4 | 4.13 | 16.46 | +8.70 | 282.7 | 17.5 | 94% |
| Apparel | degree-2 OLS | 90 | 2.2 | 25.24 | 18.78 | -6.16 | 474.9 | 664.2 | 42% |
| Apparel | degree-2 ridge | 90 | 2.2 | 7.22 | 15.05 | +4.15 | 292.8 | 52.9 | 85% |

**sd is not the variance.** Mean sd and mean |bias| are in **units**;
bias² and variance are their squares, in **units²**, and that is the only
scale on which the two can be compared or added (Err = Bias² + Var + σ²).
The brief writes "the standard deviation of the 20 predictions (variance)",
meaning the variance *component* of the decomposition; the reportable form
is the sd and the additive form is its square. Squaring is done per query
point and then averaged, not the other way round, because the
decomposition holds at each point.

The truth at each query point is itself an average of
ten weeks, so it carries a standard error of σ̂/√10: 3.85 units in Hardgoods
and 3.77 in Apparel using the pooled floor. The floor varies by configuration,
so the yardstick does too; per query point it runs 3.60 / 1.95 / 4.06 (H) and
3.64 / 3.34 / 4.81 (A), from `b1_query_yardsticks.csv`. A bias of that size is
indistinguishable from zero.

### Per query point (q1 low, q2 middle, q3 high demand)

| Division | Model | sd q1 | sd q2 | sd q3 | bias q1 | bias q2 | bias q3 |
|---|---|---:|---:|---:|---:|---:|---:|
| Hardgoods | degree-1 OLS | 1.02 | 1.15 | 1.25 | **+21.01** | **−15.06** | −1.89 |
| Hardgoods | degree-2 OLS | 1.97 | 4.33 | 2.18 | −4.46 | +5.01 | +2.05 |
| Hardgoods | degree-2 ridge | 1.96 | 4.28 | 2.16 | −3.89 | +5.15 | +1.88 |
| Apparel | degree-1 OLS | 3.39 | 5.07 | 4.52 | +19.60 | +19.40 | −10.97 |
| Apparel | degree-2 OLS | 18.08 | **30.25** | 27.40 | +18.94 | −5.17 | **−32.24** |
| Apparel | degree-2 ridge | 5.96 | 7.62 | 8.07 | +24.31 | +4.48 | −16.35 |

(Degree-1 ridge omitted here: identical to degree-1 OLS to two decimals in
both divisions. Full table in the CSV.)

---

## Prose (draft, ~170 words)

**What raising the degree did.** In Hardgoods it bought the trade it is
supposed to: the spread of the predictions rose from 1.14 units to 2.83 while
the typical distance from the truth fell from 12.65 to 3.84, so a small
amount of instability purchased a large correction. In Apparel it bought
nothing: the spread rose from 4.33 to 25.24, nearly six-fold, and the
distance from the truth did not improve at all, moving from 16.66 to 18.78.

**What the penalty did.** Nothing at degree 1, in either division — 1.14 to
1.14 in Hardgoods and 4.33 to 4.13 in Apparel, with bias unchanged to within
0.2 units. At degree 2 it is nothing in Hardgoods (2.83 to 2.80) and
decisive in Apparel, cutting the spread from 25.24 to 7.22, a 71% reduction,
while also improving bias slightly.

**Why the same four procedures answer differently.** Ninety terms estimated
from 3,000 rows is 0.03 terms per row; from 197 rows it is 0.46. That ratio,
not the division's size, is what B2 found separates the cell where the
penalty is worth 288 units² of cross-validated error from the three where it
is worth nothing, and it is the same ratio that makes Apparel's degree-2
predictions move nine times as much as Hardgoods'.

---

## Notes to self (not memo text)

### Design decisions (mine, session 6)

- **The supplied loop runs as issued.** `analysis/part2/b3_stability.py`
  imports `part2_cascade/starter/stability.py` rather than copying or editing
  it, and supplies the three things it leaves blank: the two penalty dicts,
  `build_models()`, and the output path. `git diff` against the supplied
  folder stays empty. Defensible in one sentence: the measurement is the
  instructor's, only the four models are mine.
- **Penalties read from `b2_penalties.csv`,** not retyped, so they cannot
  drift from B2 and cannot be re-tuned inside the resamples.
- **Output to `analysis/outputs/`** as `b3_stability.csv` and `.png`, dropping
  the starter's `b3_outputs/` folder. This **overrides the session-1 decision**
  to keep the starter's folder names; one consistent output location won, and
  B1 and B2 already write there.
- **Signed mean bias added** as a column the starter does not compute. It
  earns its place: see the cancellation point below.
- **sd reported, not sd².** The brief asks for the standard deviation. Squared
  units appear only where proportions are being compared, and then they are
  computed as mean-of-squares, not square-of-mean.

### An independent check the starter embeds

`stability.py`'s comment on the penalties says "at one of the two degrees the
two divisions land in the same place, and at the other they do not." Ours:
degree 1 is α = 10.0 in **both** divisions, degree 2 is 0.316 (H) against
3.162 (A). Hint satisfied. Second embedded check Part B has passed, after
σ̂/√10 ≈ 4 in B1. Both are worth one line in the process note.

(Consequence: my B2 note calling the degree-1 α "close to arbitrary" was too
strong and has been softened. The curve is flat — 19 of 25 α values within
one SE of the minimum in Hardgoods, 16 of 25 in Apparel — but both divisions
finding the same minimum is evidently expected, not luck.)

### Why signed bias was worth adding

Hardgoods degree-1 OLS: biases of **+21.01, −15.06, −1.89**. Mean absolute
12.65, signed mean **+1.35**. Reported signed alone, that model looks nearly
unbiased. It is not: it is a surface too rigid to bend, over-predicting low
demand by 21 units and under-predicting middle demand by 15, and the two
merely cancel in the average. Degree 2 flattens it to −4.46, +5.01, +2.05.
Mean absolute is the right headline; signed mean is the diagnostic that
reveals the shape. One clause in §2 if the budget allows.

### The finding that changes §2's conclusion

Converting to units² so bias and variance can be compared (mean of squares at
each query point, because the decomposition holds at each point):

| Division | Model | Bias² | Variance | Total | Bias share |
|---|---|---:|---:|---:|---:|
| Hardgoods | degree-1 OLS | 224.0 | 1.3 | 225.3 | 99% |
| Hardgoods | degree-2 ridge | 15.1 | 8.9 | 24.0 | 63% |
| Apparel | degree-1 OLS | 293.6 | 19.2 | 312.9 | 94% |
| Apparel | degree-2 OLS | 474.9 | 664.2 | 1139.0 | 42% |
| Apparel | degree-2 ridge | **292.8** | **52.9** | 345.7 | **85%** |

I predicted before running that Apparel's problem would be variance. For the
unpenalised degree-2 fit that is right — variance is the majority, 664 of
1,139. But **the penalty converts it into a bias problem**: Apparel's best
model carries 293 units² of bias² against 53 of variance. A mean absolute
bias of 15.05 units against a 3.77-unit yardstick is unambiguously real.

So "Apparel is unstable, penalise it" is only half the story. The penalty has
already done its work; what remains is a model too rigid to follow the
Apparel demand surface, and the fix is more Apparel history, not a different
estimator. That is what the company-wide standard should say, and it is the
bridge from B3 into the standard-a-process answer.

### Why Apparel's bias got *worse* at degree 2 (settled session 8)

Bias² at 90 terms: Hardgoods 16.4, Apparel 474.9. More flexibility made Apparel
worse, which looks impossible, since a richer basis can represent anything the
poorer one could.

The resolution is in how bias is measured here: the distance from the truth of
the **mean of twenty refits**. At 2.2 rows per coefficient the fits are not just
variable, their average is displaced too. The model is not wrong in a consistent
direction, it is unanchored. So the extra flexibility is unusable rather than
harmful in principle: there is not enough data to locate it.

Three consequences, all of which the memo now states:

- **The penalty did not create Apparel's bias.** Unpenalised degree 1, with no
  shrinkage at all, carries bias² 293.6; penalised degree 2 carries 292.8. Same
  bias, reached two different ways. What the penalty did was rescue degree 2
  from 474.9 back to where twelve terms already sat, by trading away variance
  that 197 rows could not support (664.2 → 52.9).
- **Hardgoods is the evidence that rows are the remedy.** The identical
  specification, degree-2 ridge, reaches bias² 15.1 on 3,000 rows. Not a
  controlled experiment, since the two demand surfaces differ, but it does
  refute "the shrinkage causes the bias", because Hardgoods shrinks too.
- **An earlier draft said the bias should fall "as history accumulates and
  cross-validation relaxes the penalty", and called that an expectation rather
  than a measurement.** The mechanism was wrong, since the penalty is not what
  put the bias there. Corrected in the memo.

### B3 and B2 rank Apparel differently, and B2 is the one to trust

| | Apparel degree-1 OLS | Apparel degree-2 ridge |
|---|---:|---:|
| B3, bias² + variance at 3 query points | **312.9** | 345.7 |
| B2, test MSE over all 45 configurations | 363.58 | **296.19** |

Opposite orderings. Not a contradiction, and the same reason as the level
mismatch: three query points chosen to span the demand range are not a sample
of the 45, and bootstrap fits on ~123 distinct rows penalise a 90-term model
more than a 12-term one. **B2 answers which procedure is better; B3 answers
what kind of error each one has.** Do not use B3 to rank, and do not let the
memo imply that B3 endorses the degree-2 ridge choice. It does not need to.

### Arguing against the draft

- **Twenty resamples is few.** A standard deviation from 20 draws has roughly
  16% relative uncertainty of its own. So 2.83 vs 2.80 in Hardgoods degree 2
  is not a finding, and neither is 4.33 vs 4.13 in Apparel degree 1. Both are
  reported as "nothing", which is the honest reading, and that is also what
  B2's paired CV differences said (0.15 ± 0.22 and 1.47 ± 7.26).
- **B3's levels are not comparable with B2's**, and the gap decomposes
  (measured in session, 2026-10-01):

  | Quantity | Value | What changed |
  |---|---:|---|
  | B2: one fit on 197 rows, all 45 configs | 154.2 | the reported number |
  | Same fit, the 3 query points only | 257.3 | which points |
  | B3: 20 bootstrap fits, same 3 points | 345.7 | which fits |

  *Which points:* the three are chosen to span low/middle/high demand, so two
  sit at the extremes where a rigid surface fits worst. Per point, the
  full-data fit's reducible error is A10 = 624, A08 = −12, A07 = 159. The 45
  are mostly mid-range. *Which fits:* a bootstrap resample holds only about
  63% distinct rows (measured 0.625, ~123 of 197), so each B3 fit estimates
  90 terms from ~123 rows instead of 197; that is the extra 88.

  **Do not put 345.7 and 154.15 in the same sentence of the memo.** Their
  difference means nothing, and it would read as B3 contradicting B2 when
  they agree. Comparisons *within* a table are safe, because those hold the
  points and the fits fixed and vary only the model. B2 for levels, B3 for
  mechanism.

  (Aside worth knowing: A08's −12 is below zero, which no real reducible
  error can be. `test MSE − σ̂²` is unbiased averaged over configurations, not
  guaranteed non-negative at any single one.)
- **The bootstrap measures variance over resamples, not over genuinely new
  samples.** It is the standard proxy and the brief prescribes it, but a
  resample is drawn from the one extract we have, so it cannot see variation
  the extract itself does not contain.
- **Bias here is measured against a replicate mean, not the truth.** Same
  σ̂/√10 wobble as everywhere else in Part B; ~3.8 units. It is why "nearly
  zero" has to mean "under about 4", not "under 1".
- **Three query points is three.** They were chosen by the instructor to span
  the demand range, which is the right design, but no claim about how bias
  behaves *across* feature space can rest on three points. The per-point
  signs are suggestive (both divisions over-predict low demand and
  under-predict high), not established.
- **Apparel degree-2 ridge still has the largest bias of any Apparel model
  bar degree-2 OLS**, and its signed mean is +4.15 while its per-point
  biases run +24.31, +4.48, −16.35. It is the best of the four and still not
  a good model. Say that plainly rather than letting "the penalty fixed it"
  stand unqualified.

### Numbers used and where they live

| Number | File |
|---|---|
| All eight rows: sd and bias at each query point, mean sd, mean \|bias\|, signed mean | `b3_stability.csv` |
| The figure | `b3_stability.png` |
| Penalties 10.0 / 10.0 / 0.316 / 3.162 | `b2_penalties.csv` |
| σ̂/√10 = 3.85 / 3.77 | `b1_noise_floor.csv`, printed in `run.log` |
| Terms per row 0.03 / 0.46; penalty worth 288 ± 55 | `b2_table.csv`, `b2_differences.csv` |
| Bias² / variance split (units²), bias share 85% / 42% / 63% | `b3_stability.csv` columns `bias2_mean`, `variance_mean`, `bias_share_pct` |
