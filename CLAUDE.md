# CLAUDE.md

IDS 575 Fall 2026, Assignment 1. Due Thursday October 1, 6:00 PM Central.

## Read these first

`README.md` and `rubric.md` in this folder are the authoritative brief and
grading criteria. `assignment1.pdf` contains both plus the data
dictionaries. Read them rather than relying on anything restated here.
Where this file and the brief disagree, the brief wins.

`course_docs/` holds the course-wide policy, approach, export and
submission documents. They apply to this assignment.

## Hard rules

- **Never read a data file into the conversation.** No `cat`, `head`,
  `print(df)`, or pasted CSV contents. Write code that reads the file and
  reports numbers back.
- **Never modify a supplied data file.** The duplicate rows in
  `division_h.csv` and `member_months.csv` are deliberate. Handle them in
  code. No in-place edits.
- **Never select on a test set.** Northline's test window and Cascade's
  `replicates.csv` are scored once and select nothing.
- **Never state a number you have not produced by running code.**
- **Never decide the evaluation design for me.** Splits, metrics, units of
  analysis, and what counts as held out are mine. Lay out the options and
  what each implies, then wait.
- **Stop if I cannot explain what you produced.** I may be asked to explain
  or modify any line of this submission.

## Requirements the submission must meet

- `analysis/` runs end to end from one command on a clean clone. No
  absolute paths. Seeds set.
- Grader has Python 3.10+, numpy, pandas, scikit-learn, matplotlib and
  nothing else. Anything further goes in `analysis/README.md`. No GPU.
- Outputs go to `analysis/outputs/`.
- Use the supplied helpers in the two `starter/load.py` files rather than
  reimplementing them.

## Working habits

- Baseline before model.
- When I reach a conclusion, argue against it: what would have to be true
  for it to be wrong, and what the strongest objection is.
- Say so when a result looks too good.
- One work block per session, one topic.

## End of every session

1. Export the transcript to `sessions/claude-code/`.
2. Remind me what to record in `ai_process_note.md`: what was delegated,
   what I changed or rejected and why, how numbers were checked.
3. Append to `NOTES.md`: what was done, the current open question, and any
   number produced with where it came from. Read `NOTES.md` at the start of
   each session.

Transcripts embed full file contents and command output. Keep this folder
free of anything private.