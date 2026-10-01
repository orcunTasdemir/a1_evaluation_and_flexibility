# AI process note — raw material (draft, not the deliverable)

The submitted `ai_process_note.md` is one page max, in my own words, covering
both parts. This file collects the per-session material so nothing is lost.
Append a block per session; condense at the end.

Rubric reminder: "Generic notes score zero. 'Used Claude Code to write the
analysis, reviewed the output, verified it was correct' is a generic note."
Name the specific tasks, the specific rejections with reasons, and the
specific checks.

---

## Session 1 (2026-09-17, Windows) — setup only

**Delegated:** folder audit against the brief's file list; environment
build; smoke test of the supplied loaders under the pinned package versions.

**Changed or rejected:**
- Agent proposed anchoring the `.gitignore` directory patterns to the repo
  root (stock template would have silently dropped an `analysis/lib/`); I
  approved.
- Agent suggested relocating Part B outputs to `analysis/outputs/`; I
  overrode it and directed that the starter scripts' own folder names be
  kept, for easier grading.
- Agent's smoke test left `__pycache__` in the supplied `starter/` folders;
  removed so the supplied folders matched what was issued.

**How numbers were checked:** the 33,340 row count from `wc -l` was checked
against the brief; `dedup_h()` confirmed to take 3,350 → 3,000 before anything
depends on it; supplied files verified unmodified with `git diff HEAD`, not by
assertion.

---

## Session 2 (2026-09-17, macOS) — concept review and A1

**Delegated:** Mac environment build; `analysis/run.sh`, the A1 script and
its README; reading the handouts and locating where each concept lives;
drafting the A1 exhibit and prose; the end-of-session export and notes.

**Changed or rejected:**
- Agent called the label-structure finding (one flagged row per churner,
  always the last) "interesting." I pushed back — obviously the cancellation
  month is the last month. That produced the sharper statement: the
  dictionary's 60-day window would flag two rows per churner, the extract
  flags one, so the label is really "cancellation month," and the leak is a
  same-row timing problem, not a look-ahead into later rows.
- I reframed the A1 "what would have to be true" paragraph around "the data
  dictionary's timing notes would have to be correct, and the columns not
  back-filled from later months." That is now the lead of the paragraph.
- I chose four single-variable columns (days since login, tenure, app opens,
  session minutes) and both row-level and member-level base rates; the agent
  had proposed one column and row-level only.
- I asked whether the leakage evidence (exit-survey / winback cross-tabs)
  was produced by the run. It was not — it came from a one-off check in the
  session. It was added to the script (`a1_column_timing.csv`) before it was
  allowed into the draft.
- Agent replaced `.vscode/settings.json`, which had been pointing VS Code at
  the system interpreter instead of `.venv`; I asked for that fix.
- I asked whether to drop the brief's two-month gap given the label behaves
  like a 30-day window. Decision: keep it — the brief fixes the windows for
  comparability, and the protocol should be safe under the documented
  definition, not the reverse-engineered one.
- Agent had said the cross-validation material was in "Handout 1 §6" per the
  brief; on reading the PDFs it is Handout 2 §4. Recorded the mapping so
  citations in the memo are right.

**How numbers were checked:**
- Base rate predicted at ~9% before running (from the brief); came out 9.29%.
- Member-level 70% reconciled against the row-level rate: a ~4.5%/month
  hazard compounds to ~67% over 24 months, so both are consistent.
- The exit-survey AUC of 0.808 recomputed by hand as coverage plus half the
  ties: 0.616 + 0.5 × 0.384 = 0.808. Same for winback: 0.858.
- The analyst's 0.967 comes from running their script untouched and capturing
  its output, not from retyping the brief's figure.
- One-off diagnostic numbers were accepted only once the script reproduced
  them exactly (dedup count, monthly rates, corporate share, the cross-tabs).
- Everything came out as expected, which the course doc says is the moment to
  slow down; the one unexpected thing (label structure) was found by checking
  rather than trusting the dictionary.

**Would still not bet on:** whether the July–August 2025 churn spike is the
competitor or seasonality — 2024 also peaked in July–September, and two years
cannot separate them. Memo says "coinciding with," not "caused by."

---

## Session 3 (2026-09-20, Windows) — A1 review and finalisation, A2 built

**Delegated:** recap of A1 from the repo after pulling; a five-question
oral-check quiz on A1 and grading of my answers; the 0.50 AUC row and its
prose; the tenure-bucket and corporate-segment diagnostics; the `prep.py`
refactor; `a2_evaluation.py` with the harness check, the column table, the
fold-overlap count and the odds-ratio table; the A1 final prose and the A2
draft; `CLAUDE.md` drafting rule.

