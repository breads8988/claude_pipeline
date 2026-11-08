---
description: Approve the AC (or TC) of a feature
argument-hint: <feature-folder> [--tc]
---

Approve: $ARGUMENTS

1. Target file: `qa/specs/<feature>/ac.md`, or `qa/testcases/<feature>/tc.md` with `--tc`.
2. The header must be `Status: Draft`. Otherwise stop and say why (`Changes requested` → apply the changes first; `Approved` → nothing to do).
3. Run the `comment-style` lint on it. Exit not 0 → stop and show the hits.
4. `--tc` only:
   - The AC file must be `Approved`. Otherwise stop.
   - Run `python3 .claude/skills/gen-testcase/scripts/coverage.py qa/specs/<feature>/ac.md qa/testcases/<feature>/tc.md`. Exit not 0 → stop and show the errors.
5. Set the header:
   - `Status: Approved`
   - `Approved by:` `git config user.name`; empty → ask the user for the name.
   - `Approved on:` today (YYYY-MM-DD)
6. Add a `Review log` row: date, `Approved`, name, open question count (`Open` + `Posted`).
7. Reply in one line, then the next step: `/gen-tc <feature>` after AC, `/start-run <feature> --build <build> --scope smoke` after TC.

Do not change any other line of the file.
