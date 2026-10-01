# B2 draft — four models against the floor

Draft for the B2 part of memo §2 (to the VP of Merchandising Planning). Every
number is in `analysis/outputs/` from `bash analysis/run.sh` (session 6,
2026-10-01).

**Prose budget.** §2 is one page for B1, B2 and B3 together, roughly 450–500
words. B1 uses about 60. B2's three questions are "two or three sentences
each," so B2's share is about 250 words. Everything below the prose is notes,
not memo text.

---

## Exhibit B2 — Four models per division, against the noise floor

Source: `analysis/outputs/b2_table.csv`. Protocol as prescribed: 5-fold CV
with `make_folds()` (seed 575) on the division's own training extract, basis
and scaler fitted inside each fold via `poly_pipeline()`, ridge tuned over
the 25-value `ALPHA_GRID` by lowest CV MSE, each tuned configuration refit on
all training rows, then scored once on `test_extract()`. CV MSE is the average
of the five fold MSEs; the SE is their standard deviation over √5.

| Division | Degree | Penalty | Terms | Terms per row | Tuned α | CV MSE | ± SE | Test MSE | Test − σ̂² |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| Hardgoods | 1 | none | 12 | 0.004 | | 336.62 | 6.42 | 398.55 | 250.44 |
| Hardgoods | 1 | ridge | 12 | 0.004 | 10.0 | 336.61 | 6.39 | 398.38 | 250.27 |
| Hardgoods | 2 | none | 90 | 0.030 | | 233.12 | 4.64 | 246.16 | 98.05 |
| Hardgoods | 2 | ridge | 90 | 0.030 | 0.316 | **232.98** | 4.79 | 247.47 | 99.36 |
| Apparel | 1 | none | 12 | 0.061 | | 413.53 | 29.84 | 363.58 | 221.54 |
| Apparel | 1 | ridge | 12 | 0.061 | 10.0 | 412.06 | 36.19 | 354.12 | 212.08 |
| Apparel | 2 | none | 90 | 0.457 | | 617.97 | 67.54 | 366.86 | 224.82 |
| Apparel | 2 | ridge | 90 | 0.457 | 3.162 | **329.80** | 14.31 | **296.19** | **154.15** |

σ̂² = 148.11 (Hardgoods), 142.04 (Apparel), from Exhibit B1. No tuned α falls
on an endpoint of the grid.

*Footnote.* The CV column is not quite like-for-like: an unpenalised cell
reports a single estimate, while a ridge cell reports the lowest of 25, which
flatters it. The test column, scored once, is not subject to this.

## Exhibit B2b — Paired CV differences within a division

Source: `analysis/outputs/b2_differences.csv`. The five folds are identical
across cells, so differences are taken fold by fold and the fold-to-fold
variation cancels. "SEs from zero" is the difference over its own standard
error.

| Division | Comparison | Difference | ± SE | SEs from zero |
|---|---|---:|---:|---:|
| Hardgoods | degree-1 OLS − degree-1 ridge | 0.01 | 0.05 | 0.1 |
| Hardgoods | degree-2 OLS − degree-2 ridge | 0.15 | 0.22 | 0.7 |
| Hardgoods | degree-1 OLS − degree-2 OLS | 103.50 | 5.31 | 19.5 |
| Apparel | degree-1 OLS − degree-1 ridge | 1.47 | 7.26 | 0.2 |
| Apparel | degree-2 OLS − degree-2 ridge | **288.16** | 55.02 | **5.2** |
| Apparel | degree-1 OLS − degree-2 OLS | −204.44 | 52.90 | −3.9 |
| Apparel | degree-1 OLS − degree-2 ridge | 83.72 | 19.98 | 4.2 |

## Exhibit B2c — The contractor's figures, reproduced

Source: `analysis/outputs/b2_contractor_check.csv`. His specifications refit
under the prescribed protocol.

| Division | Degree | His CV MSE | Ours | Difference | SEs from his |
|---|---:|---:|---:|---:|---:|
| Hardgoods | 1 | 336 | 336.62 | +0.62 | 0.10 |
| Hardgoods | 2 | 231 | 233.12 | +2.12 | 0.46 |
| Apparel | 1 | 414 | 413.53 | −0.47 | −0.02 |
| Apparel | 2 | 618 | 617.97 | −0.03 | 0.00 |

---

## Prose (draft, ~300 words)

