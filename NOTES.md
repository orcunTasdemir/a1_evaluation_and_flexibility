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
