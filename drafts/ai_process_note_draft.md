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