**Where the penalty earns its keep.** In one cell out of four, and
overwhelmingly: Apparel at degree 2, where the penalty takes cross-validated
error from 618 to 330, a drop of 288 against a standard error of 55. In the
other three it does nothing measurable — 0.01 in Hardgoods degree 1, 0.15 in
Hardgoods degree 2, 1.47 in Apparel degree 1, none of them as large as its
own standard error. What separates them is not the size of the division but
the number of terms it has to estimate per row of data: 0.46 terms per row in
the cell where the penalty matters, against 0.004, 0.030 and 0.061 where it
does not. Apparel degree 1 is the proof that "Apparel is small" is not the
explanation: same 197 rows, twelve terms instead of ninety, and the penalty
buys nothing.

**One specification can serve both divisions.** The contractor compared
unpenalised fits and concluded otherwise. Allow each specification a tuned
penalty and degree-2 ridge is at least as good as the best hand-picked choice
in both: 232.98 against 233.12 in Hardgoods, a difference of 0.15 ± 0.22, and
329.80 against 413.53 in Apparel, better by 83.72 ± 19.98. The
one-standard-error rule is what licenses the Hardgoods half of that claim —
degree-2 ridge and the contractor's degree-2 OLS are well inside one standard
error of each other, so there is no evidence to prefer his, and twelve of the
twenty-five penalties tested sit within one standard error of the best, so
the exact value is not load-bearing.

**How firm the Apparel ordering is.** Not uniformly. Apparel's standard
errors run 14 to 68 against Hardgoods' 4.6 to 6.4, three to ten times wider
on 197 rows against 3,000. Firm: degree-2 ridge beats both degree-1 cells by
82 to 84 with standard errors of 20 to 26, and degree-2 OLS is the worst by
204 ± 53. Not firm: whether to penalise at degree 1, 1.47 ± 7.26, which is no
evidence at all.

**What the floor does to the reading.** Hardgoods' best leaves 99 units²
above its floor of 148, so roughly three-fifths of what remains is noise
nobody can remove. Apparel's best leaves 154 above a floor of 142: more than
half of its remaining error is still recoverable in principle, which is the
opposite of a division at its limit.

---

## Notes to self (not memo text)

### Design decisions (mine, session 6)

- **Tuned to the CV minimum**, not by the one-standard-error rule. The brief's
  question 2 asks where the rule "bears on your answer", which is a request
  to discuss it; one criterion across eight cells keeps them comparable; and
  the rule then does real work in question 2. The 1-SE α is computed and
  reported beside the tuned one in `b2_table.csv`.
  - *Correction to an earlier justification of mine.* Tuning to the CV minimum
    does **not** make the ridge and OLS cells comparable. It makes them less
    so: a ridge cell reports the minimum of 25 noisy estimates and so carries
    selection bias, while an OLS cell reports one estimate and carries none.
    Disclosed in the Exhibit B2 footnote. Evidence it is real and small: in
    Hardgoods degree 2, ridge wins the CV comparison by 0.15 and loses the
    test comparison by 1.31.
- **CV MSE is the average of the five fold MSEs**, not one MSE pooled over all
  out-of-fold predictions. The brief asks for the SE across folds, which only
  exists if the five are kept. Apparel's folds are 40/40/39/39/39 so the two
  differ slightly. (A2 pooled, correctly: it had to reproduce the analyst's
  protocol exactly, and AUC is a pairwise rank statistic, so the pooled
  version answers the deployment question of ranking one whole book.)
- **No degree 3.** `DEGREES` offers it and 454 terms on 197 rows would make
  the terms-per-row point vividly, but the brief specifies four models and
  says there are no marks for more. `sweep.py` shows the curve if wanted.
- **Figures and tables to `analysis/outputs/`**, consistent with Part A and
  `CLAUDE.md`, rather than the starter's script-adjacent folders.
- Penalties frozen to `b2_penalties.csv` for B3 to read, so B3 cannot
  accidentally re-tune.

### The test MSE decomposition, and why there is nothing to footnote

Because all ten replicates of a configuration are identical on every feature,
the model emits one prediction per group and the test MSE splits exactly:

    test MSE = (405/450)·σ̂² + mean_g (ȳ_g − ŷ_g)²

Verified to zero in all eight cells (`b2_test_decomposition.csv`). Two
offsetting biases, each exactly σ̂²/10:

- The floor occupies only 405/450 of the test MSE, so subtracting a whole σ̂²
  removes σ̂²/10 too much.
- ȳ_g is itself an average of ten weeks, so it wobbles around the true mean
  with variance σ̂²/10, which inflates the measured gap by σ̂²/10.

They cancel exactly, so **`test MSE − σ̂²` is the unbiased estimate of the
true average squared bias**. Checked: structural part − σ̂²/10 equals
`test MSE − σ̂²` to the cent in all eight cells. The brief's instruction is
exact, not approximate. Nothing to disclose; report it as asked.

