---
description: Approve the AC (or TC) of a feature
argument-hint: <feature-folder> [--tc]
---

Approve: $ARGUMENTS

1. Target file: `qa/specs/<feature>/ac.md`, or `qa/testcases/<feature>/tc.md` with `--tc`.
2. Run the `comment-style` lint on it. Exit not 0 → stop and show the hits.
3. `--tc` only: the AC file must be `Approved`. Otherwise stop.
4. Set the header:
   - `Status: Approved`
   - `Approved by:` the user's name from `git config user.name`
   - `Approved on:` today (YYYY-MM-DD)
5. Add a `Review log` row: date, `Approved`, name, open question count.
6. Open questions are allowed. Report how many are still open.
7. Reply in one line, then the next step: `/gen-tc <feature>` after AC, `/start-run <feature>` after TC.

Do not change any other line of the file.
