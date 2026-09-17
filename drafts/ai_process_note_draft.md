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

## Session 3 — (to be added)
