# AI process note

Agent: Claude Code, eight sessions across two machines. Transcripts in `sessions/`.

**What I delegated.** The environment, the one-command pipeline, the six
analysis scripts, the handout reading and the drafting. I kept the evaluation
design: admissible columns, what counts as held out, the order of the A2
changes, the unit an offer is counted in, how the penalty is tuned, and both
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

**Where the tripwire points.** I specified it in dollars rather than AUC,
after seeing the model's top-scoring offers claim 39.6% and deliver 27.9%: a
ranking statistic holds steady through exactly the calibration drift that stops
the cut-point meaning what it meant. I also declined to score the test window
with the analyst's model for a directly comparable dollar figure, since that
would touch a set meant to be scored once.

**A question that moved an argument.** The draft justified excluding corporate
on its dollar figure: 11% of corporate offers reached a churner against the
21.4% needed to break even. I asked whether the standard error differed by
segment, which the run did not report. Added, it showed corporate's −$78
carries a ±$84 standard error on nine offers, 0.93 from zero, and that
excluding corporate moves reliability only from 1.49 to 1.65 standard errors,
since corporate was 9 of 242 offers. Same recommendation: I kept the dollar
observation, labelled as nine offers, and leaned the argument on the ranking
failure (0.404 on 860 rows) and on 533 training rows with no tenure past six
months.

**Two claims I made it withdraw.** It called the two noise floors "the same
amount in both"; they are 148.1 and 142.0, and the defensible claim is that the
data cannot separate them, and that even at the edge of a 95% interval they
differ by at most 34 units² against the 183 separating the contractor's two
best figures. And it wrote that the shrinkage Apparel's sample forces on it
creates Apparel's bias, when unpenalised degree 1, with no shrinkage at all,
carries the same bias of 294.

**A question that needed a measurement.** I asked why the penalty left
degree-1 *bias* unchanged, not just variance. Ridge shrinks the Hardgoods
degree-1 coefficient vector by 0.3%: nothing changed because nothing was
done. The grid's heaviest penalty would have shrunk it 77% at a
cross-validated cost of 286 units², so doing almost nothing was the search's
decision rather than a limit of the method. Added to the run as
`b2_shrinkage.csv` and to Exhibit B2.

**Errors.** The agent told me test MSE − σ̂² was conservative by σ̂²/10, which
ignores the noise in the replicate-mean yardstick; the two biases cancel
exactly. When I rewrote its draft in my own words it caught three places where
my wording had inverted the meaning, including writing that the scored data was
already *not* unseen, when out-of-fold means it was. Mine: I first thought §2
had to name a specific model, when the rubric's named trap is "a standard that
is really a model."

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
outputs and ran it as a grader would: every file came back byte-identical, and
`analysis/check_memo_numbers.py` asserts 103 memo figures against that run.

**What I would not bet on:** that $852 transfers to April, and whether
Apparel's bias really falls as history accumulates, which is an expectation
rather than a measurement.
