"""
A3 -- the targeting decision.  Northline Fitness churn.

Uses the final protocol from A2 and never rescores the test window: the
predictions come from `a2_test_scores.csv`, written by A2 row 3.

What happens here, in order, and the order matters:

    1. The cost-based threshold, derived from the finance table in the brief
       by taking the expectation at predicted probability p.  Two routes, both
       computed from the constants in starter/load.py rather than typed in.
    2. A calibration check on the validation month (2025-09).  The threshold
       multiplies p by money, so it assumes p is a probability and not merely
       a ranking (Handout R1 s4.7).  The validation month is the place the
       brief reserves for any choice made by looking at data; the test window
       is not touched.  Scoring the validation month needs the row-3 model, so
       it is refitted here through A2's own `fit_once` and `ADMISSIBLE` -- the
       same code path, deterministic, and A2 is left alone.
    3. Only then, the money: realised value on the test quarter at the derived
       threshold, against offering to everyone, against no programme, and at
       the threshold the analyst's script grid-searched.

The calibration verdict is set below, from the evidence in step 2, before any
dollar figure is computed.  Deciding it afterwards would be choosing the
correction by which version pays better.

Outputs, all in analysis/outputs/:
    a3_threshold.txt      the derivation, with the arithmetic printed
    a3_calibration.csv    reliability table on the validation month
    a3_value.csv          the A3 value exhibit: policies x segments
    a3_by_month.csv       the same threshold month by month
    a3_offer_quality.csv  where the value comes from inside the offered set
    a3_value_curve.csv    realised value across the threshold grid
    a3_value_curve.png    the same, as a figure
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = ROOT / "analysis" / "outputs"

sys.path.insert(0, str(HERE))
from prep import (TARGET, TRAIN_END, VALID_MONTH, OFFER_COST, MEMBER_LTV,  # noqa: E402
                  OFFER_CONVERSION, load_clean, offer_value)
from a2_evaluation import ADMISSIBLE, fit_once  # noqa: E402

# ---------------------------------------------------------------------------
# Calibration decision.  Set from the validation-month check in step 2, on
# calibration evidence only, before any dollar figure was computed.
#   "raw"   -- predicted probabilities used as they come out of the model
#   "platt" -- corrected by a logistic fitted on the validation month
# ---------------------------------------------------------------------------
# Verdict from step 2, on validation evidence only: Platt slope 0.79 (1.0 would
# be calibrated) and under-prediction in 8 of 10 bins including the decision
# region.  A pure level shift from September being a high-churn month would
# have left the slope near 1.0; it did not, so the miscalibration is a
# property of the model.  Correct.
CALIBRATION = "platt"

N_CALIBRATION_BINS = 10
ANALYST_THRESHOLD = 0.267    # what analyst_model.py's grid search selected
CURVE_GRID = np.linspace(0.005, 0.6, 400)   # the analyst's grid, for the curve


def derive_threshold() -> tuple[float, list[str]]:
    """The cost-based threshold, derived rather than quoted.

    Everything comes from the constants in starter/load.py so the arithmetic
    cannot drift from the brief.
    """
    gain_churner = MEMBER_LTV * OFFER_CONVERSION - OFFER_COST   # offer lands on a churner
    cost_stayer = OFFER_COST                                    # offer lands on a stayer
    t = OFFER_COST / (MEMBER_LTV * OFFER_CONVERSION)
    # Same number by Handout R1 eq. (4), t* = C_FP / (C_FP + C_FN), with a
    # wasted offer as the false positive and a missed churner as the false
    # negative.  Two routes agreeing is the check.
    t_r1 = cost_stayer / (cost_stayer + gain_churner)
    assert abs(t - t_r1) < 1e-12, (t, t_r1)

    lines = [
        "Deriving the threshold from the finance table",
        "",
        f"  offer cost                     ${OFFER_COST:,.2f}",
        f"  lifetime value of a member     ${MEMBER_LTV:,.2f}",
        f"  fraction of churners retained  {OFFER_CONVERSION}",
        "",
        "An offer to a member who would have churned is worth",
        f"  {MEMBER_LTV:,.0f} x {OFFER_CONVERSION} - {OFFER_COST:,.0f} = ${gain_churner:,.2f}",
        "An offer to a member who would not have churned costs",
        f"  ${cost_stayer:,.2f}",
        "No offer is worth $0.",
        "",
        "At predicted probability p the expected value of offering is",
        f"  E[value | p] = p x {gain_churner:,.0f} + (1 - p) x (-{cost_stayer:,.0f})"
        f" = {gain_churner + cost_stayer:,.0f}p - {cost_stayer:,.0f}",
        "",
        "Offering beats not offering when that expectation exceeds 0:",
        f"  {gain_churner + cost_stayer:,.0f}p - {cost_stayer:,.0f} > 0",
        f"  p > {cost_stayer:,.0f} / {gain_churner + cost_stayer:,.0f}"
        f" = {OFFER_COST:,.0f} / ({MEMBER_LTV:,.0f} x {OFFER_CONVERSION})",
        f"  p > {t:.6f}",
        "",
        f"Threshold t* = {t:.4f}.  Offer to every member scored above it.",
        "",
        "Cross-check, Handout R1 eq. (4): t* = C_FP / (C_FP + C_FN) with a",
        f"wasted offer C_FP = ${cost_stayer:,.0f} and a missed churner",
        f"C_FN = ${gain_churner:,.0f} gives {cost_stayer:,.0f}/"
        f"({cost_stayer:,.0f}+{gain_churner:,.0f}) = {t_r1:.6f}.  Same number.",
        "",
        "Note this depends only on the finance figures, not on the data, and",
        "was fixed before any test-window score was read.  The analyst's",
        f"script instead grid-searched {ANALYST_THRESHOLD} by maximising realised value",
        "on its own out-of-fold predictions, which is a choice made by looking",
        "at outcomes.",
    ]
    return t, lines


def logit(p: np.ndarray) -> np.ndarray:
    p = np.clip(p, 1e-12, 1 - 1e-12)
    return np.log(p / (1 - p))


def reliability(y: np.ndarray, p: np.ndarray, bins: int) -> pd.DataFrame:
    """Equal-count bins: mean predicted probability against observed rate."""
    order = np.argsort(p)
    groups = np.array_split(order, bins)
    rows = []
    for i, idx in enumerate(groups, start=1):
        rows.append({
            "bin": i,
            "rows": len(idx),
            "mean_predicted": round(float(p[idx].mean()), 4),
            "observed_rate": round(float(y[idx].mean()), 4),
            "churners": int(y[idx].sum()),
        })
    out = pd.DataFrame(rows)
    out["predicted_minus_observed"] = (out["mean_predicted"] - out["observed_rate"]).round(4)
    return out


def calibration_check(model) -> tuple[pd.DataFrame, LogisticRegression, list[str]]:
    """Score the validation month and ask whether p means what it claims."""
    df, _ = load_clean()
    val = df[df["month"] == VALID_MONTH].reset_index(drop=True)
    y = val[TARGET].to_numpy()
    p = model.predict_proba(val[ADMISSIBLE])[:, 1]

    table = reliability(y, p, N_CALIBRATION_BINS)

    # Platt scaling: a logistic regression of the outcome on the log-odds of
    # the model's own score.  If the model were already calibrated the fit
    # would be slope 1, intercept 0, so the coefficients read directly as
    # "how far off, and in which direction".
    platt = LogisticRegression().fit(logit(p).reshape(-1, 1), y)
    slope = float(platt.coef_[0][0])
    intercept = float(platt.intercept_[0])

    lines = [
        f"Calibration check on the validation month ({VALID_MONTH})",
        f"  rows {len(val):,}   churners {int(y.sum()):,}   "
        f"observed rate {y.mean():.4f}",
        f"  mean predicted probability      {p.mean():.4f}",
        f"  observed minus predicted        {y.mean() - p.mean():+.4f}",
        f"  AUC on the validation month     {roc_auc_score(y, p):.4f}",
        f"  Platt slope {slope:.4f}, intercept {intercept:+.4f} "
        f"(1.0 and 0.0 would be perfectly calibrated)",
    ]
    return table, platt, lines


def apply_calibration(p: np.ndarray, platt: LogisticRegression) -> np.ndarray:
    if CALIBRATION == "raw":
        return p
    if CALIBRATION == "platt":
        return platt.predict_proba(logit(p).reshape(-1, 1))[:, 1]
    raise ValueError(CALIBRATION)


def value_of(y: np.ndarray, offered: np.ndarray) -> float:
    """Realised dollars from a set of targeting decisions.

    Vectorised, then checked row by row against the supplied offer_value()
    helper so the economics come from the starter module, not from here.
    """
    v = np.where(offered, np.where(y == 1,
                                   MEMBER_LTV * OFFER_CONVERSION - OFFER_COST,
                                   -OFFER_COST), 0.0)
    check = np.array([offer_value(int(c), bool(o)) for c, o in zip(y, offered)])
    assert np.allclose(v, check), "vectorised value disagrees with offer_value()"
    return float(v.sum())


def per_offer_values(y: np.ndarray, offered: np.ndarray) -> np.ndarray:
    """The realised dollars from each offer actually made, one per offer."""
    return np.where(y[offered] == 1,
                    MEMBER_LTV * OFFER_CONVERSION - OFFER_COST, -OFFER_COST)


def value_with_se(y: np.ndarray, offered: np.ndarray) -> tuple[float, float]:
    """Total realised value and its standard error.

    Each offer returns +$66 or -$18, so the quarter's total is a sum of n
    such draws and its standard error is sd x sqrt(n).  Reported because the
    total sits close enough to zero that its uncertainty changes how it reads.
    """
    v = per_offer_values(y, offered)
    return float(v.sum()), float(v.std(ddof=1) * np.sqrt(len(v)))


def value_by_month(scores: pd.DataFrame, y: np.ndarray, offered: np.ndarray,
                   t_star: float) -> pd.DataFrame:
    """The same fixed threshold, month by month.

    Value per offer is exactly 84 x (precision - t*), so a month's programme
    is profitable precisely when the share of its offers that land on a
    churner exceeds the break-even precision, which is t* itself.
    """
    rows = []
    for month, idx in scores.groupby("month").groups.items():
        m = np.zeros(len(scores), dtype=bool)
        m[scores.index.get_indexer(idx)] = True
        o = offered & m
        n = int(o.sum())
        k = int((o & (y == 1)).sum())
        total, se = value_with_se(y, o) if n else (0.0, 0.0)
        rows.append({
            "month": month,
            "rows": int(m.sum()),
            "base_rate": round(float(y[m].mean()), 4),
            "offers": n,
            "offers_to_churners": k,
            "precision": round(k / n, 4) if n else np.nan,
            "break_even_precision": round(t_star, 4),
            "value_usd": round(total, 2),
            "value_se_usd": round(se, 2),
            "value_per_offer_usd": round(total / n, 2) if n else np.nan,
        })
    return pd.DataFrame(rows)


def offer_quality(scores: pd.DataFrame, y: np.ndarray, offered: np.ndarray,
                  t_star: float) -> pd.DataFrame:
    """Where inside the offered set the value comes from, two cuts.

    First-versus-repeat contact is a property of the policy: a member may
    clear the threshold in more than one month.  The score quartiles are a
    property of the model: selecting the top of a noisy score means the
    highest scores are the most over-stated, so the gap between what the
    model claims and what it delivers is widest at the top.
    """
    f = scores.loc[offered].copy()
    f["y"] = y[offered]
    f = f.sort_values(["member_id", "month"])
    f["contact_no"] = f.groupby("member_id").cumcount() + 1

    rows = []

    def add(cut, label, g):
        n, k = len(g), int(g["y"].sum())
        prec = k / n if n else np.nan
        rows.append({
            "cut": cut, "group": label, "offers": n, "offers_to_churners": k,
            "precision": round(prec, 4),
            "mean_predicted": round(float(g["p_used"].mean()), 4),
            "predicted_minus_observed": round(float(g["p_used"].mean()) - prec, 4),
            "value_usd": round(84.0 * n * (prec - t_star), 2),
            "value_per_offer_usd": round(84.0 * (prec - t_star), 2),
        })

    add("contact", "first contact", f[f["contact_no"] == 1])
    add("contact", "repeat contact", f[f["contact_no"] > 1])
    f["quartile"] = pd.qcut(f["p_used"], 4, labels=[1, 2, 3, 4])
    for q, g in f.groupby("quartile", observed=True):
        add("score quartile", f"Q{q} ({'lowest' if q == 1 else 'highest' if q == 4 else 'mid'})", g)
    add("all", "all offers", f)
    return pd.DataFrame(rows)


LINE = "#20486b"      # the one series
MARK_T = "#c2570c"    # the derived threshold
MARK_A = "#4a7c2f"    # the analyst's threshold
INK = "#1a1a1a"       # label text: ink, never the series colour
MUTED = "#6b6b6b"


def value_curve_figure(curve: pd.DataFrame, t_star: float) -> None:
    """Realised value against the decision threshold, in two panels.

    One panel cannot carry this: offering to (almost) everyone loses tens of
    thousands, so on a single axis the region that decides the programme is a
    flat line on the zero gridline.  Left panel is the full range, right panel
    the decision region at its own scale.  Same series, same units, two views.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    def at(t):
        return float(curve.loc[(curve["threshold"] - t).abs().idxmin(), "value_usd"])

    v_star, v_analyst = at(t_star), at(ANALYST_THRESHOLD)
    peak = curve.loc[curve["value_usd"].idxmax()]

    fig, (ax_full, ax_zoom) = plt.subplots(1, 2, figsize=(10.5, 4.3))

    for ax in (ax_full, ax_zoom):
        ax.axhline(0, lw=0.9, color=MUTED, zorder=1)
        ax.plot(curve["threshold"], curve["value_usd"], "-", lw=2,
                color=LINE, zorder=3)
        ax.axvline(t_star, ls="--", lw=1.4, color=MARK_T, zorder=2)
        ax.spines[["top", "right"]].set_visible(False)
        ax.spines[["left", "bottom"]].set_color(MUTED)
        ax.tick_params(colors=MUTED, labelsize=9)
        ax.set_xlabel("threshold on predicted churn probability",
                      fontsize=9, color=INK)

    # ---- left: the whole range, so the cost of blanket offers is visible ----
    ax_full.set_ylabel("realised value, Oct-Dec 2025 (USD)", fontsize=9, color=INK)
    ax_full.set_title("Full range", fontsize=10, color=INK, loc="left")
    ax_full.annotate(f"offer to everyone\n-${abs(curve['value_usd'].iloc[0]):,.0f}",
                     (curve["threshold"].iloc[0], curve["value_usd"].iloc[0]),
                     textcoords="offset points", xytext=(14, 6),
                     fontsize=8.5, color=INK)
    ax_full.annotate(f"t* = {t_star:.3f}", (t_star, 0),
                     textcoords="offset points", xytext=(8, -34),
                     fontsize=8.5, color=INK)
    ax_full.add_patch(plt.Rectangle((0.15, -3000), 0.30, 5000, fill=False,
                                    ec=MUTED, lw=0.8, ls=":", zorder=4))
    ax_full.annotate("detail, right", (0.45, 2000), textcoords="offset points",
                     xytext=(-6, 10), fontsize=8, color=MUTED, ha="right")

    # ---- right: the decision region at a scale that can be read ------------
    ax_zoom.axvline(ANALYST_THRESHOLD, ls=":", lw=1.4, color=MARK_A, zorder=2)
    ax_zoom.set_xlim(0.15, 0.45)
    ax_zoom.set_ylim(-3000, 2000)
    ax_zoom.set_title("Decision region (detail)", fontsize=10, color=INK, loc="left")
    ax_zoom.plot([t_star], [v_star], "o", ms=8, color=MARK_T,
                 mec="white", mew=1.6, zorder=5)
    ax_zoom.annotate(f"derived t* = {t_star:.3f}\n${v_star:,.0f}", (t_star, v_star),
                     textcoords="offset points", xytext=(10, -40),
                     fontsize=8.5, color=INK)
    ax_zoom.plot([ANALYST_THRESHOLD], [v_analyst], "o", ms=8, color=MARK_A,
                 mec="white", mew=1.6, zorder=5)
    ax_zoom.annotate(f"analyst's {ANALYST_THRESHOLD}\n${v_analyst:,.0f}",
                     (ANALYST_THRESHOLD, v_analyst), textcoords="offset points",
                     xytext=(12, 18), fontsize=8.5, color=INK)
    ax_zoom.text(0.16, -2550,
                 f"curve peaks at ${peak.value_usd:,.0f} (threshold {peak.threshold:.3f});\n"
                 f"not selected -- t* was fixed before scoring",
                 fontsize=8, color=MUTED, ha="left", va="bottom")

    fig.suptitle("Exhibit A3: realised programme value across decision thresholds",
                 fontsize=11.5, color=INK, x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(OUT / "a3_value_curve.png", dpi=150)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    # ---- 1. the threshold ----------------------------------------------------
    t_star, lines = derive_threshold()
    (OUT / "a3_threshold.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print()

    # ---- 2. calibration, on the validation month -----------------------------
    df, _ = load_clean()
    build = df[df["month"] <= TRAIN_END].reset_index(drop=True)
    model = fit_once(build, ADMISSIBLE)          # the row-3 model, same code path
    table, platt, cal_lines = calibration_check(model)
    table.to_csv(OUT / "a3_calibration.csv", index=False)
    print("\n".join(cal_lines))
    print()
    print(table.to_string(index=False))
    print()
    print(f"calibration setting in use: {CALIBRATION}")
    print()

    # ---- 3. the money, on the test window that A2 already scored -------------
    scores = pd.read_csv(OUT / "a2_test_scores.csv")
    y = scores[TARGET].to_numpy()
    p = apply_calibration(scores["p_churn"].to_numpy(), platt)
    scores["p_used"] = p

    policies = {
        f"targeted at t* = {t_star:.4f}": p > t_star,
        "offer to every member-month": np.ones(len(scores), dtype=bool),
        "no programme": np.zeros(len(scores), dtype=bool),
        f"targeted at the analyst's {ANALYST_THRESHOLD}": p > ANALYST_THRESHOLD,
    }

    rows = []
    for name, offered in policies.items():
        for seg in ("all", "corporate", "other"):
            m = (np.ones(len(scores), dtype=bool) if seg == "all"
                 else scores["segment"].eq(seg).to_numpy())
            o = offered & m
            rows.append({
                "policy": name,
                "segment": seg,
                "rows_scored": int(m.sum()),
                "churners": int(y[m].sum()),
                "offers": int(o.sum()),
                "offers_to_churners": int((o & (y == 1)).sum()),
                "offers_wasted": int((o & (y == 0)).sum()),
                "value_usd": round(value_of(y[m], o[m]), 2),
                # Standard error of that total, and how many SEs it sits from
                # zero.  Reported per segment because the segment case has to
                # stand or fall on its own evidence: corporate is only nine
                # offers, so its dollar figure cannot carry a recommendation
                # by itself.
                "value_se_usd": round(value_with_se(y[m], o[m])[1], 2) if o[m].sum() else 0.0,
                "ses_from_zero": (round(value_of(y[m], o[m]) / value_with_se(y[m], o[m])[1], 2)
                                  if o[m].sum() > 1 and value_with_se(y[m], o[m])[1] else None),
            })
    value = pd.DataFrame(rows)
    value.to_csv(OUT / "a3_value.csv", index=False)

    offered = p > t_star
    by_month = value_by_month(scores, y, offered, t_star)
    by_month.to_csv(OUT / "a3_by_month.csv", index=False)
    quality = offer_quality(scores, y, offered, t_star)
    quality.to_csv(OUT / "a3_offer_quality.csv", index=False)
    total, se = value_with_se(y, offered)

    # Sensitivity: the same policy, but a member is contacted at most once
    # across the quarter (the first month they clear the threshold).
    flagged = scores.loc[p > t_star].copy()
    first_only = flagged.sort_values(["member_id", "month"]).groupby("member_id").head(1)
    repeat_offers = len(flagged) - len(first_only)
    v_first = value_of(first_only[TARGET].to_numpy(),
                       np.ones(len(first_only), dtype=bool))

    # Sensitivity: the same policy on uncorrected probabilities, so the reader
    # can see how much the calibration step is carrying.
    raw = scores["p_churn"].to_numpy()
    v_raw = value_of(y, raw > t_star)

    # ---- the value curve: the same scores read at many cut points ------------
    grid = np.unique(np.concatenate([[0.0], CURVE_GRID, [t_star, ANALYST_THRESHOLD]]))
    curve = pd.DataFrame({
        "threshold": grid,
        "offers": [int((p > c).sum()) for c in grid],
        "value_usd": [round(value_of(y, p > c), 2) for c in grid],
    })
    curve.to_csv(OUT / "a3_value_curve.csv", index=False)

    value_curve_figure(curve, t_star)

    print("A3 value exhibit (test quarter, Oct-Dec 2025)")
    print(value.to_string(index=False))
    print()
    print(f"realised value at t* over the quarter: ${total:,.0f} "
          f"with a standard error of ${se:,.0f} "
          f"({total / se:.1f} standard errors from zero); each offer returns "
          f"+${MEMBER_LTV * OFFER_CONVERSION - OFFER_COST:,.0f} or "
          f"-${OFFER_COST:,.0f}, so the total is a sum of {int(offered.sum())} such draws")
    print()
    print("the same threshold, month by month")
    print(by_month.to_string(index=False))
    print()
    print("where the value comes from inside the offered set")
    print(quality.to_string(index=False))
    print()
    print(f"calibration sensitivity: on uncorrected probabilities the same policy "
          f"offers to {int((raw > t_star).sum())} rows and is worth ${v_raw:,.0f}, "
          f"against {int((p > t_star).sum())} offers worth "
          f"${value_of(y, p > t_star):,.0f} on corrected ones")
    print()
    print(f"threshold sensitivity: the curve peaks at "
          f"${curve.value_usd.max():,.0f} (threshold "
          f"{curve.loc[curve.value_usd.idxmax(), 'threshold']:.3f}); the derived t* was "
          f"fixed before scoring and was not chosen from this curve")
    print()
    print(f"repeat-contact sensitivity: of {len(flagged)} offers at t*, "
          f"{repeat_offers} are repeat contacts of a member already offered "
          f"earlier in the quarter; contacting each member at most once gives "
          f"{len(first_only)} offers worth ${v_first:,.0f}")
    print()
    print(f"wrote {OUT / 'a3_threshold.txt'}, a3_calibration.csv, a3_value.csv, "
          f"a3_by_month.csv, a3_offer_quality.csv, a3_value_curve.csv, "
          f"a3_value_curve.png")


if __name__ == "__main__":
    main()