(I initially told Orcun the brief's quantity was conservative by σ̂²/10. That
was wrong — it ignored the noise in the replicate-mean yardstick. Recorded
for the process note.)

### CV versus test diverge in opposite directions

| Cell | CV MSE | Test MSE | Direction |
|---|---:|---:|---|
| Apparel degree 1 OLS | 413.53 | 363.58 | test **below** CV |
| Apparel degree 2 ridge | 329.80 | 296.19 | test below CV |
| Hardgoods degree 1 OLS | 336.62 | 398.55 | test **above** CV |
| Hardgoods degree 2 OLS | 233.12 | 246.16 | test above CV |

Two different course ideas, one in each division:

- **Apparel: training-set size.** Each fold fits on about 158 of the 197 rows,
  while the refit gets all 197, a 25% increase. CV is therefore pessimistic
  about the model that actually gets deployed (Handout 2 §3.2, §4.3). The
  effect is large here because 158 → 197 matters when there are 90 terms to
  estimate; in Hardgoods, 2,400 → 3,000 changes almost nothing.
- **Hardgoods: sample representativeness.** The gap runs the other way, so
  training-set size cannot explain it. The 45 replicate configurations were
  chosen by Merchandising Analytics during platform validation, not sampled at
  random from the store-week population, and degree 1 does relatively worse on
  them (test 398.55 vs CV 336.62) than degree 2 does (246.16 vs 233.12). The
  chosen points include regions a linear surface fits badly.

Worth two sentences in §2 if the budget allows; it is not one of the brief's
three questions.

### Arguing against the draft

- **"One specification can serve both" rests on a tie, not a win.** In
  Hardgoods, degree-2 ridge matches degree-2 OLS in CV by 0.15 ± 0.22 and
  *loses* on test by 1.31. The claim is "no worse", not "better", and the
  memo should not overstate it. The honest framing is that standardising on
  degree-2 ridge costs Hardgoods nothing measurable and saves Apparel 84.
- **Selection bias flatters every ridge CV number.** Small where the curve is
  flat and the grid wide, but it is the same direction in all four ridge
  cells. The Apparel degree-2 gain of 288 ± 55 is far too large to be
  explained this way; the Hardgoods ties are exactly where it could matter,
  and it pushes them further towards "tie".
- **The contractor's arithmetic was never wrong.** All four of his figures
  reproduce within half a standard error. His two conclusions were wrong, not
  his fitting. Say so: it is a cleaner criticism and it means B1's
  "avoidable" column needs no restatement.
- **α = 10.0 is the tuned value at degree 1 in both divisions.** The curve
  there is nearly flat — 19 of 25 α values in Hardgoods and 16 of 25 in
  Apparel sit within one SE of the minimum — so the exact value is not
  load-bearing. But both divisions finding the *same* minimum is expected,
  not luck: `stability.py`'s own comment says the two divisions "land in the
  same place" at one degree and not the other, which ours do. (An earlier
  version of this note called the degree-1 argmin "close to arbitrary";
  too strong, corrected.) Consequence for B3, predicted before running it:
  degree-1 ridge and degree-1 OLS should behave almost identically. They do,
  to 0.01 units of sd.
- **Apparel's test MSE beats Hardgoods' at degree 1** (363.58 vs 398.55),
  which would be an odd thing to quote without the floor beside it, since the
  two floors are the same size. Another reason the brief insists on the
  subtraction.
- **197 rows and 5 folds means the SEs are themselves badly estimated.**
  sd over √5 from five correlated numbers is a heuristic (Handout 2 §4.5).
  "Three to ten times wider" is the right order of magnitude; do not quote
  Apparel's SEs to two decimals as though they were precise.

### Numbers used and where they live

| Number | File |
|---|---|
| All eight cells: terms, terms per row, tuned α, CV MSE, SE, test MSE, test − σ̂² | `b2_table.csv` |
| 1-SE α choices (316.2 / 5.62 / 56.2 / 10.0) and endpoint check | `b2_table.csv` |
| CV MSE for each of the 25 α in each ridge cell; 19, 12, 16, 5 α within 1 SE of the minimum | `b2_alpha_curves.csv` |
| Paired differences and their SEs | `b2_differences.csv` |
| Contractor comparison 336.62 / 233.12 / 413.53 / 617.97 | `b2_contractor_check.csv` |
| Exact test MSE split; floor parts 133.30 / 127.83 | `b2_test_decomposition.csv` |
| σ̂² 148.11 / 142.04 | `b1_noise_floor.csv` |
| Tuned penalties for B3 | `b2_penalties.csv` |
