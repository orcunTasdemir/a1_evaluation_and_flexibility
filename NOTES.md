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
