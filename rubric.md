# Assignment 1 — grading rubric

100 points, scaled to 10% of the course grade.

Part A carries 55 points, Part B 35, and submission quality 10.

## Part A — Northline Fitness

| # | Criterion | Pts |
|---|---|---:|
| A1 | **Baselines.** Base rate, accuracy of the trivial rule with a correct statement of whether accuracy suits this decision, at least one single-variable AUC, and the analyst's headline beside them. The paragraph on what would have to be true for 0.967 to be credible. | **8** |
| A2 | **The evaluation.** All four changes made one at a time, AUC reported after each, the ordering justified, each row interpreted in a sentence, and each row labelled as cross-validated or test-window. Column decisions argued from availability at the moment of scoring, for columns kept as well as dropped. Correct statement of why the differences between rows are not an order-independent decomposition. Correct explanation of the two-month gap. | **27** |
| A3 | **The decision.** Test AUC overall and by segment with row and churner counts; the cost-based threshold derived rather than quoted; realised program value at that threshold against offering to everyone; a recommendation whose condition, if any, is stated so it can be checked. | **20** |

## Part B — Cascade Outdoor

| # | Criterion | Pts |
|---|---|---:|
| B1 | **The noise floor.** σ̂² for both divisions with its uncertainty, computed correctly as pooled within-configuration variance, and a correct statement of what the two floors imply about the "Apparel is inherently harder" claim. | **8** |
| B2 | **Comparison against the floor.** All eight cells tuned and reported under the prescribed protocol, with results stated as distance from σ̂². The penalty's effect quantified in all four cells and attributed to the ratio of terms to rows. The single-standard question answered against penalised fits, with the one-standard-error rule used. CV standard errors reported and used to say which Apparel differences are supported. | **19** |
| B3 | **Stability.** Bias and variance reported for all four models in both divisions, plus the figure. Three interpretive claims, each tied to a number in the student's own table rather than asserted from the lecture. | **8** |

## Submission

| # | Criterion | Pts |
|---|---|---:|
| S | **Reproducibility, communication and process.** Runs end to end from one command on a clean copy of the folder. Every number in the memo comes from that run. Both memo sections within length and addressed to their named reader, each leading with a recommendation. Session transcripts present for every session used. AI process note specific about what was delegated, what was changed or rejected, and how numbers were checked. | **10** |

A2 and B2 are 46 of the 100 points. That is deliberate: the assignment is about what an evaluation matched to deployment does to a headline number, and about what changes between a division with 3,000 rows and one with 197.

---

## Common ways marks are lost

- **Making several changes at once in A2.** A row that removes columns, regroups by member and re-splits by time attributes the change to nothing in particular.
- **Reading the A2 table as a decomposition.** The differences between rows depend on the order you made the changes in.
- **Dropping columns without a timing argument.** Both keeping and dropping a column need to be justified from when the column is measured.
- **Selecting anything on a test set.** Northline's test period and Cascade's replicate extract are each scored once.
- **A raw MSE with no floor beside it.** B2 asks for distance from σ̂².
- **Generalising one division to both.** The answer differs between Hardgoods and Apparel; that difference is the content of Part B.
- **Reporting an ordering without its uncertainty.** In Apparel some differences are inside the noise. Saying so scores better than declaring a winner the data cannot support.
- **Lecture vocabulary in place of your own numbers in B3.** "Ridge reduces variance" is a sentence from the handout; B3 asks for the number from your table.
- **A "standard" that is really a model.** The VP asked for something portable to a division acquired next year. Fixing a polynomial degree in advance has not answered her.
- **A generic AI process note.** "Used AI to help write code, verified output" earns nothing.