**Changed or rejected:**
- I had been reading 90.71% (accuracy) and 0.967 (AUC) as neighbours. Agent
  separated the two scales; I asked for the do-nothing rule's AUC (0.50) as a
  row and a sentence so the VP cannot make the same mistake.
- Agent explained tenure's 0.50 as a possible monotonicity artefact (U-shape
  that AUC cannot see). I asked for the bucket table; it showed churn flat at
  6.7–10.1% in every bucket. Agent's explanation was withdrawn and the draft's
  hedge replaced with the fact. The general point (AUC and a linear logit see
  only monotone signal) kept in notes for the midterm.
- In the quiz I claimed the 2024 summer swing was ~1 point and 2025's ~10.
  Wrong: 6.9 and 8.9 from `a1_base_rate_by_month.csv`. Seasonality is the
  dominant pattern; the competitor claim stays at "coinciding with."
- In the quiz I mixed leaks/fold contamination with the book moving. Agent
  separated them (one makes 0.967 wrong about 2024–25, the other means an
  honest number may not transfer). Kept apart in both drafts.
- Agent offered a "dedup row" in the A2 table. I rejected it: the brief says
  remove duplicates before modelling, so dedup happens before row 0 and is
  footnoted. Kept the agent's raw-file harness check (reproduces 0.967) as a
  wiring test, not an exhibit row.
- "Building data" for rows 0–2: I chose the training window only, so the
  test window is scored once.
- Rejected: bootstrap CI on segment AUCs (not asked for, page budget); a
  single-column reference AUC on the test window (would score the test set a
  second time); computing the alternative change order (not required).
- Agent kept raising `__pycache__` in the supplied folders. I said it has no
  importance. It stopped.
- I asked for odds ratios to understand row 4; agent added them as a
  diagnostic. Agent flagged that `plan_tier` / `monthly_price` are collinear
  and that `app_opens` flips sign versus its single-column direction; both
  kept as cautions, not memo claims.
- The 79.5% fold-overlap figure came from a scratch run. I asked whether it
  was in the run; it was not; it was added to the script before it went in
  the draft.
- In my row-0 reading I called 0.968 "better than 0.967." Wrong: same number,
  different rows. Sentence replaced with "the leak dominates everything else."
- In my order-independence answer I said dedup made member overlap rare.
  Wrong: 79.5% of members straddle folds after dedup. The real reason change
  2 barely moves is that the admissible columns cannot identify a member.
- `CLAUDE.md` "never write the judgment" relaxed to match policy line 47:
  agent drafts on request; judgments stated by me first.

**How numbers were checked:**
- Harness re-ran the analyst's exact protocol on the raw file and printed
  0.967 before any change was measured.
- The `prep.py` refactor was accepted only after all eight A1 outputs were
  diffed byte-for-byte against a pre-refactor snapshot.
- Raw base rate 0.0912 reconciled with deduped 0.0929: (2,939 + 101) / 33,340.
- Corporate share of test rows (19%) and churners (8%) computed by hand from
  `a2_table.csv` and stated as arithmetic in the provenance table.
- Rough SE for the corporate AUC (~0.05 with 34 positives) is a hand
  estimate and is labelled rough; it is in notes, not the memo.
- Every number in both drafts is listed with its file in a provenance table.

**Would still not bet on:** why corporate ranks at 0.404 (contract-driven
churn not in the columns is a hypothesis); whether the 12-column model beats
a single column on the test window (not computed, to honour score-once).


---

## Session 4 (2026-09-29, macOS) — A3, the targeting decision

**Delegated:** the A3 script (threshold derivation, calibration check and
correction, value exhibit, monthly split, offer-quality table, value curve and
figure); the cross-machine reproducibility check; verifying A2's partitions
against the brief's window table; the A3 draft.

**Changed or rejected:**
- I declined the agent's proposal to add window-compliance assertions to
  `a2_evaluation.py`. A2 is run and its questions are answered; the assertions
  only guard against future edits.
- The agent recommended skipping the monthly split to save words, and I
  agreed. It then turned out to be the clearest evidence that the value is
  unstable — October $48, November $810, December -$6 — so it went in after
  all. A pre-commitment revisited because the data disagreed with it.
- The agent argued that fitting the calibration correction on September
  (10.8% base rate) would over-correct for a lower-rate test window. That was
  wrong and it said so: the raw model under-predicts on the test window too,
  because the test book is more corporate and the model scores corporate low.
- I chose one offer = one member-month over per-member accounting, and fixed
  the shape of the recommendation (scope to non-corporate, plus a tripwire)
  before any dollar figure was computed.
- I rejected scoring the test window with the analyst's *model* for a
  like-for-like dollar comparison: it would be a second scoring of the test
  set, and session 3 had already set the norm against that.
