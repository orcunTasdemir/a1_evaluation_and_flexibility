# AI process note

Agent: Claude Code, seven sessions across two machines. Transcripts in `sessions/`.

**What I delegated.** The environment and the one-command pipeline; all six
analysis scripts; reading the handouts; drafting exhibits and prose. I kept the
evaluation design: admissible columns, what counts as held out, the order of the
A2 changes, the unit an offer is counted in, how the penalty is tuned, and both
recommendations.

## What I changed or rejected

**Evidence that was not reproducible.** The agent handed me the leakage
cross-tabs (`exit_survey_started` is 1 on 1,810 rows, every one a cancellation)
from a scratch command, not the pipeline. I made it put the check into
`a1_baselines.py` before it could enter a draft. Twice more after that: the
79.5% fold-overlap figure, and the monthly corporate share.

**A recommendation I reversed.** The agent advised skipping A3's monthly split
to save words and I agreed. It then proved to be the clearest evidence the value
is unstable: November $810, October $48, December −$6, so it went in.

**Where the tripwire points.** I specified it in dollars rather than AUC, after
seeing the model's top-scoring offers claim 39.6% and deliver 27.9%. A ranking
statistic can hold steady while calibration drifts and the cut-point stops
meaning what it meant. I also refused to score the test window with the
analyst's model for a like-for-like dollar comparison, since that is a second
scoring of a set meant to be touched once.

**A question that moved an argument.** The draft justified excluding corporate
on its dollar figure: 11% of corporate offers reached a churner against the
21.4% needed to break even. I asked whether the standard error differed by
segment, which the run did not report. Added, it showed corporate's −$78
carries a ±$84 standard error on nine offers, 0.93 from zero, so that claim
cannot bear weight on its own; and that excluding corporate moves reliability
only from 1.49 to 1.65 standard errors, since corporate was 9 of 242 offers.
Same recommendation. I kept the dollar observation but labelled it as nine
offers, and leaned the argument on the ranking failure (0.404 on 860 rows) and
on 533 training rows with no tenure past six months, which do bear weight.

**Errors.** The agent told me `test MSE − σ̂²` was conservative by σ̂²/10, which
ignores the noise in the replicate-mean yardstick; the two biases cancel
exactly. Its B3 figure annotated $834 where the exhibit said $852, because
the curve grid missed the derived threshold. Mine: I first thought §2 had to
name a specific model, when the rubric's named trap is "a standard that is
really a model."

## How I checked the numbers

I wrote expectations down first, base rate ~9% (came out 9.29%) and that Apparel's
problem would be variance (half wrong: the penalty converts it to 85% bias),
and recomputed by hand where I could, including the exit-survey AUC of 0.808 as
coverage plus half the ties, 0.616 + 0.5 × 0.384. Two checks the instructor
embedded in the brief both passed: σ̂/√10 ≈ 4 units (ours 3.85 and 3.77), and the
tuned penalties coinciding at one degree and not the other. The contractor's
four figures reproduce within half a standard error, so his arithmetic was never
the problem. The calibration decision was made on validation evidence **before**
any dollar figure existed; it cost $30, which is the point: deciding afterwards
would have selected the raw scores.

Run on both machines the pipeline gives byte-identical outputs but for
floating-point noise at 10⁻¹¹, and the *same 203 rows* clear the threshold. I
also cloned the repo to a fresh directory with no virtual environment, wiped the
outputs and ran it as a grader would: 31 files byte-identical, and
`analysis/check_memo_numbers.py` asserts 50 memo figures against that run.

**What I would not bet on:** that $852 transfers to April, and whether
Apparel's bias really falls as history accumulates, which is an expectation
rather than a measurement.
