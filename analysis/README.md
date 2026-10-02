# Analysis — how to run

One command, from the assignment folder root:

    bash analysis/run.sh

Requires Python 3.10+ with numpy, pandas, scikit-learn and matplotlib. No
other packages. No GPU. Pinned versions used to produce the submitted numbers
are in `../requirements.txt` (Python 3.11; numpy 2.4.6, pandas 3.0.5,
scikit-learn 1.9.1, matplotlib 3.11.2). The script prefers `../.venv` if one
exists and otherwise uses `python3` on PATH.

Runtime: about 18 seconds for the whole submission (A1-A3, B1-B3).

## What it runs, in order

| Step | Script | Writes to `outputs/` |
|---|---|---|
| Analyst's pipeline, as supplied | `part1_northline/starter/analyst_model.py` | `analyst_model_output.txt` |
| A1 baselines | `part1/a1_baselines.py` | `a1_baselines.csv` (the exhibit), `a1_cleaning.txt`, and diagnostics `a1_base_rate_by_year.csv`, `a1_base_rate_by_month.csv`, `a1_column_timing.csv`, `a1_churn_by_tenure.csv`, `a1_corporate_segment.csv` |
| A2 evaluation | `part1/a2_evaluation.py` | `a2_table.csv` (the exhibit), `a2_columns.csv` (every column's keep/drop decision with the dictionary's timing note), `a2_test_scores.csv` (test-window predictions, read by A3 so the test set is scored once) |
| A3 targeting decision | `part1/a3_decision.py` | `a3_threshold.txt` (the derivation), `a3_value.csv` (the exhibit), plus diagnostics `a3_calibration.csv`, `a3_by_month.csv`, `a3_offer_quality.csv`, `a3_value_curve.csv`, `a3_value_curve.png` |
| B1 noise floor | `part2/b1_noise_floor.py` | `b1_noise_floor.csv` (the exhibit), `b1_config_check.csv` (the estimator's assumption, verified), `b1_variance_shape.csv` (is the floor level-dependent, and how wide the per-configuration spread is), `b1_query_yardsticks.csv` (B3's yardstick per query point rather than pooled) |

| B2 four models | `part2/b2_models.py` | `b2_table.csv` (the exhibit), `b2_alpha_curves.csv`, `b2_penalties.csv` (tuned alphas, read by B3), `b2_contractor_check.csv`, `b2_differences.csv`, `b2_test_decomposition.csv`, `b2_shrinkage.csv` (how much the tuned penalty actually moved the coefficients) |
| B3 stability | `part2/b3_stability.py` | `b3_stability.csv` (the exhibit, in units and units²), `b3_stability.png` (the figure), `b3_flexibility_ledger.csv` (terms and terms-per-row beside bias² and variance: the two-dials evidence) |

Everything printed is also captured in `outputs/run.log`.

## Checking the memo against the run

`python analysis/check_memo_numbers.py` asserts that the headline figures
quoted in `memo.md` match `analysis/outputs/`. It is deliberately **not** part
of `run.sh`, so the analysis still runs on a clean clone with no memo present.
Run it after editing the memo.

## Notes

- The supplied `starter/` modules are imported, not copied or modified. B3 is
  the strongest case: `part2/b3_stability.py` imports the supplied
  `stability.py` and supplies only the two penalty dicts, `build_models()` and
  the output path, so the stability loop itself runs exactly as issued.
- B2's tuned penalties are written to `outputs/b2_penalties.csv` and read back
  by B3, so B3 cannot re-tune or drift from the B2 values.
  `part1/prep.py` holds the one cleaning routine (`load_clean()`) every Part A
  script uses: `month_key()` normalisation, then exact-duplicate removal.
- A1 has no randomness (single-variable rules are not fitted). A2 uses
  `random_state=0` for its folds, matching the analyst's script. Logistic
  regression is deterministic.
- A2 begins with a harness check that re-runs the analyst's exact protocol on
  the raw file and prints the AUC beside the printed 0.967. It is not an
  exhibit row and selects nothing; it confirms the harness is wired correctly
  before any change is measured.
- Data files are read in place from `part1_northline/data/` and
  `part2_cascade/data/`; nothing is written there.
