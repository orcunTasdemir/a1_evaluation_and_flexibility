# CLAUDE.md

IDS 575 Fall 2026, Assignment 1. Two cases (Northline Fitness churn
evaluation, Cascade Outdoor flexibility), one memo. Due Thursday
October 1, 6:00 PM Central.

## Scope

Work only inside this assignment folder (policy §3). Four deliverables:
memo, `analysis/`, `ai_process_note.md`, `sessions/`.

## Never do these

- **Never read a data file into the conversation.** No `cat`, `head`,
  `print(df)` or paste of CSV contents. Write code that reads the file
  and reports numbers back. `member_months.csv` is 33,000 rows.
  (brief, "Two practical habits"; setup §5)
- **Never choose the evaluation design.** Splits, metrics, units of
  analysis, and what counts as held out are mine to decide. Lay out
  options and tradeoffs; do not pick one and proceed. (approach §4)
- **Never write the judgment.** Do not draft the recommendation, or
  decide whether a model is good enough. (approach §4)
- **Never edit a supplied data file.** `division_h.csv` ships with
  duplicated store-weeks (CO-4471) and `member_months.csv` with
  duplicates from the re-run March 2025 load (NLF-2231), deliberately.
  Dedup in code; use `dedup_h()` for Part B. No in-place fixes.
- **Never select on a test set.** Northline 2025-10 to 2025-12 and
  Cascade `replicates.csv` are scored once and select nothing.
  (brief, Ground rules)
- **Never bundle the A2 changes.** One change at a time, AUC recorded
  after each, each row labelled cross-validated or test-window.
- **Never report a Part B error without the floor beside it.** State
  test MSE and test MSE minus sigma-hat squared. (brief, Ground rules)
- **Never re-tune penalties inside the B3 bootstrap.** Hold them at
  the B2 values.
- **Never state a number you have not produced by running code.** If a
  figure is not in a run's output, it cannot go in the memo.
  (policy §3, Validate outputs)

## Requirements on the code

- `analysis/` runs end to end from one command on a clean copy of the
  folder. State the command in `analysis/README.md`, with what it
  produces and roughly how long it takes.
- Assume the grader has Python 3.10+, numpy, pandas, scikit-learn and
  matplotlib and nothing else. Anything further goes in
  `analysis/README.md`. No GPU.
- No absolute paths. Set random seeds so numbers reproduce.
- Figures, tables and saved numbers go in `analysis/outputs/`.
- Fit preprocessing inside each CV fold. Use the supplied helpers:
  `month_key()`, `make_folds()`, `poly_pipeline()`,
  `bootstrap_indices()`, `QUERY_CONFIGS`, `ALPHA_GRID`.
- Standardise before penalising; `poly_pipeline()` handles it.
- Cache expensive results. `analyst_model.py` returns the same numbers
  every time; run it once and save the output. (setup §5)

## How to work with me

- Baseline before model. Compute the do-nothing answer first.
  (approach §3)
- When I reach a conclusion, argue against it. "What would have to be
  true for this estimate to be wrong?" and "What is the strongest
  objection to this?" (approach §4)
- Say so when a result looks too good.
- If I cannot explain what you produced, stop. I may be asked to
  explain or modify any line of this submission in an oral check.
  (approach §4; checklist, Ownership checks)
- One work block per session, kept to one topic. (setup §5)

## End of every session

1. `/export sessions/claude-code/a1-session-N.txt`
2. Note for `ai_process_note.md`: what was delegated, what I changed
   or rejected and why, how numbers were checked. Specific instances.
   Generic notes score zero. (checklist)
3. Transcripts embed full file contents and command output. This
   folder must contain only course material. (policy §7)
4. Claude Code deletes transcripts after 30 days by default. The copy
   in this repo is the record. (export sheet §2)

## Cross-machine continuity

I work on two machines and alternate. Conversation history does not
travel between them; this repo does. At the end of each session,
append to `NOTES.md`: what was done, what the current open question
is, and any number produced with where it came from. Read `NOTES.md`
at the start of each session.