- I specified the tripwire in dollars — realised value per offer — rather than
  AUC, after seeing that the model's top-scoring offers claim 39.6% and
  deliver 27.9%, so a ranking statistic can hold steady while the programme
  goes underwater.

**How numbers were checked:**
- Cross-machine: re-ran the whole pipeline on the Mac against outputs
  committed from Windows. `a2_table.csv` and all six A1 outputs were
  byte-identical; `a2_test_scores.csv` differed by at most 4e-14 in `p_churn`,
  and the same 203 rows cleared the threshold on both machines, so no dollar
  figure depends on the hardware.
- The threshold is derived two ways in code — 18/(240 x 0.35) and the general
  form C_FP/(C_FP+C_FN) — with an assertion that they agree, and both read the
  constants from `starter/load.py` rather than being typed in.
- The vectorised value calculation is asserted row by row against the supplied
  `offer_value()` helper, so the economics come from the starter module.
- A2's partitions were verified from the data (months present in each, no
  overlap, all 24 accounted for) rather than from reading the code.
- The calibration decision was made on validation evidence *before* any dollar
  figure was computed, and it cost $30 — raw scores return $882 against $852
  corrected. Deciding afterwards would have selected the raw scores.
- The figure's annotation disagreed with the exhibit ($834 against $852)
  because the curve grid did not pass through the derived threshold. Caught by
  reading the figure against the table; fixed by putting t* and 0 in the grid.

**Would still not bet on:** the corporate dollar line (-$78 on nine offers and
one churner); the quartile pattern below the top quartile (~15 churners each);
and that $852 transfers to April-June, which runs a lower base rate on a book
forecast at 35% corporate.

---

## Session 5 (2026-09-29, macOS) — B1, the noise floor

**Delegated:** the B1 script (pooled within-configuration variance, its
standard error, the verification that the twelve fields really are constant
within a configuration, and the test of whether the floor is level-dependent);
reading Handout 3; the B1 draft.

**Changed or rejected:**
- I asked what we actually test on — `test_extract()` or the replicates —
  before letting any of Part B be built on an assumption. They are the same
  object; the agent verified it with `.equals()` rather than telling me from
  the docstring.
- I asked for the "average unavoidable error" caveat to go into the draft,
  and the agent had computed the supporting slope test as a one-off. It went
  into `b1_noise_floor.py` before it was allowed into the draft — the same
  rule I applied to the leakage evidence in A1.
- I pushed back on the claim that the one-standard-error rule needs
  cross-validation, pointing out that scoring the five fold-models on a
  single held-out set would also give a spread. It would — but it measures
  the spread of the *predictor* with the evaluation data fixed, which is the
  Var term of the bias-variance decomposition and is what B3 measures with
  bootstrap resamples, not the uncertainty of the risk estimate that the rule
  needs.
- I asked for the A2 "no decision was made from data" claim to be stated with
  both caveats — that A3 *did* use the validation month, and that we had seen
  the two dropped columns' univariate AUCs in A1 before finalising A2 — so
  the write-up shows the rebuttal as well as the argument.

**How numbers were checked:**
- The pooled variance is computed two ways in the script — directly from the
  definition, and as the mean of the per-group sample variances — with an
  assertion that they agree when group sizes are equal.
- The estimator's assumption is verified, not trusted: 0 of 12 recorded
  fields vary within any of the 90 configurations, every group has exactly
  ten rows, and the script raises rather than computing a floor if that fails.
- **Independent check:** the brief states, in the B3 section, that a
  configuration's replicate mean estimates true demand to within about
  sigma/sqrt(10) ~ 4 units, without naming a division. Ours give 3.85 and
  3.77. That figure was computed by the instructor from data we had not seen,
  and our estimate lands on it.
- The heteroscedasticity test was reported as inconclusive rather than spun:
  a configuration's variance is estimated from ten rows and carries a standard
  error near 70 on a value of 148, so Hardgoods' slope of +0.657 +/- 0.410 is
  consistent with both a Poisson-like law and a constant floor.

**Would still not bet on:** that the 45 configurations are representative of
where the training rows live — they are points Merchandising Analytics chose
during platform validation, and nothing claims they are a random sample; and
the contractor's 231 and 414, which are quoted from the brief and not yet
reproduced under our own protocol (B2 will say).

---

## Session 6 (2026-10-01, Windows) — B2 and B3. Part B complete.

**Delegated:** `b2_models.py` and `b3_stability.py`; the explanations of
ALPHA_GRID, pooling vs averaging, the test-MSE decomposition, bias/variance
at a query point; both drafts; the session close.

