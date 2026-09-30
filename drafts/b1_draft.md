# B1 draft — the noise floor

Draft for the B1 part of memo §2 (to the VP of Merchandising Planning). Every
number is in `analysis/outputs/` from `bash analysis/run.sh` (session 5,
2026-09-29).

**Prose budget.** §2 is one page for B1, B2 and B3 together — roughly 450–500
words. The brief asks B1 for "one or two sentences," so B1's share is about
60 words. Everything else on this page is notes, not memo text.

---

## Exhibit B1 — How much of the error is unavoidable

Source: `analysis/outputs/b1_noise_floor.csv`, `b1_config_check.csv`.
Pooled within-configuration variance over 45 configurations of 10 replicates
per division, so dof = 45 × 9 = 405 in each.

| Division | σ̂² | Approx. SE | σ̂ (units) | Mean units |
|---|---:|---:|---:|---:|
| Hardgoods | **148.1** | ± 10.4 | 12.2 | 111.9 |
| Apparel | **142.0** | ± 10.0 | 11.9 | 111.0 |

Difference (Apparel − Hardgoods) = −6.1, standard error 14.4: **0.42 standard
errors, indistinguishable from zero.**

Against the contractor's own cross-validated figures:

| Division | His best CV MSE | Floor σ̂² | Avoidable | Share that is floor |
|---|---:|---:|---:|---:|
| Hardgoods | 231 (degree 2) | 148.1 | **82.9** | 64% |
| Apparel | 414 (degree 1) | 142.0 | **272.0** | 34% |

*Footnote for the exhibit:* the estimator assumes the twelve recorded fields
are constant inside a configuration. Checked: 0 of 12 fields vary within any
of the 90 configurations, every group has exactly 10 rows, and `units` varies
within every group. The script raises rather than computing a floor if that
fails.

---

## Prose (draft, 62 words)

The unavoidable error is the same size in both divisions: 148 units² in
Hardgoods and 142 in Apparel, a difference of 0.4 standard errors. Apparel
demand is therefore not inherently harder to forecast. What differs is how
much error is left on the table — 83 units² above the floor in Hardgoods
against 272 in Apparel, so roughly two-thirds of Hardgoods' error is
irreducible and only one-third of Apparel's is.

---

## Notes to self (not memo text)

### The two variances, and why only one of them is this number

Handout 3 §1.1 lists "two levels of randomness": the noise ε₀ in the new case,
and the training set 𝒟 and hence the predictor built from it. Equation (2)
keeps them apart —

  Err(x₀) = Bias² + **Var** + **σ²**

where **Var** = E_𝒟[(f̂_𝒟(x₀) − f̄(x₀))²] is how much the *prediction* moves
across training samples (reducible: more data, or a penalty, shrinks it), and
**σ² = Var(ε₀)** is how much the *outcome* moves at a fixed x (irreducible).
B1 measures the second: ten weeks identical on every recorded field, and
`units` still differs. The dartboard in §2.3 — "how spread out the cloud is"
versus "the scatter in the target itself."

### Say "the average irreducible error", not "the irreducible error"

Strictly the floor is Var(ε | X = x), which may depend on where you are in
feature space. Handout 3 §2.2 writes the population version as
E[Err] = Bias²̄ + Var̄ + σ², with bars on the first two terms and none on σ² —
which silently assumes the floor is the same everywhere. `units` is a count,
and Handout 1 §4.7 warns that for counts "the variance typically grows with
the mean," so variance–mean coupling is the default expectation here, not an
exotic worry.

Tested it (`b1_variance_shape.csv`): regressing a configuration's variance on its
mean gives a slope of **+0.657 ± 0.410** in Hardgoods and **+0.103 ± 0.401**
in Apparel. Poisson would be slope 1, constant variance slope 0. Hardgoods is
consistent with *both* — the experiment cannot resolve it, because a single
configuration's variance is estimated from ten observations and carries a
standard error near 70 on a value of 148. Both divisions are mildly
overdispersed relative to Poisson (σ̂² ≈ 1.3 × mean).

Consequences:
- It does **not** threaten the B1 comparison. Both divisions were pooled
  identically, over configurations spanning similar demand ranges
  (Hardgoods 51–176 units, Apparel 80–182), so we are comparing two averages
  computed the same way.
- It **would** matter if σ̂² were used to judge a single prediction at a
  specific store-week: the floor there could be above or below 148.
- So the memo says "the average unavoidable error", and B2's "test MSE − σ̂²"
  is a distance from an average floor, not from a pointwise one.

### An independent check that the arithmetic is right

The brief states, in the B3 section, that a configuration's replicate mean
estimates true demand "to within about σ/√10 ≈ 4 units", without saying which
division. Ours give **3.85** (Hardgoods) and **3.77** (Apparel). That number
was computed by the instructor from data we had not seen, and our estimate
lands on it. Worth one line in the process note.

### Why "test MSE − σ̂²" is the right thing to report (carry into B2)

All ten replicates of a configuration are identical on every feature, so the
model predicts the same value for all ten. The test MSE therefore splits
exactly:

  test MSE = (405/450)·σ̂² + (1/45)·Σ_g (ȳ_g − ŷ_g)²

The second term is the only part a better model could remove — the squared
error of the model against the *true* configuration means. Subtracting σ̂² is
approximately recovering it. Useful to be able to say out loud, and it
explains why the brief calls a raw MSE uninterpretable.

### Arguing against the draft

- **"Identical" is too strong.** A 95% interval on the difference of the two
  floors is roughly ±28 units², up to about 20% of a floor. The defensible
  phrasing is "indistinguishable at this precision", which is still far more
  than enough to sink 414-versus-231.
- **The 45 configurations are not a random sample.** They are points
  Merchandising Analytics chose during the 2025 platform validation. Nothing
  in the dictionary claims they are representative of where the training rows
  live, so the floor is estimated where they looked.
- **The contractor's 231 and 414 are quoted, not reproduced.** B2 refits those
  specifications under the prescribed protocol; if our degree-1 and degree-2
  OLS numbers land far from his, the "avoidable" column above needs restating
  with our own figures. Check this when B2 runs.
- **Same floor does not mean same business difficulty.** Apparel still has 197
  usable rows, and the dictionary says parity is not expected until late 2027.
  "Not inherently harder" is a claim about demand, not about Apparel's
  forecasting problem being easy.

### Numbers used and where they live

| Number | File |
|---|---|
| σ̂² 148.1 ± 10.4, σ̂ 12.2, mean units 111.9 (Hardgoods) | `b1_noise_floor.csv` |
| σ̂² 142.0 ± 10.0, σ̂ 11.9, mean units 111.0 (Apparel) | " |
| dof 405, 45 configs × 10 replicates, both divisions | " |
| Avoidable 82.9 / 272.0; floor share 64% / 34% | " |
| 0 of 12 fields vary within a config; all groups size 10 | `b1_config_check.csv` |
| Difference −6.1, SE 14.4, 0.42 SE | `run.log` |
| Contractor's 336 / 231 / 414 / 618 | quoted from the brief, not computed |
| Variance-on-mean slopes +0.657 ± 0.410, +0.103 ± 0.401; overdispersion 1.32× / 1.28×; config mean ranges 51–176 / 80–182 | `b1_variance_shape.csv` |
