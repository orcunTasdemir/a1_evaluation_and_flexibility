# Analysis — how to run

One command, from the assignment folder root:

    bash analysis/run.sh

Requires Python 3.10+ with numpy, pandas, scikit-learn and matplotlib. No
other packages. No GPU. Pinned versions used to produce the submitted numbers
are in `../requirements.txt` (Python 3.11; numpy 2.4.6, pandas 3.0.5,
scikit-learn 1.9.1, matplotlib 3.11.2). The script prefers `../.venv` if one
exists and otherwise uses `python3` on PATH.

Runtime: about 15 seconds so far (A1 only). Will be updated as parts are added.

## What it runs, in order

| Step | Script | Writes to `outputs/` |
|---|---|---|
| Analyst's pipeline, as supplied | `part1_northline/starter/analyst_model.py` | `analyst_model_output.txt` |
| A1 baselines | `part1/a1_baselines.py` | `a1_baselines.csv` (the exhibit), `a1_cleaning.txt`, and diagnostics `a1_base_rate_by_year.csv`, `a1_base_rate_by_month.csv`, `a1_column_timing.csv` |

Everything printed is also captured in `outputs/run.log`.

## Notes

- The supplied `starter/` modules are imported, not copied or modified.
- A1 has no randomness (single-variable rules are not fitted). Seeds for later
  parts are set in the scripts that need them and noted here when added.
- Data files are read in place from `part1_northline/data/` and
  `part2_cascade/data/`; nothing is written there.