**Changed or rejected:**
- I chose to tune to the CV minimum rather than by the 1-SE rule, reading the
  brief's "note where the rule bears on your answer" as a request to discuss
  it. My stated reason was that it keeps the ridge and OLS cells comparable;
  the agent corrected me — it does the opposite. A ridge cell reports the
  minimum of 25 noisy estimates and carries selection bias; an OLS cell
  reports one estimate and carries none. I kept the decision and had the
  asymmetry disclosed in the Exhibit B2 footnote instead. Evidence it is real
  and small: Hardgoods degree 2, ridge wins the CV comparison by 0.15 and
  loses the test comparison by 1.31.
- Agent told me three times that the brief's `test MSE − σ̂²` was conservative
  by σ̂²/10, because the "exact" gap against replicate means was larger. I
  pushed for an explanation I could follow, and the explanation is what broke
  it: the replicate mean is itself an average of ten weeks, so it wobbles by
  σ̂²/10 and inflates the measured gap by exactly the amount the subtraction
  over-removes. The two cancel; the brief's quantity is unbiased. Confirmed
  by a 20,000-dataset simulation with known truth: target 99.92, replicate-mean
  gap 114.19 (overstates by 14.27 ≈ σ²/10 = 14.4), brief's quantity 99.79.
  Nothing about it went in the memo, because there was nothing to disclose.
- Rejected degree 3 (no marks for more models) and a bootstrap CI on the B2
  cells (not asked, page budget).
- For B3 I chose the wrapper approach over editing or copying the supplied
  `stability.py`, so the instructor's loop runs as issued and `git diff`
  against the supplied folders stays empty.
- I asked for signed bias alongside mean absolute. It earned its place:
  Hardgoods degree-1 OLS has per-point biases +21.01, −15.06, −1.89, so its
  signed mean of +1.35 would have made a rigid model look unbiased.
- Agent predicted before running B3 that Apparel's problem would be variance.
  Half wrong: true for degree-2 OLS (variance 664 of 1,139 units²), but the
  penalty converts it, and Apparel's best model is 85% bias (293 vs 53). That
  changed §2's conclusion from "penalise Apparel" to "the penalty has already
  done its work; what remains needs more Apparel history."
- Agent's B2 note called the degree-1 tuned α "close to arbitrary". The
  starter's own comment says the two divisions land on the same α at one
  degree, which ours do (10.0 at degree 1), so it is expected, not luck.
  Note softened.
- Overrode my own session-1 decision to keep the starter's `b3_outputs/`
  folder name: everything else writes to `analysis/outputs/`, and one
  consistent location is worth more than fidelity to a folder name.

**How numbers were checked:**
- Our refits of the contractor's four specifications reproduce his quoted
  336 / 231 / 414 / 618 as 336.62 / 233.12 / 413.53 / 617.97, all within half
  a standard error. So his arithmetic was never wrong; his conclusions were.
- Two checks the instructor embedded in the materials, both passed: σ̂/√10 ≈ 4
  units (ours 3.85 and 3.77), and `stability.py`'s hint that the tuned
  penalties coincide at one degree and not the other (ours 10.0/10.0 at
  degree 1, 0.316/3.162 at degree 2).
- The test-MSE identity (floor part + structural part = test MSE) checks to
  zero in all eight cells.
- B3's penalties are read from `b2_penalties.csv` rather than retyped, so they
  cannot drift from B2 or be re-tuned inside the resamples.
- The bias²/variance split was computed in conversation first; it was moved
  into `b3_stability.py` before any of it was allowed into a draft.
- B3's 345.7 against B2's 154.15 for the same cell looked like a
  contradiction. Decomposed it instead: 154.2 over all 45 configs, 257.3 over
  the three query points with the same single fit, 345.7 once the fits are
  bootstrap resamples holding only 62.5% distinct rows. Two stacked changes,
  not a conflict. Recorded as a rule: B2 for levels, B3 for mechanism.
- `a2_test_scores.csv` changed when re-run on Windows after the Mac. Verified
  it is floating-point only: max change 4e-14 and the same 203 rows clear the
  threshold, so no dollar figure moves.

**Would still not bet on:** whether the three query points' per-point bias
pattern (both divisions over-predicting low demand, under-predicting high)
generalises across feature space. Three points cannot establish it.

**End-of-session verification (2026-10-01).** Rather than assert the
submission reproduces, I had it tested: a fresh `git clone` into an empty
directory with no `.venv`, outputs wiped, `bash analysis/run.sh` run with
only `python3` on PATH. Exit 0 in 12.7 seconds; all 31 output files came
back byte-identical to the committed ones and `run.log` matched once paths
and the Python patch version were stripped. Separately, a script checked
every numeric token in the B1-B3 prose and exhibits against the output
files: 242 tokens, 0 unaccounted, with the brief's quoted contractor
figures and hand-computed percentages listed explicitly as exceptions.
