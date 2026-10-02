# AI process note

Agent: Claude Code, eight sessions across two machines. Transcripts in `sessions/`.

**Delegated.** The environment, the one-command pipeline, the six analysis
scripts, the handout reading, the drafting. **Kept:** admissible columns, what
counts as held out, the order of the A2 changes, the unit an offer is counted in,
how the penalty is tuned, both recommendations.

## What I changed or rejected

**Evidence that was not reproducible.** Three times it quoted figures from
scratch commands rather than the pipeline: the leakage cross-tabs
(`exit_survey_started` is 1 on 1,810 rows, every one a cancellation), the 79.5%
fold overlap, the monthly corporate share. Each went into a script before it was
allowed into a draft.

**A recommendation I reversed.** It advised skipping A3's monthly split to save
words and I agreed. The split proved to be the clearest evidence the value is
unstable, November $810 against October $48 and December −$6, so it went in.

**Where the tripwire points.** Dollars, not AUC, after seeing the top-scoring
offers claim 39.6% and deliver 27.9%: a ranking statistic holds steady through
exactly the calibration drift that stops the cut-point meaning what it meant. I
also declined to re-score the test window with the analyst's model, since that
set is scored once.

**Two questions that changed the memo.** Did the standard error differ by
segment? It was not in the run. Added, corporate's −$78 carries ±$84 on nine
offers, 0.93 from zero, and excluding corporate moves reliability only from 1.49
to 1.65 standard errors. The recommendation stands but the 11% precision is now
labelled as nine offers, with the argument leaning on the 0.404 ranking on 860
rows and 533 training rows with no tenure past six months. And why did the
penalty leave degree-1 *bias* unchanged, not just variance? Ridge shrinks those
coefficients by 0.3%: nothing changed because nothing was done, and the grid's
heaviest penalty would have shrunk them 77% at a cross-validated cost of 286
units², so doing almost nothing was the search's decision, not a limit of ridge.

**Two claims I made it withdraw.** It called the noise floors "the same amount
in both"; they are 148.1 and 142.0, and the defensible claim is that the data
cannot separate them, and that even at a 95% interval's edge they differ by at
most 34 units² against the 183 separating the contractor's best two. And it
wrote that shrinkage creates Apparel's bias, when unpenalised degree 1, with no
shrinkage at all, carries the same bias of 294.

**Writing the VP could not have followed.** Reading Part B line by line I marked
five numbers with nothing to interpret them against: "0.4 standard errors"
without saying the standard error was 14 on the difference; three bare decimals
with no units; two spreads never identified as standard deviations of the twenty
predictions; "parity in late 2027" without the platform migration behind it; and
one cell claimed as proof where it takes two, each holding one thing fixed. I had
it audit itself on that standard; it found AUC carries the whole of §1 and was
never defined, and that §2 quoted units² repeatedly without saying that is about
12 units a week per store against average demand of 112.

**Errors.** It told me test MSE − σ̂² was conservative by σ̂²/10, ignoring the
noise in the replicate-mean yardstick; the two biases cancel exactly. It also
reported for two sessions that both sections met their page limits when the
page-break filter it wrote emitted nothing, so the limits had never been tested;
§2 was over by a page, fixed by moving exhibit commentary under the exhibits,
which the brief excludes. When I rewrote its draft it caught three places where
my wording inverted the meaning. Mine: I first thought §2 had to name a model,
when the rubric's trap is "a standard that is really a model."

## How I checked the numbers

Expectations written first: base rate around 9% (9.29%), and Apparel's problem
would be variance, half wrong since the penalty converts it to 85% bias.
Recomputed by hand where possible, including the exit-survey AUC of 0.808 as
coverage plus half the ties, 0.616 + 0.5 × 0.384. Two checks the instructor
embedded both passed: σ̂/√10 ≈ 4 units (3.85, 3.77), and the tuned penalties
coinciding at one degree and not the other. The contractor's four figures
reproduce within half a standard error, so his arithmetic was never the problem.
The calibration decision was made on validation evidence **before** any dollar
figure existed; it cost $30, which is the point. Across both machines the outputs
are byte-identical but for floating-point noise at 10⁻¹¹, and the *same 203 rows*
clear the threshold. I also cloned the repository to an empty directory with no
virtual environment, wiped the outputs and ran it as a grader would;
`check_memo_numbers.py` asserts 107 memo figures against that run.

**Would not bet on:** that $852 transfers to April, and whether Apparel's bias
falls as history accumulates, which is an expectation, not a measurement.
