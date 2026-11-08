---
description: Request changes to the AC (or TC) of a feature
argument-hint: <feature-folder> [--tc] "<what to change>"
---

Request changes: $ARGUMENTS

1. Target file: `qa/specs/<feature>/ac.md`, or `qa/testcases/<feature>/tc.md` with `--tc`.
2. Set the header `Status: Changes requested`. Rejecting the AC also sets an `Approved` `tc.md` of the feature to `Draft`.
3. Add a `Review log` row: date, `Changes requested`, name from `git config user.name` (empty → ask), the note.
4. Apply the requested changes with the matching skill (`write-ac` or `gen-testcase`), including its lint, validator and reviewer steps.
5. When done, set `Status: Draft` and send the matching "ready for review" notification.
