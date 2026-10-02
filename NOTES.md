# Working notes, IDS 575 Assignment 1

Append one section per work block. Read this first when switching machines.

---

## Session 1 — 2026-09-17 (Windows 11 machine). Setup only, no analysis.

Transcript: `sessions/claude-code/a1-session-1.jsonl` (raw) and
`a1-session-1.txt` (readable).

**`/export` does not work in the VS Code extension** and the CLI has no export
subcommand. Used Option A from the course sheet (the raw JSONL) plus
`sessions/render_transcript.py` to reproduce the readable form. Documented in
`sessions/README.md`. If a future session runs in the terminal CLI rather than
the extension, `/export` may work there; either route is fine.

### What was done

- Audited the folder against the brief's "What is in this folder" list. All nine
  supplied files present, nothing missing.
- Built the Python environment. `.venv` at the repo root, pinned versions in
  `requirements.txt`. Nothing was installed before this; the system Python had
  only pip and setuptools.
- Fixed `.gitignore`. The stock Python template ignored `lib/`, `var/`, `build/`,
  `dist/`, `target/`, `instance/`, `cover/`, `htmlcov/` at any depth, so an
  `analysis/part2/lib/` would have been dropped from the submission silently.
  Those are now anchored to the repo root. Added an exception so run logs under
  `analysis/outputs/` can be committed.
- Confirmed the supplied folders are untouched. `git diff HEAD` against
  `part1_northline` and `part2_cascade` is empty. The starter `OUT` paths are as
  shipped. `__pycache__` folders created by the smoke test were deleted.

### Environment

Python 3.11.9 on this machine. Recreate on the Mac with Python 3.11:

    python3.11 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt

`.venv` is git-ignored and does not travel. `requirements.txt` does.
Versions are pinned so numbers reproduce across the two machines.

### Numbers produced, with provenance

All from `wc -l` on the CSVs and from a smoke-test script run under the new
`.venv` that imported the starter modules and printed shapes only. No data file
contents were read into the session.

| Quantity | Value | Source |
|---|---|---|
| `member_months.csv` rows | 33,340 | `wc -l`; matches the brief's stated figure |
| `member_months.csv` shape | (33340, 18) | `part1_northline/starter/load.py::load_raw()` |
| `division_h.csv` shape | (3350, 15) | `part2_cascade/starter/load.py::load_h()` |
| `division_h.csv` after `dedup_h()` | (3000, 15) | same, so 350 duplicate store-weeks |
| `division_a.csv` shape | (197, 15) | `load_a()` |
| `replicates.csv` shape | (900, 16) | `load_replicates()` |
| Folds / alpha grid / queries | 5 / 25 / H, A | `make_folds()`, `ALPHA_GRID`, `QUERY_CONFIGS` |

These are structural checks, not results. Nothing here is a finding for the memo.

### Open questions for next session

1. **Where Part B outputs land.** The starters write to `sweep_outputs/` and
   `b3_outputs/` beside the script. Decision made: keep those folder names. Not
   yet decided whether they sit at `analysis/part2/<name>/` or
   `analysis/outputs/<name>/`. My call to make at the start of Part B.
2. **Running `sweep.py` in place would write into `part2_cascade/starter/`.**
   Run it from a copy under `analysis/part2/` instead, to keep the supplied
   folder clean.
3. **Handouts.** Pull from Canvas into `handouts/`: Handout 1
   (`lecture01_learning_from_data.pdf`), Handout 2 (Lecture 2, logistic
   regression), Handout 3 (`lecture03_bias_variance.pdf`), Handout R1
   (`handoutR1_reading_a_metric.pdf`). Undecided whether to track or ignore them.
4. **Not started yet:** `analysis/README.md`, `ai_process_note.md`, the memo.

### Next block

A1, the baselines. Base rate, the trivial rule's accuracy and whether accuracy
suits this decision, at least one single-variable AUC, the analyst's 0.967
beside them. Do-nothing answer before any modelling.

---

## Session 2 — 2026-09-17 (macOS laptop). Mac environment, concept review, A1 done.

Transcript: `sessions/claude-code/a1-session-2.jsonl` (raw) and
`a1-session-2.txt` (readable), exported the same way as session 1.

### What was done

- Built the Mac environment: Homebrew `python@3.11` (3.11.16), `.venv` from
  `requirements.txt`. Package versions identical to Windows. Smoke test
  reproduced session 1's shapes exactly.
- `.vscode/settings.json` now selects `.venv` (was pointing at system Python).
  `handouts/` un-ignored and tracked; five PDFs added from Canvas.
- Read Handouts 1, 2 and R1 in full. **The brief's section numbers for
  "Handout 1 §6 / §6.5 / §7.2 / §7.3–7.4" are actually Handout 2 §4 / §4.5 /
  §5.2 / §5.3–5.4** (`lecture02_evaluating_models.pdf`). Handout 1 stops at §5.
  Handout 2 Exercise 7 (leakage triage) and Exercise 10 (baselines) map almost
  directly onto A2's column decision and A1.
- Concept review before any code: risk vs empirical risk vs loss, K-fold CV
  and what it estimates (risk of the procedure), the three data roles, why CV
  may choose model classes (H2 §3.1, Ex. 1) but the winner's CV score is
  optimistic, one-SE rule, AUC as a pairwise ranking probability, the
  cost-derived threshold t* = C_FP/(C_FP+C_FN) (R1 §3 eq. 4).
- Wrote `analysis/run.sh` (one command), `analysis/README.md`,
  `analysis/part1/a1_baselines.py`. Run time ~15 s. Runs the supplied
  `analyst_model.py` unmodified and captures its output.
- Drafted `drafts/a1_draft.md`: Exhibit A1, ~180 words of prose, notes to self,
  argue-against list, provenance table.

### Design decisions made (mine)

- Clean = `month_key()` normalise, then `drop_duplicates()` on all columns.
  No cleaned CSV is written; cleaning is in code, logged to `a1_cleaning.txt`.
- Base rate reported row-level (headline, matches analyst's unit) and
  member-level (context).
- Single-variable AUCs for four columns, directions fixed from the dictionary
  before computing: days_since_last_login (+), tenure_months (−),
  app_opens_last_30d (−), avg_session_minutes (−).
- Keep the brief's two-month gap even though the label behaves like a 30-day
  window (see below): the brief fixes the windows, and the protocol should be
  safe under the documented definition.

### Numbers produced, with provenance (all from `bash analysis/run.sh`)

| Quantity | Value | File |
|---|---|---|
| Duplicates removed (all 2025-03) | 1,695 → 31,645 rows | `a1_cleaning.txt` |
| Base rate, rows | 0.0929 (2,939 / 31,645) | `a1_baselines.csv` |
| Base rate, members ever churning | 0.6998 (2,939 / 4,200) | " |
| Accuracy of "no churn" | 0.9071 | " |
| AUC days_since_last_login / tenure / app_opens / avg_session | 0.6464 / 0.5017 / 0.6476 / 0.6810 | " |
| Analyst's CV AUC as printed | 0.967 (AP 0.899, threshold 0.267, $19,774/qtr) | `analyst_model_output.txt` |
| Base rate 2024 / 2025 | 0.1061 / 0.0862; corporate share 0 / 0.101 | `a1_base_rate_by_year.csv` |
| Monthly base rate range | 0.053 (2025-04) to 0.142 (2025-08); 2024 Jul–Sep 0.124–0.133 | `a1_base_rate_by_month.csv` |
| Corporate share 2025-12 | 0.202 | " |
| Book size | peaks 2,119 rows (2025-07), 1,376 by 2025-12 | " |
| exit_survey_started = 1 | 1,810 rows, all churners, all last rows, 61.6% of churners, AUC alone 0.808 | `a1_column_timing.csv` |
| winback_offer_sent = 1 | 3,533 rows, 2,239 churners (63.4%), 76.2% of churners, AUC alone 0.858 | " |

### Findings not in the brief

- **Label structure.** Every churner has exactly one flagged row and it is
  always their last row (2,939 of 2,939). A literal 60-day window would flag
  two. In practice `churn_next_60d = 1` means "cancellation month." Evidence:
  `exit_survey_started` is 1 only on flagged rows.
- **Leakage mechanism is concrete.** The row is scored at the start of the
  month; `exit_survey_started` and `winback_offer_sent` record events during
  or after it. On 1 April 2026 both will be 0 for everyone.

### Open questions / next session (A2)

1. **First task:** move the cleaning into `analysis/part1/prep.py` with a
   `load_clean()` so A2 and A3 clean identically. Refactor `a1_baselines.py` to
   use it and confirm numbers unchanged.
2. **A2 design, to decide before coding:** import `analyst_pipeline()` from the
   supplied `analyst_model.py` so each row changes protocol only; the order of
   the four changes; which columns are admissible (argue every column from the
   dictionary's timing notes, kept and dropped); how grouped CV is done
   (GroupKFold vs StratifiedGroupKFold — my call).
3. Handout 3 (Part B) and R2 not yet read.
4. Part B output-folder question from session 1 still open.
5. `ai_process_note.md` and `memo.md` not started. Raw material for the
   process note is kept per session in `drafts/ai_process_note_draft.md`;
   append a block each session. `drafts/a1_draft.md` exists.

---

## Session 3 — 2026-09-20 (Windows 11 machine). A1 reviewed and finalised, A2 built.

Transcript: `sessions/claude-code/a1-session-3.jsonl` and `.txt`. This is the
same VS Code conversation as session 1, continued, so the file contains
session 1 as its first part. Not sliced (course doc: do not curate).

### What was done

- Pulled sessions 2 from the Mac. Recap of A1 from the repo, then a
  five-question quiz; my answers and the corrections are in
  `drafts/ai_process_note_draft.md`.
- A1 finalised: do-nothing AUC 0.50 row added; tenure's 0.50 checked with a
  bucket table (flat, not a monotonicity artefact); corporate segment
  diagnostic added; prose rewritten with leaks/contamination kept separate
  from the book moving. `drafts/a1_draft.md`, 499 words.
- `analysis/part1/prep.py` with `load_clean()`; `a1_baselines.py` refactored
  to use it; all eight outputs byte-identical before and after.
- `analysis/part1/a2_evaluation.py` built and in `run.sh`. Harness check,
  rows 0–4, column table, fold overlap, odds ratios, test scores saved.
- `drafts/a2_draft.md`: exhibits A2, A2b, A2c and prose (552 words).
- `CLAUDE.md`: Drafting section added (policy line 47).
- `run.sh` sets `PYTHONDONTWRITEBYTECODE=1`. Harmless; not important.

### Design decisions made (mine)

- Dedup before row 0 (brief: "remove the duplicates before modelling"). The
  "as printed" 0.967 line is the analyst's own output; a harness check on
  the raw file reproduces it and is not an exhibit row.
- Rows 0–2 cross-validated on the training window only (≤ 2025-06), so the
  test window is scored exactly once, at row 3. Row 4 splits row-3 scores.
- Order 1→2→3→4: 2 must precede 3 (no folds after 3); 3 as late as possible.
- Columns: 12 kept, `winback_offer_sent` and `exit_survey_started` dropped,
  from the dictionary's timing notes; `plan_tier`/`monthly_price` flagged as
  a reading. `acquisition_channel` kept.
- `StratifiedGroupKFold(5, shuffle=True, random_state=0)` for change 2.
- Validation month unused in A2 (no choice made from data). No bootstrap CI.
  No single-column reference on the test window. No alternative-order run.

### Numbers produced, with provenance (all from `bash analysis/run.sh`)

| Quantity | Value | File |
|---|---|---|
| Do-nothing AUC | 0.50 | `a1_baselines.csv` |
| Churn by tenure bucket | 6.7% (month 2) to 10.1% (months 6–8), all buckets | `a1_churn_by_tenure.csv` |
| Corporate: members / rows / churn | 328 / 2,130 / 3.1% vs other 9.7% | `a1_corporate_segment.csv` |
| Corporate in training window | 533 rows, tenure ≤ 6 | " |
| Building window | 21,031 rows, 1,767 churners, 3,648 members | `a2_table.csv`, `run.log` |
| Test window | 4,556 rows, 408 churners, 1,669 members | " |
| Harness check on raw file | 0.967 | `run.log` |
| A2 rows 0 / 1 / 2 / 3 | 0.9679 / 0.7475 / 0.7466 / 0.6435 | `a2_table.csv` |
| A2 row 4 corporate / other | 0.4044 (860 rows, 34 churners) / 0.6406 (3,696, 374) | " |
| Test churners by month, corporate / other | Oct 10/148, Nov 8/127, Dec 16/99 | `run.log` |
| Members in 2+ folds under random split | 2,899 of 3,648 (79.5%); 613 single-row | `a2_fold_overlap.csv` |
| Odds ratios: non-corporate channels vs corporate | 4.3 / 4.1 / 4.1 | `a2_odds_ratios.csv` |
| Odds ratios: elite / sessions per SD / minutes / price / login / tenure | 0.38 / 0.57 / 0.61 / 1.38 / 1.33 / 0.85 | " |
| Sessions per unit | 0.88 per session | " |
| 2024 vs 2025 monthly swing | 6.4→13.3 (6.9 pts) vs 5.3→14.2 (8.9 pts) | `a1_base_rate_by_month.csv` |

Hand arithmetic, stated as such in the drafts: corporate = 860/4,556 = 19% of
test rows and 34/408 = 8% of test churners; raw base rate (2,939+101)/33,340
= 0.0912.

### Findings this session

- Tenure is flat in churn. Not a U-shape; binning would not help.
- Change 1 costs 0.22, change 2 costs 0.001, change 3 costs 0.10. Change 2 is
  near zero because the admissible columns cannot identify a member and a
  linear model cannot build identity from shared attributes, not because
  overlap was rare (79.5% of members straddle folds).
- Row 3's drop is the cost of time, not of novelty: rows 0–2 were also on
  unseen rows; row 3's unseen rows are later.
- Corporate ranks at 0.404 on 34 churners. The model's largest term is the
  channel itself (~4× odds for non-corporate). The pooled 0.644 is really the
  "other" 0.641.

### Open questions / next session (A3)

1. **A3 design, to decide before coding.** The threshold is derived from $18
   and $66 (t* = 18/84 = 0.214 by the expected-value argument; derive it in
   the memo, do not quote). Then: what population "offer everyone" is priced
   over (all test rows? per month? per quarter as the analyst did?); whether
   value is reported per month, per quarter, or for the three test months as
   given; by segment with the 34-churner caveat; whether calibration is
   checked anywhere before applying t* (the validation month is available
   and unused). A3 reads `a2_test_scores.csv` and must not refit or rescore.
2. The analyst's threshold 0.267 was a grid search on out-of-fold scores,
   i.e. chosen by looking at data. Ours will not be. Say so in the memo.
3. Test window is Oct–Dec (base rate 8.4–9.5%); deployment is Apr–Jun
   (5.3–7.1% in 2025). The dollar estimate depends on churners available to
   find. Carry into A3's caveats.
4. `winback_offer_sent` is 1 on 1,294 non-churners: it is the intervention
   the programme proposes, so some historical outcomes are post-treatment.
   Worth one line in A3.
5. Prose budget: A1 499 + A2 552 words already; §1 is two pages. Trim after
   A3 exists. Candidates: A1's loss sentence (A3 says it better), corporate
   and seasonality figures to exhibit footnotes.
6. Part B untouched. Handout 3 and R2 not yet read. Output-folder question
   from session 1 still open.
7. `ai_process_note.md` and `memo.md` not started; raw material per session
   is in `drafts/ai_process_note_draft.md` (session 3 block added).

---

## Session 4 — 2026-09-29 (macOS laptop). A3 built and drafted. Part A complete.

Transcript: `sessions/claude-code/a1-session-4.jsonl` and `.txt`.

### What was done

- Pulled session 3 from Windows. **Cross-machine reproducibility verified**:
  re-running everything on the Mac left `a2_table.csv` and all six A1 outputs
  byte-identical. Only `a2_test_scores.csv` moved, by at most 4e-14 in
  `p_churn` (ARM vs x86 floating point), and the *same 203 rows* cleared the
  threshold on both machines, so no dollar figure depends on the laptop.
  `run.log` differs only by Python patch version and path separators.
- Verified A2's partitions against the brief's window table from the data, not
  from reading the code: fitted on 2024-01..2025-06 (18 months), scored on
  2025-10..12 (3 months), 2025-07/08/09 in neither, no month in both.
- `analysis/part1/a3_decision.py` written and added to `run.sh`. Full run is
  ~12 s. Threshold derivation, calibration check and correction, value
  exhibit, monthly split, offer-quality table, value curve and figure.
- `drafts/a3_draft.md`: recommendation, Exhibits A3a-A3d, prose (448 words),
  notes, argue-against list, provenance table, trimming candidates.

### Design decisions made (mine)

- One offer = one member-month (matches the monthly programme and the brief's
  per-offer economics; per-member accounting has no honest answer to "which
  month did the offer happen in", since a churner has only one flagged row).
- Quarter as the reporting period. Monthly split added afterwards once it
  proved informative — I had decided to skip it.
- Priced t* against offer-everyone, no programme, and the analyst's 0.267.
  Declined to score the test window with the analyst's *model*: that is a
  second scoring, and A2 set the norm against it.
- Calibration: checked on the validation month, and corrected there with
  Platt scaling. **The verdict was set from validation evidence before any
  dollar figure existed.** It cost $30.
- Value curve reported (re-reads the same scores, no new scoring).
- Recommendation shape (scope to non-corporate + dollar tripwire) chosen
  before the numbers were computed.
- Declined to add window-compliance assertions to `a2_evaluation.py`: A2 is
  run and answered.

### Numbers produced, with provenance (all from `bash analysis/run.sh`)

| Quantity | Value | File |
|---|---|---|
| Threshold t* | 0.2143 = 18/84, two routes agreeing | `a3_threshold.txt` |
| Value at t*, quarter | $852 (242 offers, 62 to churners, 180 wasted) | `a3_value.csv` |
| Standard error of that total | $572, i.e. 1.5 SE from zero | `run.log` |
| By segment | corporate -$78 (9 offers, 1 churner); other +$930 (233, 61) | `a3_value.csv` |
| Offer to everyone | -$47,736 (4,556 offers, 408 churners) | " |
| No programme | $0 | " |
| At the analyst's 0.267 | $828 (108 offers, 33 churners) | " |
| Monthly at t* | Oct $48 (114 offers, 21.9%); Nov $810 (81, 33.3%); Dec -$6 (47, 21.3%) | `a3_by_month.csv` |
| First vs repeat contact | $3.97 vs $1.66 per offer; 195 vs 47 offers | `a3_offer_quality.csv` |
| Top-quartile over-prediction | claims 39.6%, delivers 27.9% (61 offers) | " |
| Q1 just above t* | 22.2% claimed, 18.0% observed, -$2.85 per offer | " |
| Validation calibration | slope 0.788, intercept -0.219; under-predicts in 8 of 10 bins; val AUC 0.695 | `a3_calibration.csv`, `run.log` |
| Calibration sensitivity | raw scores give $882 on 203 offers | `run.log` |
| Curve peak | $1,098 at threshold 0.236; not selecting cost $264 | `a3_value_curve.csv` |

Hand arithmetic, stated as such: break-even precision = t* = 21.43%, and
value per offer = 84 x (precision - 0.2143); quarter precision 25.6%.

### Findings this session

- **The margin is thin, not the ranking.** Value per offer is $3.52 against a
  break-even precision of 21.4% on a 9% base rate. Two of the three test
  months are at or below break-even; the quarter's $852 is essentially
  November. With 47-114 offers a month those differences are mostly noise,
  which is the finding: the programme sits close enough to zero that ordinary
  variation straddles it.
- **The threshold was not the analyst's main error.** Their grid-searched
  0.267 on honest scores gives $828 against our derived $852. The $19,774 came
  from leaked columns and a shuffled evaluation, not from the cut point.
- **The model overstates the members it selects.** Top-scoring quartile claims
  39.6% and delivers 27.9% — selecting the top of a noisy score. This is why
  the tripwire is a dollar figure, not AUC: AUC can hold while calibration
  drifts and the cut point stops meaning what it meant.
- A fixed threshold is self-regulating *if* the probabilities are honest, so
  a lower April base rate should mean fewer offers rather than worse ones.
  The exposure is miscalibration under drift, not the base rate itself.

### Open questions / next session (Part B)

1. **Part B is untouched and worth 35 points.** Handout 3 and R2 unread.
   Output-folder question from session 1 still open (`sweep_outputs/` and
   `b3_outputs/` under `analysis/part2/` vs `analysis/outputs/`).
2. **Prose budget is over.** A1 499 + A2 552 + A3 448 = 1,499 words for a
   two-page §1 (~1,000-1,200). Trimming candidates are listed at the end of
   `drafts/a3_draft.md`; roughly 450 words need to come out.
3. `memo.md` not started. `ai_process_note.md` not started; per-session raw
   material is in `drafts/ai_process_note_draft.md` (session 4 block added).
4. Deadline Thursday 1 October, 6:00 PM Central.

### Two structural points for the write-up (settled end of session 4)

- **The memo is not the drafts stapled together.** One document, two
  sections: §1 to the Northline VP (A1-A3, max 2 pages of prose, Exhibits
  A1-A3), §2 to the Cascade VP (B1-B3, max 1 page, Exhibits B1-B3). Each
  section *leads with its recommendation* and works backwards through the
  evidence. The drafts are organised by rubric item so nothing is lost; the
  memo has to be reorganised by argument. Some of the 450-word trim comes
  free from that, since the three A-drafts repeat context for each other.
  Also check the exhibit count: eight labels exist (A1, A2, A2b, A2c,
  A3a-A3d) against the brief's "Exhibits A1-A3"; sub-lettering is fine but
  four under A3 is probably one or two too many.
- **`ai_process_note.md` is one page maximum for both parts**, stated in
  README, the submission checklist and course doc 01, and length limits are
  "stated per assignment, and enforced". That is ~500 words against the
  1,927 now in `drafts/ai_process_note_draft.md`, with Part B still to add.
  Treat that file as a quarry, not a first draft; it is not submitted. The
  strongest items are the ones where I corrected the agent, not the ones
  where it built something. Write it last, in one pass, covering both parts.

### For office hours (added session 5, before 2026-09-30)

Four questions, ranked by how much they could move a grade (the fourth added
session 8).

1. **The "building data" ambiguity in A2.** The brief says rows before change
   3 are "cross-validated on the building data" without defining the phrase.
   We read it as the training window (months <= 2025-06, 21,031 rows). The
   alternative reading is everything that is not test (<= 2025-09, including
   the two gap months and the validation month). If the second reading is
   intended, rows 0-2 change and `a2_evaluation.py` needs a one-line edit and
   a re-run -- not a rebuild.
2. **Does corroboration count as selection?** We dropped `winback_offer_sent`
   and `exit_survey_started` on provenance grounds from the dictionary's
   timing notes, but had already computed their univariate AUCs in A1. Does
   having seen those numbers count as choosing from the data, and does it
   oblige us to use the validation month? Written up in `drafts/a2_draft.md`
   under "On 'no choice was made by looking at data'".
3. **A3's use of the validation month.** We used Sep 2025 to check and then
   correct calibration (Platt). We read that as squarely within "any choice
   made by looking at data", but it is the only fitted correction in Part A
   and is worth one sentence of confirmation.
4. **The label is not a 60-day window** (added session 8, 2026-10-02).
   Brief and dictionary both define `churn_next_60d` as termination within 60
   days of the end of `snapshot_month`, and the dictionary's maturity logic
   uses the same window. The delivered file flags exactly one row per churner,
   their cancellation month, never the one or two months before. Measured:
   label base rate 9.29% (the figure the brief quotes); one-month cancellation
   rate 9.37%; true rolling 60-day rate 17-20% depending on the denominator.
   So the label behaves like a one-month indicator. Which definition is
   authoritative? Nothing in my work depends on it: numbers come from the
   column, the 21.4% threshold comes from the cost ratio and not the base
   rate, and the two-month gap is required under the documented definition and
   merely conservative under the delivered one. Unlike NLF-2231, NLF-2198 and
   the two post-scoring columns, this discrepancy has no ticket and no note,
   so it may be a generation artefact rather than planted.

Related concept settled this session, in case it comes up: cross-validation
carries **two opposing biases**. Fitting on (K-1)/K of the data makes every
candidate's estimate pessimistic for the final refit model (Handout 2 s3.2,
s4.3). Selecting the best of several noisy estimates makes the *winner's*
reported score optimistic (Handout 2 s3.1, "applied one level up"). A
simulation with 25 candidates of identical true risk 400 and CV noise 30
reports 341 for "the best" -- 59 units of pure selection bias with no model
involved. Pessimism is safe, optimism is not, which is why the test set
exists. A2 row 3 compares no candidates, so it carries only the conservative
bias. Both biases will be large in Apparel at n=197 with 25 alphas.

---

## Session 5 — 2026-09-29 (macOS laptop). B1 done. Concepts for B2 settled.

Transcript: `sessions/claude-code/a1-session-5.jsonl` and `.txt`. Same VS Code
thread as sessions 2 and 4, continued, so the file contains those as its
opening parts (see `sessions/README.md` for the containment table).

### What was done

- Confirmed `test_extract("H")` **is** `replicates.csv` filtered to division H
  — verified with `.equals()`. There is no separate test set: one file, two
  jobs (the noise floor, and scoring once). All **eight** B2 cells are scored
  on their own division's 450 replicate rows; nothing is held back.
- `analysis/part2/b1_noise_floor.py`, in `run.sh`. Full run now ~13 s.
- `drafts/b1_draft.md`: exhibit, 62 words of prose, the two-variances note,
  the level-dependence caveat, argue-against list, provenance.
- `drafts/a2_draft.md`: new section on active vs passive use of data, and the
  correction that A2 did not use the validation month but A3 did.
- Office-hours questions recorded above (three, ranked).

### B1 numbers, with provenance (all from `bash analysis/run.sh`)

| Quantity | Value | File |
|---|---|---|
| Hardgoods sigma^2 | 148.11 +/- 10.41 (sigma 12.17 units, mean units 111.88) | `b1_noise_floor.csv` |
| Apparel sigma^2 | 142.04 +/- 9.98 (sigma 11.92 units, mean units 111.04) | " |
| dof | 405 each (45 configs x 9) | " |
| Difference A - H | -6.1, SE 14.4, **0.42 standard errors** | `run.log` |
| Avoidable vs contractor's best | H 82.9 (64% of 231 is floor); A 272.0 (34% of 414 is floor) | `b1_noise_floor.csv` |
| Estimator's assumption | 0 of 12 fields vary within any of the 90 configs; all groups size 10; script raises if not | `b1_config_check.csv` |
| Variance-on-mean slope | H +0.657 +/- 0.410 (consistent with both Poisson and constant); A +0.103 +/- 0.401 (rules out Poisson) | `b1_variance_shape.csv` |
| Overdispersion vs Poisson | 1.32x / 1.28x | " |

**Independent check:** the brief says sigma/sqrt(10) ~ 4 units without naming
a division. Ours give 3.85 and 3.77. That figure was computed by the
instructor from data we had not seen.

**Finding:** the unavoidable error is the same size in both divisions, so the
contractor's "Apparel is inherently harder" does not survive. What differs is
avoidable error: 83 units^2 above the floor in Hardgoods, 272 in Apparel.

### Concepts settled this session (carry into B2/B3)

1. **Two variances, not one.** Handout 3 s1.1's "two levels of randomness".
   **Var** = E_D[(fhat_D(x0) - fbar(x0))^2] is how much the *prediction* moves
   across training samples — reducible. **sigma^2 = Var(eps_0)** is how much
   the *outcome* moves at a fixed x — irreducible. B1 measures the second.
2. **Say "the average unavoidable error".** Handout 3 eq. (4) bars Bias^2 and
   Var but not sigma^2, silently assuming the floor is constant in x. `units`
   is a count and Handout 1 s4.7 warns variance usually grows with the mean.
   Tested: inconclusive (see slopes above). Doesn't threaten the B1
   comparison — both divisions pooled identically over similar demand ranges
   — but would matter for judging a single store-week prediction.
3. **CV carries two opposing biases.** Fitting on (K-1)/K of the data makes
   every candidate's estimate *pessimistic* for the final refit (H2 s3.2,
   s4.3). Selecting the best of several noisy estimates makes the *winner's*
   reported score *optimistic* (H2 s3.1, "applied one level up"). Simulation:
   25 candidates with identical true risk 400 and CV noise 30 report 341 for
   "the best" — 59 units of pure selection bias, no model involved.
   Pessimism is safe; optimism is why the test set exists. A2 row 3 compared
   no candidates, so it carries only the conservative bias.
   **Expect both to be large in Apparel** (n=197, folds fit on ~158 rows, 25
   alphas x 2 degrees), so Apparel's tuned CV number will flatter itself
   relative to its test MSE, and by more than Hardgoods' does.
4. **CV *replaces* a validation set, it does not supplement one** (H2 s3.2 ->
   s4, protocol s6). Part B has no validation set. Part A has a validation
   month only because its holdout is temporal and folds cannot manufacture a
   time-ordered holdout.
5. **The 1-SE rule needs fold-level errors.** H2 s4.5:
   `SE(d) = sd(MSE_1..MSE_K)/sqrt(K)`, then take the *simplest* model whose CV
   error is within one SE of the minimum. Scoring the K fold-models on a
   single shared holdout instead would measure something else — the spread of
   the *predictor* with the evaluation data fixed, which is the **Var** term
   and is what B3 measures with bootstrap resamples. The rule's SE is a
   heuristic: the K training sets overlap heavily so the fold errors are
   correlated, and sd/sqrt(K) treats them as independent.

### B2 — design calls still OPEN (mine to make before coding)

1. **How the penalty is tuned.** (a) tune to the CV minimum and *discuss* the
   1-SE rule in the write-up, or (b) tune *by* the 1-SE rule and report both.
   Whichever is chosen becomes the value frozen into B3's
   `RIDGE_ALPHA_DEG1/DEG2` — `stability.py` says do not re-tune inside the
   resamples. The brief's B2 question 2 says to "note where the
   one-standard-error rule bears on your answer", which reads like (a) plus
   discussion, but (b) is defensible if stated.
2. **Averaging, not pooling — recommended and near-settled.** The brief asks
   for "CV MSE with its standard error across folds", and the SE only exists
   if the five fold-level MSEs are kept. Note A2 *pooled* out-of-fold
   predictions (right for AUC, which is not an average of per-row losses).
   Fold sizes: Hardgoods 600x5 (pooled == averaged), Apparel 40,40,39,39,39
   (they differ slightly). Verified in session 5.
3. **Degree 3?** `DEGREES = (1,2,3)` exists and `basis_size(3)` = 454 terms,
   which against 197 Apparel rows would make the terms-to-rows point vividly.
   The brief specifies four models and says there are no marks for more.
   Recommendation: keep it out of the exhibit; the optional `sweep.py` shows
   it.
4. **Where Part B's figures land** — open since session 1. `sweep.py` writes
   to `sweep_outputs/` and `stability.py` to `b3_outputs/`, both beside the
   script. Session-1 decision: keep the starter's folder names. Remaining
   choice: `analysis/part2/<name>/` vs `analysis/outputs/<name>/`. Everything
   else in this submission writes to `analysis/outputs/`.

### B2 — what the script must do (from the brief's protocol table)

- **Tune:** 5-fold CV on the division's own training extract using
  `make_folds()` (seed 575, do not change). `poly_pipeline(estimator, degree=d)`
  fits the basis and the scaler *inside* each fold. `ALPHA_GRID` is 25
  log-spaced values; the brief warns that if the best value lands on an
  endpoint, something upstream is wrong.
- **Refit** each tuned configuration on all rows of that division's training
  extract. Hardgoods must go through `dedup_h()` (3,350 -> 3,000).
- **Test:** score once on `test_extract("H")` / `test_extract("A")`.
- **Report** per cell: tuned penalty where there is one, CV MSE with its SE
  across folds, test MSE, and **test MSE - sigma^2_hat**.
- Eight cells: {degree 1, degree 2} x {OLS, ridge} x {H, A}.
- Check our degree-1 and degree-2 OLS CV MSEs against the contractor's
  quoted 336 / 231 (H) and 414 / 618 (A). If they land far off, B1's
  "avoidable" column needs restating with our own figures.

### Useful identity for B2's interpretation

All ten replicates of a configuration are identical on every feature, so the
model predicts the same value for all ten and the test MSE splits exactly:

    test MSE = (405/450) * sigma^2_hat + (1/45) * sum_g (ybar_g - yhat_g)^2

The second term is the only part a better model could remove. That is why the
brief insists a raw MSE has no interpretation without the floor beside it.

### Still open beyond B2

- B3 after B2 (needs B2's penalties). `stability.py`'s `build_models()` is
  the only thing to fill in; everything else there is fixed.
- Prose budget: A1 499 + A2 552 + A3 448 = 1,499 words for a two-page S1
  (~1,000-1,200). ~450 words to cut; candidates listed at the end of
  `drafts/a3_draft.md`. S2 is one page for B1+B2+B3 together (~450-500
  words), of which B1 uses about 60.
- `memo.md` and `ai_process_note.md` not started. The process note is **one
  page maximum for both parts** (~500 words) against 1,927 now in
  `drafts/ai_process_note_draft.md` — that file is a quarry, not a draft, and
  is not submitted.
- Deadline Thursday 1 October, 6:00 PM Central.

---

## Session 6 - 2026-10-01 (Windows 11 machine). B2 and B3 done. Part B complete.

Transcript: `sessions/claude-code/a1-session-6.jsonl` and `.txt`. Thread A
continued (sessions 1 and 3), so the file contains those as its opening part;
see the containment table in `sessions/README.md`.

**Deadline extended to Friday 2026-10-02, midnight. Office hours Friday 11:00**,
so the three ranked questions in the session-4 block get answered before
submission.

### What was done

- `analysis/part2/b2_models.py` and `analysis/part2/b3_stability.py`, both in
  `run.sh`. **The whole submission now runs in ~18 s from one command.**
- `drafts/b2_draft.md` (Exhibits B2, B2b, B2c; prose 392 words) and
  `drafts/b3_draft.md` (Exhibit B3, per-query-point table; prose 211 words).
- Supplied folders still byte-identical: `git diff HEAD -- part1_northline
  part2_cascade` is empty, B3 included.

### Design decisions made (mine)

- **Tuned to the CV minimum**, not by the 1-SE rule; the 1-SE alpha is
  reported beside it. The asymmetry this creates (a ridge cell reports the
  minimum of 25 estimates, an OLS cell reports one) is disclosed in the
  Exhibit B2 footnote.
- **CV MSE = average of the five fold MSEs**, not pooled, because the SE
  across folds is asked for and only exists if the five are kept. A2 pooled,
  correctly, for a different reason: AUC is a pairwise rank statistic and the
  analyst's protocol had to be reproduced exactly.
- **No degree 3.** No marks for more models.
- **B3 runs the supplied loop as issued**, via a wrapper that imports
  `stability.py` and supplies only the penalty dicts, `build_models()` and the
  output path. Chosen over editing or copying it.
- **Signed mean bias added** to B3's table beside the starter's mean absolute.
- **Outputs to `analysis/outputs/`**, overriding the session-1 decision to
  keep the starter's `b3_outputs/` folder name.
- No bootstrap CI on the B2 cells; not asked, page budget.

### B2 numbers, with provenance (all from `bash analysis/run.sh`)

| Quantity | Value | File |
|---|---|---|
| Hardgoods d1 OLS / ridge | CV 336.62 +/- 6.42 / 336.61 +/- 6.39; test 398.55 / 398.38 | `b2_table.csv` |
| Hardgoods d2 OLS / ridge | CV 233.12 +/- 4.64 / **232.98** +/- 4.79; test 246.16 / 247.47 | " |
| Apparel d1 OLS / ridge | CV 413.53 +/- 29.84 / 412.06 +/- 36.19; test 363.58 / 354.12 | " |
| Apparel d2 OLS / ridge | CV 617.97 +/- 67.54 / **329.80** +/- 14.31; test 366.86 / **296.19** | " |
| Test - sigma^2, all eight | H 250.44 / 250.27 / 98.05 / 99.36; A 221.54 / 212.08 / 224.82 / **154.15** | " |
| Tuned alpha | d1 H 10.0, A 10.0; d2 H 0.316, A 3.162. None on a grid endpoint | `b2_penalties.csv` |
| 1-SE alpha | 316.2 / 5.62 / 56.2 / 10.0 | `b2_table.csv` |
| Terms per row | H 0.004 / 0.030; A 0.061 / **0.457** | " |
| Penalty effect, paired across folds | A d2 **288.16 +/- 55.02** (5.2 SE); H d1 0.01 +/- 0.05; H d2 0.15 +/- 0.22; A d1 1.47 +/- 7.26 | `b2_differences.csv` |
| d2 ridge vs best hand-picked | H 0.15 +/- 0.22 (a tie); A better by 83.72 +/- 19.98 | " |
| Alphas within 1 SE of the minimum | H 19/25 (d1), 12/25 (d2); A 16/25 (d1), 5/25 (d2) | `b2_alpha_curves.csv` |
| Contractor reproduced | 336.62 / 233.12 / 413.53 / 617.97 against his 336 / 231 / 414 / 618, all under 0.5 SE | `b2_contractor_check.csv` |
| Test MSE split, floor part | H 133.30, A 127.83 (= 0.9 sigma^2); identity checks to 0 in all 8 cells | `b2_test_decomposition.csv` |

### B3 numbers, with provenance

| Quantity | Value | File |
|---|---|---|
| Hardgoods mean sd / mean abs bias | d1 OLS 1.14 / 12.65; d1 ridge 1.14 / 12.66; d2 OLS 2.83 / 3.84; d2 ridge 2.80 / 3.64 | `b3_stability.csv` |
| Apparel mean sd / mean abs bias | d1 OLS 4.33 / 16.66; d1 ridge 4.13 / 16.46; d2 OLS **25.24** / 18.78; d2 ridge **7.22** / 15.05 | " |
| Signed mean bias | H +1.35 / +1.34 / +0.86 / +1.05; A +9.35 / +8.70 / -6.16 / +4.15 | " |
| H d1 OLS per-point bias | +21.01, -15.06, -1.89 (cancel to +1.35) | " |
| A d2 OLS per-point sd | 18.08, 30.25, 27.40 | " |
| Bias^2 / variance (units^2) | H d2 ridge 15.1 / 8.9 (63% bias); A d2 OLS 474.9 / 664.2 (42%); A d2 ridge **292.8 / 52.9 (85% bias)** | " |
| Yardstick precision | sigma/sqrt(10) = 3.85 (H), 3.77 (A) | `run.log` |
| Figure | `b3_stability.png` | |

Measured in session, notes only, not in a script: the B2-vs-B3 level gap
decomposes as 154.2 (45 configs, one fit) -> 257.3 (3 query points, same fit)
-> 345.7 (3 points, 20 bootstrap fits), with bootstrap resamples holding 0.625
distinct rows. Per-point reducible error at the three Apparel query points is
A10 = 624, A08 = -12, A07 = 159.

### Findings this session

- **The contractor's arithmetic was right; his conclusions were wrong.** All
  four of his quoted figures reproduce within half a standard error.
- **One specification serves both divisions: degree-2 ridge.** It ties the
  best hand-picked choice in Hardgoods (0.15 +/- 0.22) and beats it in Apparel
  (83.72 +/- 19.98). The 1-SE rule is what licenses the Hardgoods half.
- **Terms per row, not division size, is the quantity.** Apparel degree 1 is
  the proof: the same 197 rows, 12 terms instead of 90, penalty worth nothing
  (1.47 +/- 7.26).
- **Degree 1 -> 2 is a trade in Hardgoods and a pure loss in Apparel.**
  H: sd 1.14 -> 2.83, bias 12.65 -> 3.84. A: sd 4.33 -> 25.24, bias 16.66 ->
  18.78.
- **The penalty converts Apparel's variance problem into a bias problem.** The
  best Apparel model is 85% bias (293 against 53 units^2). So the standard
  should say "collect more Apparel history", not "use a bigger basis" or
  "penalise harder". This is the bridge into standardise-a-process.
- **CV and test diverge in opposite directions by division.** Apparel's test
  comes in below CV (158-row folds against a 197-row refit: the conservative
  CV bias); Hardgoods degree 1 goes the other way (the 45 configurations are
  not a random sample of where the training rows live).
- Two instructor-embedded checks passed: sigma/sqrt(10) ~ 4, and the tuned
  penalties coinciding at one degree and not the other.

### Rule for the memo

**Never put a B3 level beside a B2 level.** Same cell, but two different
populations of query points and two different training sizes. Comparisons
*within* a table are safe. B2 for levels, B3 for mechanism.

### Open - everything that is left

1. **`memo.md` is the whole remaining job.** One document, two sections, each
   leading with its recommendation. S1 to the Northline VP (A1-A3, max 2 pages
   of prose plus Exhibits A1-A3); S2 to the Cascade VP (B1-B3, max 1 page plus
   Exhibits B1-B3), answering Part B's three questions and saying what a
   company-wide standard should fix and what it should leave to the data, in
   terms that would transfer to a third division acquired next year.
   - S1 prose: 499 + 552 + 448 = **1,499 words against ~1,000-1,200.** Trim
     candidates are listed at the end of `drafts/a3_draft.md`.
   - S2 prose: 70 + 392 + 211 = **673 against ~450-500.** Candidates: B2's
     fourth paragraph, the signed-bias clause, the CV-vs-test divergence.
   - Exhibit count: A1, A2, A2b, A2c, A3a-A3d, B1, B2, B2b, B2c, B3 is
     thirteen labels against the brief's "Exhibits A1-A3" and "B1-B3". Needs
     pruning or re-lettering.
   - The memo is organised by argument, not by rubric item. Some of the trim
     comes free from that, since the drafts repeat context for each other.
2. **`ai_process_note.md`** - one page, ~500 words, both parts.
   `drafts/ai_process_note_draft.md` is now **3,199 words**. It is a quarry,
   not a draft, and is not submitted. The strongest items are the ones where I
   corrected the agent.
3. **Office hours Friday 11:00.** Three ranked questions in the session-4
   block. Question 1 (the "building data" reading in A2) is the only one that
   could require a re-run, and that is a one-line edit plus a re-run, not a
   rebuild.
4. **Final verification: DONE for the analysis, 2026-10-01.** Cloned the repo
   to a fresh directory with no `.venv`, wiped `analysis/outputs/`, and ran
   `bash analysis/run.sh` with only `python3` on PATH, as a grader would.
   Exit 0, 12.7 s, 32 outputs; **all 31 files byte-identical** to the
   committed versions, and `run.log` identical once absolute paths and the
   Python patch version are stripped. Also checked: no absolute paths in
   `analysis/`, seeds set, supplied folders byte-identical. Repeat this check
   once more after the memo exists, against the memo's numbers.
5. Prose is the only thing left with no code behind it. Budget time for it.

---

## Session 7 — 2026-10-01 (macOS laptop). memo.md and ai_process_note.md drafted.

Transcript: `sessions/claude-code/a1-session-7.jsonl` and `.txt`. Thread B
continued (sessions 2, 4, 5), so it contains those as its opening part; the
containment table in `sessions/README.md` is updated.

### What was done

- Pulled session 6. **Cross-machine check passed again**: full pipeline here in
  18.6 s, `b2_table.csv` / `b3_stability.csv` differing from the Windows commit
  by at most 1.2e-11, `b2_test_decomposition.csv` identical.
- **`memo.md` drafted.** One document, two sections, each leading with its
  recommendation. Exhibits sit with their own section, not in a shared
  appendix, because the two sections address different readers.
- **`ai_process_note.md` drafted**, 537 words.
- **`analysis/check_memo_numbers.py`**: asserts 50 headline memo figures
  against `analysis/outputs/`. Deliberately NOT in `run.sh`, so a clean clone
  with no memo still runs end to end. All 50 match.
- `brew install pandoc` on this machine (not a project dependency; only used
  to measure page length). Chrome headless PDF rendering was tried and
  abandoned — it hangs. The reliable measure is
  `pandoc X.md -t plain --columns=92 | wc -l`, against roughly 46-51 lines per
  letter page at 11pt with 1in margins.

### Length, as measured

| | Lines | Limit | |
|---|---:|---|---|
| §1 prose | 91 | 2 pages (~92-102 lines) | fits |
| §2 prose | 49 | 1 page (~46-51) | fits |
| `ai_process_note.md` | 54 | 1 page | marginal; ~14 of those are blank lines between paragraphs, which render as half-gaps |

**Exhibits consolidated from 13 labels to the 6 the brief names** (A1, A2,
A2b, A3, B1, B2, B3 — A2b is a panel of A2, not a seventh exhibit). The
rubric's required one-sentence interpretation of each A2 row went into an
exhibit *column*, since exhibits do not count against the prose limit. Dropped
from the memo and still available in the drafts: the odds-ratio table, the
per-query-point B3 table, the contractor-check table (now a footnote line
under Exhibit B2), and A3's offer-quality table.

### Decisions made (mine)

- §2's recommendation: **standardise the process, not the model.** I had first
  thought the answer was to name a specific model; the rubric's named trap is
  "a standard that is really a model", so degree-2 ridge is an *output* of the
  process, not the standard.
- Added the measurement-lever point to §2 after noticing it: more rows lower
  the *reducible* error, only new fields lower the floor, and Hardgoods sits
  only 99 units² above its floor. Not required by the brief; added because it
  is what makes "report distance from your own floor" portable to a third
  division. Cost two lines elsewhere in §2.
- Exhibits grouped per section rather than one appendix.
- `.md` not `.pdf`, which the brief allows.

### Concept settled this session

σ̂² is irreducible **relative to the recorded fields**, not absolutely
(Handout 1 §4.3: "the variability that remains after conditioning on
everything you measured"). Independent of the model and of the number of rows;
*dependent on which columns exist* and on how `units` is defined and measured.
So: more rows → floor unchanged, reducible error falls. More columns → the
floor itself can fall. That is the distinction behind §2's closing paragraph.

### Open — what is left

1. **Editing `memo.md` is the remaining job, and it is mine.** The agent
   over-drafted it; every line is to be vetted. The two recommendation
   paragraphs in particular should sound like me.
   - Re-run `python analysis/check_memo_numbers.py` after editing.
   - Re-measure length with the pandoc command above.
2. `ai_process_note.md` likewise to be vetted — it is graded on specificity
   about *my* judgment, and the strongest items are the ones where I corrected
   the agent.
3. **Office hours Friday 11:00.** Three ranked questions in the session-4
   block; question 1 (the "building data" reading in A2) is the only one that
   could require a re-run, and that is a one-line edit.
4. **Final verification to repeat once the memo is final:** clean clone, no
   `.venv`, wiped outputs, `bash analysis/run.sh` with only `python3` on PATH,
   then `check_memo_numbers.py`.
5. Deadline Friday 2026-10-02, midnight.

---

## Session 8 - 2026-10-02 (Windows 11 machine). Part A of the memo edited and vetted.

Transcript: `sessions/claude-code/a1-session-8.jsonl` and `.txt`. Thread A
continued (sessions 1, 3, 6), so it contains those as its opening part.

### What was done

- Pulled session 7. Verified the Windows re-run against the Mac commit: labels
  identical in every output, largest numeric change 8.9e-11, so nothing moves.
- **`memo_orcun.md` created and Part A edited by me**, in my own voice.
  `memo.md` deliberately left at the committed draft so the diff stays honest.
- Both figures embedded in the memo (`a3_value_curve.png` in Exhibit A3(c),
  `b3_stability.png` in Exhibit B3). The B3 one matters: the rubric requires
  "plus the figure", and a filename reference is not a figure.
- **Per-segment standard errors added to `a3_decision.py`** and to Exhibit
  A3(a). This came out of a question of mine, see below.
- All em dashes removed from `memo_orcun.md` and `ai_process_note.md`.
- `check_memo_numbers.py` extended from 50 to 61 assertions.

### The question that moved an argument (mine)

I asked whether the programme's standard error differed by segment. It was not
in the run, so it was added. Results:

| Segment | Offers | Value | SE | SEs from zero |
|---|---:|---:|---:|---:|
| all | 242 | $852 | $572 | 1.49 |
| corporate | 9 | -$78 | $84 | -0.93 |
| other | 233 | $930 | $565 | 1.65 |

Two consequences. Corporate's -$78 is 0.93 SE from zero, so the dollar case for
excluding corporate cannot stand alone. And excluding corporate moves
reliability only from 1.49 to 1.65 SE, because corporate was 9 of 242 offers,
so the exclusion does not make the programme reliable either. The memo now
gives both reasons, the 11% precision labelled as nine offers and the
structural case (0.404 on 860 rows, 533 training rows with no tenure past six
months) named as the one to rely on.

### Errors caught in my own editing pass

The agent flagged three places where my rewording changed the meaning. Worth
recording because they are the kind of thing an editing pass introduces:

1. I wrote that the data "already was not" unseen at change 3. It **was**
   unseen; out-of-fold means exactly that. The point is that only *lateness*
   changed, not novelty.
2. I wrote the tripwire sentence so that "it" referred to the dollar measure
   holding steady. The argument is the reverse: the *ranking statistic* holds
   steady through calibration drift, which is why it makes a bad alarm.
3. I called population drift "another type of leak". It is not. Leaks make
   0.967 wrong about 2024-25 itself; drift means an honest number need not
   transfer. Protocol fixes the first, only segment reporting reveals the
   second. The memo now says so explicitly.

Also fixed: "so each is attributable to one cause" contradicted my own
decomposition paragraph two paragraphs later, and now reads "each row differs
from the one above it by exactly one change".

### Concepts settled this session

1. **The brief's "9% of active members cancel in any 60-day window" is the
   base rate of the target column, not a rolling 60-day rate.** Measured: label
   base rate 9.29%, one-month cancellation rate 9.37%, true rolling 60-day rate
   17.4% (start-of-window denominator) to 19.8% (any-time-in-window). So the
   phrase is loose relative to the delivered label. Office-hours question 4.
2. **Why the row base rate is the right unit.** Within any single month each
   member appears exactly once, so the monthly rate literally is "share of
   active members flagged"; the pooled 9.29% is the book-size-weighted average
   of 24 such windows (unweighted mean 9.33%, weighted 9.29%). The repetition
   is across windows, not within one. And the unit is a decision opportunity:
   one offer is one member-month, priced at $18.
3. **Random CV fails three separate ways**, all now named in the memo:
   direction (training on later rows), label maturity (no gap, so training
   labels encode the evaluated period), and member identity. On the third, the
   memo now names the danger rather than only its size: a member merely
   *having* a later row proves they had not cancelled earlier.
4. **The deployment gap.** On 1 April 2026 a February row's 60-day window does
   not close until the end of April, so the freshest usable labels are always
   about two months old. The protocol's gap reproduces that rather than
   handicapping the evaluation.
5. **Why the tripwire is in dollars.** If every predicted probability drifted
   upward, the ranking would be untouched and AUC would not move at all, while
   the 21.4% cut-point would start buying offers for members who do not need
   them. AUC is blind to the failure that destroys the economics.

### Decisions made (mine)

- Mention **both** reasons for excluding corporate, with the dollar figure
  labelled as nine offers. The weaker reason is still a real observation.
- Put the dictionary discrepancy in the memo as one sentence addressed to her
  analytics team, not as a paragraph and not as a verdict.
- Keep length as-is for now and convert to PDF with a smaller font if needed.
  The agent's view is that a real trim is the stronger option, since the same
  content fitted in 93 lines before my edit; revisit after office hours.
- Deleted the exclamation mark in a section heading and the duplicated
  "My recommendation is that..." sentence.

### Length, as measured

| | Words | Lines | Limit |
|---|---:|---:|---|
| S1 prose | 1,614 | ~133 | 2 pages (~92-102 lines) |
| S2 prose | 565 | 49 | 1 page (~46-51) |
| `ai_process_note.md` | 641 | 62 | 1 page (~46-51) |

S1 and the process note are both over at 11pt. Decision above.

### Open - what is left

1. **S2 of `memo_orcun.md` is still the agent's draft.** Next block: read the
   B1, B2 and B3 drafts, ask whatever is unclear, then edit S2 in my voice the
   way Part A was done.
2. **Office hours Friday 11:00.** Four questions, in the session-5 block as
   amended. Question 1 (the "building data" reading) is the only one that could
   force a re-run, and that is a one-line edit.
3. After S2: decide on length (trim or font), re-run
   `python analysis/check_memo_numbers.py`, then the final clean-clone check.
4. `memo.md` stays as the committed reference draft for diffing. Decide before
   submission whether to delete it or keep it in `drafts/`.
5. Deadline Friday 2026-10-02, midnight.
